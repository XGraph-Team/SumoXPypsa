"""
Agentic Chatbot — OpenAI Function Calling with Multi-Step Reasoning

This replaces the rule-based intent detection in ultra_intelligent_chatbot.py
with a true agentic loop:

1. Build dynamic system prompt with LIVE grid state
2. Send user message + tool definitions to OpenAI
3. If LLM returns tool_calls → execute them → feed results back → repeat
4. When LLM returns text → that's the final response
5. Emit Socket.IO events for frontend UI sync

The existing ultra_intelligent_chatbot.py is kept as fallback.
"""

import json
import os
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from agentic_tools import TOOL_DEFINITIONS, ToolExecutor


class AgenticChatbot:
    """
    Agentic chatbot using OpenAI function calling.
    The LLM decides which tools to call; your code executes them.
    """

    def __init__(self, tool_executor: ToolExecutor,
                 integrated_system, v2g_manager,
                 system_state: dict,
                 socketio=None,
                 scenario_controller=None):
        self.tool_executor = tool_executor
        self.integrated_system = integrated_system
        self.v2g_manager = v2g_manager
        self.system_state = system_state
        self.socketio = socketio
        self.scenario_controller = scenario_controller

        # OpenAI client — supports real OpenAI OR local OpenAI-compatible APIs
        # Priority: OPENAI_BASE_URL (local) > OPENAI_API_KEY (cloud)
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')  # e.g. http://localhost:8080/v1
        self.model = os.getenv('LLM_MODEL', '')

        if OpenAI and base_url:
            # Local OpenAI-compatible server (ramalama, ollama, vllm, etc.)
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key or "local"
            )
            if not self.model:
                self.model = self._detect_local_model(base_url)
            print(f"[AGENTIC CHATBOT] Using LOCAL LLM at {base_url}")
        elif OpenAI and api_key:
            # Real OpenAI API
            self.client = OpenAI(api_key=api_key)
            if not self.model:
                self.model = "gpt-4o"
            print(f"[AGENTIC CHATBOT] Using OpenAI API")
        else:
            self.client = None

        # Conversation history (per-session, not persistent yet)
        self.conversation_history: List[dict] = []
        self.max_history = 20  # Keep last N messages for context

        # Tool definitions for the API
        self.tools = TOOL_DEFINITIONS

        # Max iterations for the agentic loop (safety limit)
        self.max_iterations = 8

        print(f"[AGENTIC CHATBOT] Initialized with {len(self.tools)} tools, model={self.model}")
        if not self.client:
            print("[AGENTIC CHATBOT] WARNING: OpenAI client not available — will not function")

    # =========================================================================
    # DYNAMIC SYSTEM PROMPT
    # =========================================================================

    def _build_system_prompt(self) -> str:
        """Build system prompt with LIVE system state injected."""

        # --- Gather live data ---
        substations_info = []
        failed_list = []
        total_load = 0
        for name, sub in self.integrated_system.substations.items():
            operational = sub.get('operational', True)
            load = sub.get('load_mw', 0)
            capacity = sub.get('capacity_mva', 0)
            status = "🟢 Online" if operational else "🔴 OFFLINE"
            substations_info.append(f"  - {name}: {status} | Load: {load:.1f} MW / {capacity} MVA")
            if not operational:
                failed_list.append(name)
            total_load += load

        substations_text = "\n".join(substations_info)
        online_count = len(self.integrated_system.substations) - len(failed_list)
        total_count = len(self.integrated_system.substations)

        # EV stations
        ev_online = sum(1 for ev in self.integrated_system.ev_stations.values()
                        if ev.get('operational', True))
        ev_total = len(self.integrated_system.ev_stations)

        # V2G status
        try:
            v2g_status = self.v2g_manager.get_v2g_status()
            v2g_sessions = v2g_status.get('active_sessions', 0)
            v2g_capacity = v2g_status.get('total_v2g_capacity_kw', 0)
        except Exception:
            v2g_sessions = 0
            v2g_capacity = 0

        # Simulation state
        sumo_running = self.system_state.get('sumo_running', False)
        sim_speed = self.system_state.get('simulation_speed', 1.0)

        # Scenario state (time, temperature)
        time_str = "N/A"
        temp_str = "N/A"
        if self.scenario_controller:
            try:
                time_info = self.scenario_controller.get_current_time()
                time_str = time_info.get('formatted', 'N/A')
                temp_str = f"{self.scenario_controller.current_temperature:.0f}°F"
            except Exception:
                pass

        # Vehicle stats
        vehicle_text = "Simulation not running"
        if sumo_running:
            try:
                vehicles = self.integrated_system.get_network_state().get('vehicles', [])
                if not vehicles and hasattr(self.tool_executor.sumo_manager, 'get_vehicle_positions_for_visualization'):
                    vehicles = self.tool_executor.sumo_manager.get_vehicle_positions_for_visualization()
                total_v = len(vehicles) if vehicles else 0
                evs = sum(1 for v in vehicles if v.get('is_ev')) if vehicles else 0
                charging = sum(1 for v in vehicles if v.get('is_charging')) if vehicles else 0
                vehicle_text = f"{total_v} vehicles ({evs} EVs, {charging} charging)"
            except Exception:
                vehicle_text = "Running (stats unavailable)"

        # --- Build the prompt ---
        substation_names = ', '.join(self.integrated_system.substations.keys())
        ev_station_ids = ', '.join(self.integrated_system.ev_stations.keys())

        return f"""You are the Manhattan Power Grid AI Controller — an expert system managing NYC's electrical infrastructure.

═══════════════════════════════════════════════
📊 LIVE SYSTEM STATE (updated every request)
═══════════════════════════════════════════════
Substations: {online_count}/{total_count} online | Total Load: {total_load:.1f} MW
{substations_text}

EV Stations: {ev_online}/{ev_total} operational
V2G Sessions: {v2g_sessions} active | Capacity: {v2g_capacity:.0f} kW
Vehicles: {vehicle_text}
Simulation: {"🟢 Running" if sumo_running else "⚫ Stopped"} at {sim_speed}x speed
Time: {time_str} | Temperature: {temp_str}
{"⚠️ FAILED SUBSTATIONS: " + ", ".join(failed_list) if failed_list else "✅ All substations operational"}
═══════════════════════════════════════════════

VALID NAMES (use these exact strings in tool calls):
  Substations: {substation_names}
  EV Stations: {ev_station_ids}
  Map Layers: lights, primary, secondary, vehicles, ev, substations

CAPABILITIES:
You have full control over the Manhattan power grid through the tools provided.
You can control substations, manage V2G, run simulations, set time/temperature,
focus the map, toggle map layers, control individual EV stations, trigger blackouts,
and query system status.

RULES:
1. Use tools for ALL actions — never pretend to execute commands without tools
2. For multi-step requests, call tools in sequence and reason about results
3. Report results clearly — what changed, what was affected, current state
4. If a tool fails, explain why and suggest alternatives
5. For status queries, use get_system_status or get_scenario_status tools
6. Be concise but thorough — include numbers and specifics
7. When the user asks about the system, use tools to get fresh data rather than guessing
8. When showing infrastructure, use toggle_map_layer to highlight relevant layers
9. For DESTRUCTIVE actions (trigger_blackout, fail_substation), WARN the user first by describing what will happen and what substations will be affected, then proceed
10. For complex requests like "prepare for a heatwave" or "test resilience", use the macro tools (prepare_for_event, run_resilience_test, analyze_grid_vulnerability) — they chain multiple actions automatically
11. When the user's request is ambiguous (e.g. "fail the station" without specifying which), list the available options and ask for clarification before acting
"""

    # =========================================================================
    # MAIN CHAT METHOD — THE AGENTIC LOOP
    # =========================================================================

    async def chat(self, user_input: str, user_id: str = 'web_user') -> dict:
        """
        Main entry point. Sends user message to OpenAI with tools,
        executes any tool calls, feeds results back, repeats until done.
        """
        if not self.client:
            return {
                "success": False,
                "text": "OpenAI API key not configured. Please set OPENAI_API_KEY.",
                "fallback": True
            }

        try:
            # 1. Build messages with dynamic system prompt
            system_prompt = self._build_system_prompt()
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Add conversation history (last N messages)
            if self.conversation_history:
                messages.extend(self.conversation_history[-self.max_history:])

            # Add current user message
            messages.append({"role": "user", "content": user_input})

            # 2. Call OpenAI with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                temperature=0.3,
            )

            # 3. AGENTIC LOOP — keep going while LLM wants to call tools
            tool_results = []
            all_map_actions = []
            iteration = 0

            while (response.choices[0].finish_reason == "tool_calls" and
                   iteration < self.max_iterations):

                assistant_msg = response.choices[0].message
                # Add assistant's tool_call message to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_msg.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_msg.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    print(f"[AGENTIC] Iteration {iteration + 1}: Calling {tool_name}({tool_args})")

                    # Emit real-time progress to frontend (Feature 3: Streaming Progress)
                    if self.socketio:
                        self.socketio.emit('chatbot_tool_progress', {
                            'tool': tool_name,
                            'args': tool_args,
                            'iteration': iteration + 1,
                            'status': 'calling'
                        }, namespace='/')

                    # Execute the tool
                    result = self.tool_executor.execute(tool_name, tool_args)

                    # Track results
                    tool_results.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result,
                        "iteration": iteration + 1
                    })

                    # Extract map actions
                    if result.get("map_action"):
                        all_map_actions.append(result["map_action"])

                    # Emit Socket.IO events for frontend UI sync
                    if self.socketio:
                        self._emit_ui_updates(tool_name, tool_args, result)

                    # Add tool result to messages for next LLM call
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str)
                    })

                # Call OpenAI again with tool results
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    temperature=0.3,
                )
                iteration += 1

            # 4. Get final text response
            final_text = response.choices[0].message.content or "Action completed."

            # 5. Update conversation history (including tool calls for memory)
            self.conversation_history.append({"role": "user", "content": user_input})
            # Store tool call summaries so the LLM remembers what it did
            if tool_results:
                tool_summary = "; ".join(
                    f"{t['tool']}({t['args']}) → {'✓' if t['result'].get('success') else '✗'}"
                    for t in tool_results
                )
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"[Tools executed: {tool_summary}]\n\n{final_text}"
                })
            else:
                self.conversation_history.append({"role": "assistant", "content": final_text})

            # Trim history
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-self.max_history:]

            # 6. Build response
            response_data = {
                "success": True,
                "text": final_text,
                "tool_calls_made": [
                    {
                        "tool": t["tool"],
                        "args": t["args"],
                        "success": t["result"].get("success", False),
                        **({"url": t["result"]["url"]} if "url" in t["result"] else {}),
                        **({"download_link": t["result"]["download_link"]} if "download_link" in t["result"] else {}),
                        **({"server_json": t["result"]["server_json"]} if "server_json" in t["result"] else {}),
                    }
                    for t in tool_results
                ],
                "tools_called": len(tool_results),
                "iterations": iteration,
                "backend_executed": len(tool_results) > 0,
                "map_action": all_map_actions[0] if all_map_actions else None,
                "map_actions": all_map_actions,
                "timestamp": datetime.now().isoformat()
            }

            print(f"[AGENTIC] Complete: {len(tool_results)} tools called in {iteration} iterations")
            return response_data

        except Exception as e:
            print(f"[AGENTIC] Error: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "text": f"I encountered an error: {str(e)}",
                "fallback": True,
                "error": str(e)
            }

    # =========================================================================
    # SOCKET.IO — Frontend UI Sync
    # =========================================================================

    def _emit_ui_updates(self, tool_name: str, tool_args: dict, result: dict):
        """Emit Socket.IO events so the frontend UI updates in real-time."""
        if not self.socketio:
            return

        try:
            # --- GENERIC MAP ACTION HANDLER (Feature 3) ---
            # Any tool can return a 'map_action' to control the map view
            if result.get("map_action"):
                self.socketio.emit('ai_map_focus', result["map_action"], namespace='/')

            if tool_name == "set_time" and result.get("success"):
                self.socketio.emit('scenario_time_update', {
                    'hour': result.get('hour', tool_args.get('hour')),
                    'minute': result.get('minute', 0)
                }, namespace='/')

            elif tool_name == "set_temperature" and result.get("success"):
                self.socketio.emit('scenario_temp_update', {
                    'temperature': result.get('temperature', tool_args.get('temperature'))
                }, namespace='/')

            elif tool_name == "set_simulation_speed" and result.get("success"):
                self.socketio.emit('simulation_speed_update', {
                    'speed': result.get('speed', tool_args.get('speed'))
                }, namespace='/')

            elif tool_name in ("fail_substation", "restore_substation") and result.get("success"):
                self.socketio.emit('substation_update', {
                    'substation': result.get('substation'),
                    'action': result.get('action'),
                    'operational': tool_name == "restore_substation"
                }, namespace='/')

            elif tool_name == "restore_all_substations" and result.get("success"):
                self.socketio.emit('substation_update', {
                    'action': 'restore_all',
                    'restored': result.get('restored', [])
                }, namespace='/')

            elif tool_name in ("enable_v2g", "disable_v2g") and result.get("success"):
                self.socketio.emit('v2g_update', {
                    'substation': result.get('substation'),
                    'action': result.get('action'),
                }, namespace='/')

            elif tool_name in ("start_simulation", "stop_simulation") and result.get("success"):
                self.socketio.emit('simulation_state_update', {
                    'running': tool_name == "start_simulation",
                }, namespace='/')

            # Note: "focus_map" is now handled by the generic handler above
            # elif tool_name == "focus_map" and result.get("success"): ...

            elif tool_name == "run_scenario" and result.get("success"):
                self.socketio.emit('scenario_change', {
                    'scenario': tool_args.get('scenario'),
                    'result': {k: v for k, v in result.items()
                               if k in ('success', 'scenario', 'message')}
                }, namespace='/')

            elif tool_name == "generate_situation_report" and result.get("success"):
                report_url = result.get('url') or result.get('download_link')
                if report_url:
                    self.socketio.emit('trigger_report_download', {
                        'url': report_url
                    }, namespace='/')

            elif tool_name == "capture_system_snapshot" and result.get("success"):
                # Snapshot already emits trigger_snapshot in the tool itself,
                # but also emit server_json link if available
                server_json = result.get('server_json')
                if server_json:
                    self.socketio.emit('snapshot_saved', {
                        'url': server_json
                    }, namespace='/')

            elif tool_name == "configure_ev" and result.get("success"):
                # Push updated EV config to frontend so sliders update
                self.socketio.emit('ev_config_update', {
                    'ev_percentage': tool_args.get('ev_percentage', 70),
                    'battery_min_soc': tool_args.get('battery_min_soc', 20),
                    'battery_max_soc': tool_args.get('battery_max_soc', 90),
                }, namespace='/')

            elif tool_name == "spawn_vehicles" and result.get("success"):
                self.socketio.emit('vehicles_spawned', {
                    'count': tool_args.get('count', 0),
                    'message': result.get('message', '')
                }, namespace='/')

            elif tool_name == "toggle_map_layer" and result.get("success"):
                self.socketio.emit('layer_toggle', {
                    'layer': tool_args.get('layer'),
                    'visible': tool_args.get('visible'),
                }, namespace='/')

            elif tool_name == "set_map_view" and result.get("success"):
                self.socketio.emit('map_view_change', {
                    'mode': result.get('mode'),
                    'pitch': result.get('pitch'),
                    'bearing': result.get('bearing'),
                }, namespace='/')

            elif tool_name in ("fail_ev_station", "restore_ev_station") and result.get("success"):
                # Refresh network state so the frontend picks up the change
                self.socketio.emit('ev_station_update', {
                    'station_id': result.get('station_id'),
                    'action': 'failed' if tool_name == 'fail_ev_station' else 'restored',
                }, namespace='/')

            elif tool_name == "trigger_blackout" and result.get("success"):
                # Bulk substation failure — refresh the entire network
                self.socketio.emit('substation_update', {
                    'action': 'blackout',
                    'failed': result.get('failed_substations', []),
                    'spare': result.get('spare_substation'),
                }, namespace='/')

            # --- Macro tools ---
            elif tool_name == "prepare_for_event" and result.get("success"):
                # Push time and temp updates since this tool changes both
                self.socketio.emit('scenario_time_update', {
                    'hour': result.get('hour', 12),
                    'minute': result.get('minute', 0)
                }, namespace='/')
                self.socketio.emit('scenario_temp_update', {
                    'temperature': result.get('temperature', 72)
                }, namespace='/')

            elif tool_name == "run_resilience_test" and result.get("success"):
                # Notify frontend of test completion
                self.socketio.emit('resilience_test_complete', {
                    'substation': result.get('substation'),
                    'grade': result.get('resilience_grade'),
                    'recovery_pct': result.get('recovery_percentage'),
                }, namespace='/')

        except Exception as e:
            print(f"[AGENTIC] Socket.IO emit error: {e}")

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_tool_count(self) -> int:
        """Return number of available tools."""
        return len(self.tools)

    def is_available(self) -> bool:
        """Check if the agentic chatbot is operational."""
        return self.client is not None

    @staticmethod
    def _detect_local_model(base_url: str) -> str:
        """Auto-detect the model name from a local OpenAI-compatible server."""
        import requests
        try:
            # Strip /v1 suffix if present, then query /v1/models
            url = base_url.rstrip('/')
            if not url.endswith('/v1'):
                url += '/v1'
            resp = requests.get(f"{url}/models", timeout=3)
            if resp.ok:
                data = resp.json()
                models = data.get('data', [])
                if models:
                    model_id = models[0].get('id', 'default')
                    print(f"[AGENTIC CHATBOT] Auto-detected local model: {model_id}")
                    return model_id
        except Exception as e:
            print(f"[AGENTIC CHATBOT] Could not detect local model: {e}")
        return "default"
