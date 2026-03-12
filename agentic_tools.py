"""
Agentic Tools Module — OpenAI Function Calling Definitions + Executor

This module defines:
1. TOOL_DEFINITIONS: JSON schemas for OpenAI's function calling API
2. ToolExecutor: Maps tool names to actual system method calls

The LLM sees the schemas and decides which tools to call.
Your code uses ToolExecutor to execute the calls and return results.
"""

import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional


# =============================================================================
# 1. TOOL DEFINITIONS — OpenAI Function Calling Schemas
# =============================================================================

TOOL_DEFINITIONS = [
    # -------------------------------------------------------------------------
    # SUBSTATION CONTROL
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "fail_substation",
            "description": "Simulate a failure at a substation, taking it offline. This causes cascading effects: connected traffic lights go to caution mode and EV charging stations lose power. Use this to test grid resilience.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "Name of the substation to fail (e.g. 'Times Square', 'Penn Station')"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restore_substation",
            "description": "Restore a failed substation back to operational status. This brings connected traffic lights and EV stations back online, and automatically disables any active V2G sessions for that substation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "Name of the substation to restore"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restore_all_substations",
            "description": "Restore ALL failed substations at once. Use when multiple substations are down and the user wants to reset the grid.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # V2G (Vehicle-to-Grid) CONTROL
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "enable_v2g",
            "description": "Enable Vehicle-to-Grid (V2G) energy trading for a FAILED substation. EVs near the substation will feed power back to the grid to partially restore service. The substation must be failed/offline for V2G to be activated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "Name of the failed substation to enable V2G for"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "disable_v2g",
            "description": "Disable V2G energy trading for a substation and release all participating vehicles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "Name of the substation to disable V2G for"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_v2g_status",
            "description": "Get the current V2G system status including active sessions, total capacity, energy delivered, and participating vehicles.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # SIMULATION CONTROL (SUMO)
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "start_simulation",
            "description": "Start the SUMO traffic simulation with vehicles on Manhattan streets. You can specify the number of vehicles and EV percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_count": {
                        "type": "integer",
                        "description": "Number of vehicles to spawn (default: 50, max: 500)",
                        "default": 50
                    },
                    "ev_percentage": {
                        "type": "integer",
                        "description": "Percentage of vehicles that are electric (0-100, default: 70)",
                        "default": 70
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_simulation",
            "description": "Stop the SUMO traffic simulation. All vehicles will be removed from the map.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_vehicles",
            "description": "Spawn additional vehicles into the running simulation. The simulation must be running first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of additional vehicles to spawn (default: 50)",
                        "default": 50
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_simulation_speed",
            "description": "Set the simulation speed multiplier. 1.0 = real-time, 2.0 = 2x speed, 0.5 = half speed. Range: 0.1 to 10.0.",
            "parameters": {
                "type": "object",
                "properties": {
                    "speed": {
                        "type": "number",
                        "description": "Speed multiplier (0.1 to 10.0)"
                    }
                },
                "required": ["speed"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # SCENARIO CONTROL (Time, Temperature, Scenarios)
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "set_time",
            "description": "Set the simulation time of day. This affects power load patterns (morning rush, evening peak, etc.), lighting, and grid stress levels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hour": {
                        "type": "number",
                        "description": "Hour of day (0-23, e.g. 8 for 8 AM, 20 for 8 PM)"
                    },
                    "minute": {
                        "type": "integer",
                        "description": "Minute (0-59, default: 0)",
                        "default": 0
                    }
                },
                "required": ["hour"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_temperature",
            "description": "Set the ambient temperature in Fahrenheit. Extreme temperatures (>90°F or <30°F) increase grid load due to AC/heating demand and can trigger substation overloads.",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {
                        "type": "number",
                        "description": "Temperature in degrees Fahrenheit (e.g. 72 for normal, 98 for heatwave, 15 for extreme cold)"
                    }
                },
                "required": ["temperature"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_scenario",
            "description": "Run a predefined test scenario that sets time, temperature, and vehicle count to simulate specific conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "enum": [
                            "rush_hour_stress_test",
                            "evening_peak_v2g",
                            "winter_emergency",
                            "summer_heatwave",
                            "late_night_low_load"
                        ],
                        "description": "Name of the scenario to run"
                    }
                },
                "required": ["scenario"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # EV CONFIGURATION
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "configure_ev",
            "description": "Configure EV (Electric Vehicle) parameters for the simulation: what percentage of vehicles are electric and their battery SOC (State of Charge) range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ev_percentage": {
                        "type": "integer",
                        "description": "Percentage of vehicles that are electric (0-100)",
                        "default": 70
                    },
                    "battery_min_soc": {
                        "type": "integer",
                        "description": "Minimum battery state of charge percentage (1-100)",
                        "default": 20
                    },
                    "battery_max_soc": {
                        "type": "integer",
                        "description": "Maximum battery state of charge percentage (1-100)",
                        "default": 90
                    }
                },
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # SYSTEM STATUS & QUERIES
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "get_system_status",
            "description": "Get comprehensive system status: substations (online/offline, load levels), SUMO simulation state, vehicle counts, and scenario info.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scenario_status",
            "description": "Get current scenario state including time of day, temperature, load levels per substation, and any active warnings or failures.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_substation_details",
            "description": "Get detailed information about a specific substation including load level, capacity, operational status, connected EV stations, and traffic lights.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "Name of the substation to get details for"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_load_forecast",
            "description": "Get a load forecast for the next N hours showing predicted power demand across all substations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to forecast (default: 6)",
                        "default": 6
                    }
                },
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # MAP CONTROL
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "focus_map",
            "description": "Focus the map view on a specific location, substation, or EV station. The map will fly to and highlight the location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name to focus on (e.g. 'Times Square', 'Penn Station', 'Central Park', 'Grand Central')"
                    }
                },
                "required": ["location"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # TEST SCENARIOS
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "run_ev_rush_test",
            "description": "Run an EV rush hour test: spawns many low-battery EVs to stress the charging infrastructure. Requires SUMO to be running.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_v2g_test",
            "description": "Run a complete V2G test scenario: fails a substation, enables V2G, and monitors the restoration process.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # MAP LAYER CONTROL
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "toggle_map_layer",
            "description": "Show or hide a map visualization layer. Useful for focusing the user's attention on specific infrastructure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "layer": {
                        "type": "string",
                        "enum": ["lights", "primary", "secondary", "vehicles", "ev", "substations"],
                        "description": "Layer to toggle: 'lights' (traffic lights), 'primary' (primary power cables), 'secondary' (secondary cables), 'vehicles' (cars/EVs), 'ev' (EV charging stations), 'substations' (power substations)"
                    },
                    "visible": {
                        "type": "boolean",
                        "description": "True to show the layer, false to hide it"
                    }
                },
                "required": ["layer", "visible"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # EV STATION CONTROL
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "fail_ev_station",
            "description": "Take an individual EV charging station offline. Vehicles currently charging will be released. Requires SUMO to be running.",
            "parameters": {
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "ID of the EV station to fail (e.g. 'ev_station_1')"
                    }
                },
                "required": ["station_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restore_ev_station",
            "description": "Bring a failed EV charging station back online. Its parent substation must be operational.",
            "parameters": {
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "ID of the EV station to restore (e.g. 'ev_station_1')"
                    }
                },
                "required": ["station_id"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # BLACKOUT SCENARIO
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "trigger_blackout",
            "description": "Trigger a city-wide blackout by failing ALL substations except one spare. This is a dramatic scenario for testing grid resilience and V2G emergency response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spare_substation": {
                        "type": "string",
                        "description": "Name of the one substation to keep online (default: 'Midtown East')",
                        "default": "Midtown East"
                    }
                },
                "required": []
            }
        }
    },

    # -------------------------------------------------------------------------
    # MAP VIEW (2D / 3D)
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "set_map_view",
            "description": "Switch the map between 2D (flat, top-down) and 3D (tilted, perspective) views or set a custom camera angle.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["2d", "3d"],
                        "description": "'2d' for flat top-down view, '3d' for tilted perspective view"
                    },
                    "pitch": {
                        "type": "number",
                        "description": "Optional custom camera pitch in degrees (0=flat, 60=tilted). Overrides mode if provided."
                    },
                    "bearing": {
                        "type": "number",
                        "description": "Optional camera rotation in degrees (0=north, 90=east). Overrides mode if provided."
                    }
                },
                "required": ["mode"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # MACRO / MULTI-STEP TOOLS
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "run_resilience_test",
            "description": "Run a comprehensive grid resilience test: fail a substation, enable V2G recovery, monitor recovery metrics, and restore. Returns a full resilience report. This is a multi-step operation that chains several actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "substation": {
                        "type": "string",
                        "description": "The substation to test resilience on (e.g. 'Times Square')"
                    }
                },
                "required": ["substation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_grid_vulnerability",
            "description": "Analyze the entire grid to identify the most vulnerable substations. Checks load ratios, identifies potential cascade failures, and recommends V2G pre-positioning for resilience. Returns a ranked vulnerability report.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_for_event",
            "description": "Prepare the grid and simulation for a specific event type (heatwave, morning_rush, evening_peak, storm, normal). Automatically sets time, temperature, spawns appropriate vehicles, and adjusts EV config. This demonstrates intelligent orchestration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event": {
                        "type": "string",
                        "enum": ["heatwave", "morning_rush", "evening_peak", "storm", "normal"],
                        "description": "The event type to prepare for"
                    }
                },
                "required": ["event"]
            }
        }
    },
    
    # -------------------------------------------------------------------------
    # REPORTING & MEDIA
    # -------------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "capture_system_snapshot",
            "description": "Capture a visual snapshot of the current system state (map view) and download it along with key metrics. Use this when the user wants to save what they see.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_situation_report",
            "description": "Generate a professional PDF situation report of the current grid status, including load, V2G operations, and traffic stats. Returns a link to the PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                     "notes": {
                        "type": "string",
                        "description": "Optional notes or observations to include in the report."
                     }
                },
                "required": []
            }
        }
    },
]


# =============================================================================
# 2. TOOL EXECUTOR — Maps tool names to actual system calls
# =============================================================================

class ToolExecutor:
    """
    Executes tool calls by mapping tool names to internal system methods.
    All calls are direct Python method invocations (same process, no HTTP).
    """

    def __init__(self, integrated_system, v2g_manager, sumo_manager,
                 power_grid, system_state, scenario_controller=None,
                 current_ev_config=None, vehicle_spawn_queue=None):
        self.integrated_system = integrated_system
        self.v2g_manager = v2g_manager
        self.sumo_manager = sumo_manager
        self.power_grid = power_grid
        self.system_state = system_state
        self.scenario_controller = scenario_controller
        self.current_ev_config = current_ev_config or {}
        self.vehicle_spawn_queue = vehicle_spawn_queue

        # Map tool names → handler methods
        self.handlers = {
            # Substation
            "fail_substation": self._fail_substation,
            "restore_substation": self._restore_substation,
            "restore_all_substations": self._restore_all_substations,

            # V2G
            "enable_v2g": self._enable_v2g,
            "disable_v2g": self._disable_v2g,
            "get_v2g_status": self._get_v2g_status,

            # Sim Control
            "start_simulation": self._start_simulation,
            "stop_simulation": self._stop_simulation,
            "spawn_vehicles": self._spawn_vehicles,
            "set_simulation_speed": self._set_simulation_speed,

            # Scenario / Env
            "set_time": self._set_time,
            "set_temperature": self._set_temperature,
            "run_scenario": self._run_scenario,
            "prepare_for_event": self._prepare_for_event,

            # Status
            "get_system_status": self._get_system_status,
            "get_scenario_status": self._get_scenario_status,
            "get_substation_details": self._get_substation_details,
            "get_load_forecast": self._get_load_forecast,
            "analyze_grid_vulnerability": self._analyze_grid_vulnerability,

            # Map
            "focus_map": self._focus_map,
            "set_map_view": self._set_map_view,
            "toggle_map_layer": self._toggle_map_layer,

            # EV Stations
            "fail_ev_station": self._fail_ev_station,
            "restore_ev_station": self._restore_ev_station,
            "configure_ev": self._configure_ev,

            # Blackout
            "trigger_blackout": self._trigger_blackout,

            # Reports & Media
            "capture_system_snapshot": self._capture_system_snapshot,
            "generate_situation_report": self._generate_situation_report,

            # Tests
            "run_ev_rush_test": self._run_ev_rush_test,
            "run_v2g_test": self._run_v2g_test,
            "run_resilience_test": self._run_resilience_test,
        }


    def _locate_component(self, query: str) -> dict:
        """Find a component and return its location + map action"""
        query_lower = query.lower()
        
        # 1. Search Substations
        for name, sub in self.integrated_system.substations.items():
            if query_lower in name.lower() or name.lower() in query_lower:
                return {
                    "success": True,
                    "found": True,
                    "type": "substation",
                    "name": name,
                    "description": f"{name} Substation is located at {sub['lat']:.4f}, {sub['lon']:.4f}. Status: {'Operational' if sub.get('operational', True) else 'Offline'}.",
                    "map_action": {
                        "type": "highlight_location",
                        "location": name,
                        "coords": [sub['lon'], sub['lat']],
                        "zoom": 14,
                        "pitch": 45
                    }
                }
                
        # 2. Search EV Stations
        for ev_id, station in self.integrated_system.ev_stations.items():
            if query_lower in ev_id.lower() or query_lower in station.get('name', '').lower():
                return {
                    "success": True,
                    "found": True,
                    "type": "ev_station",
                    "name": station.get('name', ev_id),
                    "description": f"EV Station {station.get('name', ev_id)} is located at {station['lat']:.4f}, {station['lon']:.4f}. Status: {'Operational' if station.get('operational', True) else 'Offline'}.",
                    "map_action": {
                        "type": "highlight_location",
                        "location": station.get('name', ev_id),
                        "coords": [station['lon'], station['lat']],
                        "zoom": 16,
                        "pitch": 60
                    }
                }

        # 3. Known Landmarks & Aliases
        landmarks = {
            "central park": {"lat": 40.785091, "lon": -73.968285, "desc": "Central Park, the green heart of Manhattan."},
            "empire state": {"lat": 40.7484, "lon": -73.9857, "desc": "The Empire State Building, a historic landmark."},
            "statue of liberty": {"lat": 40.6892, "lon": -74.0445, "desc": "The Statue of Liberty."},
            "bryant park": {"lat": 40.7536, "lon": -73.9832, "desc": "Bryant Park, a beloved public park in Midtown."},
            "times square": {"lat": 40.7580, "lon": -73.9855, "desc": "Times Square, the crossroads of the world."}
        }
        
        # Aliases for fuzzy matching
        aliases = {
            "bryant park station": "Times Square",
            "bryant part": "Bryant Park",  # Handle typo
            "grand central station": "Grand Central",
            "penn station": "Penn Station"
        }
        
        # Check aliases first (Substring matching)
        for alias, target in aliases.items():
            if alias in query_lower:
                # specific catch for "bryant part" -> "Bryant Park" landmark
                if target == "Bryant Park":
                    # Let it fall through to landmarks check below
                    query_lower = query_lower.replace(alias, target.lower())
                    continue
                    
                # Search for the target name directly in substations
                for name, sub in self.integrated_system.substations.items():
                    if target.lower() in name.lower():
                         return {
                            "success": True,
                            "found": True,
                            "type": "substation",
                            "name": name,
                            "description": f"Found '{alias}' (mapped to {name}). Located at {sub['lat']:.4f}, {sub['lon']:.4f}. Status: {'Operational' if sub.get('operational', True) else 'Offline'}.",
                            "map_action": {
                                "type": "highlight_location",
                                "location": name,
                                "coords": [sub['lon'], sub['lat']],
                                "zoom": 15,
                                "pitch": 45
                            }
                        }
        
        for name, data in landmarks.items():
            if name in query_lower:
                 return {
                    "success": True,
                    "found": True,
                    "type": "landmark",
                    "name": name.title(),
                    "description": data['desc'],
                    "map_action": {
                        "type": "highlight_location",
                        "location": name.title(),
                        "coords": [data['lon'], data['lat']],
                        "zoom": 15,
                        "pitch": 45
                    }
                }
        
        return {
            "success": False, 
            "found": False, 
            "error": f"Could not locate '{query}'. Try asking for a specific substation or EV station."
        }

    def _locate_component(self, query: str) -> dict:
        """Find a component and return its location + map action"""
        query_lower = query.lower()
        
        # 1. Search Substations
        for name, sub in self.integrated_system.substations.items():
            if query_lower in name.lower() or name.lower() in query_lower:
                return {
                    "success": True,
                    "found": True,
                    "type": "substation",
                    "name": name,
                    "description": f"{name} Substation is located at {sub['lat']:.4f}, {sub['lon']:.4f}. Status: {'Operational' if sub.get('operational', True) else 'Offline'}.",
                    "map_action": {
                        "type": "highlight_location",
                        "location": name,
                        "coords": [sub['lon'], sub['lat']],
                        "zoom": 14,
                        "pitch": 45
                    }
                }
                
        # 2. Search EV Stations
        for ev_id, station in self.integrated_system.ev_stations.items():
            if query_lower in ev_id.lower() or query_lower in station.get('name', '').lower():
                return {
                    "success": True,
                    "found": True,
                    "type": "ev_station",
                    "name": station.get('name', ev_id),
                    "description": f"EV Station {station.get('name', ev_id)} is located at {station['lat']:.4f}, {station['lon']:.4f}. Status: {'Operational' if station.get('operational', True) else 'Offline'}.",
                    "map_action": {
                        "type": "highlight_location",
                        "location": station.get('name', ev_id),
                        "coords": [station['lon'], station['lat']],
                        "zoom": 16,
                        "pitch": 60
                    }
                }

        # 3. Known Landmarks (Hardcoded for demo)
        landmarks = {
            "central park": {"lat": 40.785091, "lon": -73.968285, "desc": "Central Park, the green heart of Manhattan."},
            "empire state": {"lat": 40.7484, "lon": -73.9857, "desc": "The Empire State Building, a historic landmark."},
            "statue of liberty": {"lat": 40.6892, "lon": -74.0445, "desc": "The Statue of Liberty."}
        }
        
        for name, data in landmarks.items():
            if name in query_lower:
                 return {
                    "success": True,
                    "found": True,
                    "type": "landmark",
                    "name": name.title(),
                    "description": data['desc'],
                    "map_action": {
                        "type": "highlight_location",
                        "location": name.title(),
                        "coords": [data['lon'], data['lat']],
                        "zoom": 15,
                        "pitch": 45
                    }
                }
        
        return {
            "success": False, 
            "found": False, 
            "error": f"Could not locate '{query}'. Try asking for a specific substation or EV station."
        }

    def execute(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool by name. Returns a result dict."""
        handler = self.handlers.get(tool_name)
        if not handler:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        try:
            result = handler(**arguments)
            print(f"[TOOL EXECUTOR] {tool_name}({arguments}) → success={result.get('success', 'N/A')}")
            return result
        except Exception as e:
            print(f"[TOOL EXECUTOR] {tool_name}({arguments}) → ERROR: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    # =========================================================================
    # SUBSTATION CONTROL
    # =========================================================================

    def _fail_substation(self, substation: str) -> dict:
        """Take a substation offline — mirrors /api/fail/<substation>"""
        # Validate
        if substation not in self.integrated_system.substations:
            available = list(self.integrated_system.substations.keys())
            return {"success": False, "error": f"Substation '{substation}' not found. Available: {available}"}

        sub_data = self.integrated_system.substations[substation]
        if not sub_data.get('operational', True):
            return {"success": False, "error": f"{substation} is already offline"}

        # Execute failure
        impact = self.integrated_system.simulate_substation_failure(substation)
        self.power_grid.trigger_failure('substation', substation)

        # Update SUMO traffic lights if running
        if self.system_state.get('sumo_running') and self.sumo_manager.running:
            self.sumo_manager.update_traffic_lights()
            if hasattr(self.sumo_manager, 'handle_blackout_traffic_lights'):
                self.sumo_manager.handle_blackout_traffic_lights([substation])

            # Update affected EV stations
            for ev_id, ev_station in self.integrated_system.ev_stations.items():
                if ev_station['substation'] == substation:
                    ev_station['operational'] = False
                    if ev_id in getattr(self.sumo_manager, 'ev_stations_sumo', {}):
                        self.sumo_manager.ev_stations_sumo[ev_id]['available'] = 0
                    if hasattr(self.sumo_manager, 'station_manager') and self.sumo_manager.station_manager:
                        if ev_id in self.sumo_manager.station_manager.stations:
                            self.sumo_manager.station_manager.stations[ev_id]['operational'] = False
                            self.sumo_manager.station_manager.handle_blackout(substation)

        return {
            "success": True,
            "substation": substation,
            "action": "failed",
            "traffic_lights_affected": impact.get('traffic_lights_affected', 0),
            "ev_stations_affected": impact.get('ev_stations_affected', 0),
            "load_lost_mw": impact.get('load_lost_mw', 0),
            "map_action": {
                "type": "highlight_failure",
                "location": substation,
                "coords": sub_data.get('coords', sub_data.get('location', 
                          [sub_data['lon'], sub_data['lat']] if 'lat' in sub_data and 'lon' in sub_data else []))
            }
        }

    def _restore_substation(self, substation: str) -> dict:
        """Restore a substation — mirrors /api/restore/<substation>"""
        if substation not in self.integrated_system.substations:
            available = list(self.integrated_system.substations.keys())
            return {"success": False, "error": f"Substation '{substation}' not found. Available: {available}"}

        sub_data = self.integrated_system.substations[substation]
        if sub_data.get('operational', True):
            return {"success": False, "error": f"{substation} is already operational"}

        success = self.integrated_system.restore_substation(substation)
        if not success:
            return {"success": False, "error": f"Failed to restore {substation}"}

        self.power_grid.restore_component('substation', substation)
        self.v2g_manager.disable_v2g_for_substation(substation)

        lights_restored = 0
        ev_stations_restored = 0

        if self.system_state.get('sumo_running') and self.sumo_manager.running:
            self.sumo_manager.update_traffic_lights()
            for ev_id, ev_station in self.integrated_system.ev_stations.items():
                if ev_station['substation'] == substation:
                    ev_station['operational'] = True
                    ev_stations_restored += 1
                    if ev_id in getattr(self.sumo_manager, 'ev_stations_sumo', {}):
                        self.sumo_manager.ev_stations_sumo[ev_id]['available'] = ev_station['chargers']

        return {
            "success": True,
            "substation": substation,
            "action": "restored",
            "lights_restored": lights_restored,
            "ev_stations_restored": ev_stations_restored,
            "map_action": {
                "type": "highlight_restore",
                "location": substation,
                "coords": sub_data.get('coords', sub_data.get('location', 
                          [sub_data['lon'], sub_data['lat']] if 'lat' in sub_data and 'lon' in sub_data else []))
            }
        }

    def _restore_all_substations(self) -> dict:
        """Restore all failed substations"""
        restored = []
        already_online = []
        for name, sub_data in self.integrated_system.substations.items():
            if not sub_data.get('operational', True):
                result = self._restore_substation(name)
                if result.get('success'):
                    restored.append(name)
            else:
                already_online.append(name)

        if not restored:
            return {"success": True, "message": "All substations are already online", "restored": []}

        return {
            "success": True,
            "restored": restored,
            "count": len(restored),
            "already_online": already_online
        }

    # =========================================================================
    # V2G CONTROL
    # =========================================================================

    def _enable_v2g(self, substation: str) -> dict:
        """Enable V2G for a failed substation"""
        if substation not in self.integrated_system.substations:
            return {"success": False, "error": f"Substation '{substation}' not found"}

        sub_data = self.integrated_system.substations[substation]
        if sub_data.get('operational', True):
            return {"success": False, "error": f"{substation} is operational — V2G is only for failed substations"}

        success = self.v2g_manager.enable_v2g_for_substation(substation)
        if not success:
            return {"success": False, "error": f"Failed to enable V2G for {substation}"}

        power_needed = sub_data.get('load_mw', 0)
        rate = self.v2g_manager.get_current_rate(substation)
        energy_needed = self.v2g_manager.substation_energy_required.get(substation, 50)

        return {
            "success": True,
            "substation": substation,
            "action": "v2g_enabled",
            "power_needed_mw": power_needed,
            "energy_needed_kwh": energy_needed,
            "rate_per_kwh": rate,
            "vehicles_needed": max(2, int(energy_needed / 30) + 1),
            "map_action": {
                "type": "highlight_restore",
                "location": substation,
                "coords": [sub_data['lon'], sub_data['lat']],
                "zoom": 15,
                "pitch": 50
             }
        }

    def _disable_v2g(self, substation: str) -> dict:
        """Disable V2G for a substation"""
        if substation not in self.integrated_system.substations:
            return {"success": False, "error": f"Substation '{substation}' not found"}

        self.v2g_manager.disable_v2g_for_substation(substation)
        sub_data = self.integrated_system.substations[substation]
        return {
            "success": True, 
            "substation": substation, 
            "action": "v2g_disabled",
            "map_action": {
                "type": "highlight_location",
                "location": substation,
                "coords": [sub_data['lon'], sub_data['lat']],
                "zoom": 14,
                "pitch": 45
             }
        }

    def _get_v2g_status(self) -> dict:
        """Get V2G dashboard data"""
        try:
            v2g_data = self.v2g_manager.get_v2g_dashboard_data()
            status = self.v2g_manager.get_v2g_status()
            return {
                "success": True,
                "active_sessions": status.get('active_sessions', 0),
                "total_v2g_capacity_kw": status.get('total_v2g_capacity_kw', 0),
                "total_energy_delivered_kwh": status.get('total_energy_delivered_kwh', 0),
                "substations_with_v2g": status.get('substations_with_v2g', []),
                "dashboard": v2g_data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # SIMULATION CONTROL
    # =========================================================================

    def _start_simulation(self, vehicle_count: int = 50, ev_percentage: int = 70) -> dict:
        """Start SUMO traffic simulation"""
        if self.system_state.get('sumo_running'):
            return {"success": False, "error": "Simulation is already running"}

        try:
            vehicle_count = max(1, min(500, vehicle_count))
            ev_pct = max(0, min(100, ev_percentage)) / 100.0

            # Start SUMO process (the method is start_sumo, not start)
            success = self.sumo_manager.start_sumo(gui=False, seed=42)

            if success:
                self.system_state['sumo_running'] = True

                # Spawn vehicles (start_sumo only launches the process,
                # vehicles must be spawned separately)
                spawned = self.sumo_manager.spawn_vehicles(
                    count=vehicle_count,
                    ev_percentage=ev_pct
                )

                return {
                    "success": True,
                    "vehicle_count": vehicle_count,
                    "vehicles_spawned": spawned,
                    "ev_percentage": ev_percentage,
                    "message": f"Simulation started with {spawned} vehicles ({ev_percentage}% electric)"
                }
            else:
                return {"success": False, "error": "SUMO failed to start"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _stop_simulation(self) -> dict:
        """Stop SUMO simulation"""
        if not self.system_state.get('sumo_running'):
            return {"success": False, "error": "Simulation is not running"}

        try:
            self.sumo_manager.stop()
            self.system_state['sumo_running'] = False
            return {"success": True, "message": "Simulation stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _spawn_vehicles(self, count: int = 50) -> dict:
        """Spawn additional vehicles into running simulation"""
        if not self.system_state.get('sumo_running'):
            return {"success": False, "error": "Simulation is not running. Start it first."}

        count = max(1, min(500, count))

        # Get current EV config for spawn parameters
        ev_pct = self.current_ev_config.get('ev_percentage', 70) / 100.0
        batt_min = self.current_ev_config.get('battery_min_soc', 20) / 100.0
        batt_max = self.current_ev_config.get('battery_max_soc', 90) / 100.0

        # Use the spawn queue (async, non-blocking)
        # Each item must have ev_percentage, battery_min_soc, battery_max_soc
        # matching the format simulation_loop expects
        if self.vehicle_spawn_queue is not None:
            for _ in range(count):
                self.vehicle_spawn_queue.append({
                    'ev_percentage': ev_pct,
                    'battery_min_soc': batt_min,
                    'battery_max_soc': batt_max,
                })
            return {"success": True, "count": count, "message": f"Queued {count} vehicles for spawning"}
        else:
            # Direct spawn
            try:
                spawned = self.sumo_manager.spawn_vehicles(
                    count, ev_percentage=ev_pct,
                    battery_min_soc=batt_min, battery_max_soc=batt_max
                )
                return {"success": True, "count": count, "spawned": spawned, "message": f"Spawned {spawned} vehicles"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def _set_simulation_speed(self, speed: float) -> dict:
        """Set simulation speed multiplier"""
        speed = max(0.1, min(10.0, speed))
        self.system_state['simulation_speed'] = speed
        return {"success": True, "speed": speed, "message": f"Simulation speed set to {speed}x"}

    # =========================================================================
    # SCENARIO CONTROL
    # =========================================================================

    def _set_time(self, hour: float, minute: int = 0) -> dict:
        """Set simulation time of day"""
        if not self.scenario_controller:
            return {"success": False, "error": "Scenario controller not available"}

        try:
            hour = max(0, min(23.99, hour))
            minute = max(0, min(59, minute))
            result = self.scenario_controller.set_time(hour, minute, 0)
            return {
                "success": True,
                "hour": hour,
                "minute": minute,
                "time_description": result.get('description', f"{int(hour):02d}:{minute:02d}"),
                **{k: v for k, v in result.items() if k != 'description'}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _set_temperature(self, temperature: float) -> dict:
        """Set ambient temperature"""
        if not self.scenario_controller:
            return {"success": False, "error": "Scenario controller not available"}

        try:
            result = self.scenario_controller.set_temperature(temperature)
            warning = None
            if temperature > 90:
                warning = "High temperature! AC demand will increase grid load."
            elif temperature < 30:
                warning = "Low temperature! Heating demand will increase grid load."

            return {
                "success": True,
                "temperature": temperature,
                "warning": warning,
                **result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_scenario(self, scenario: str) -> dict:
        """Run a predefined test scenario — also starts SUMO if not running"""
        if not self.scenario_controller:
            return {"success": False, "error": "Scenario controller not available"}

        try:
            result = self.scenario_controller.run_scenario(scenario)

            # Auto-start SUMO simulation if not already running
            # so that vehicles actually appear on the map
            if not self.system_state.get('sumo_running'):
                # Vehicle counts matching ScenarioController.run_scenario()
                scenario_vehicles = {
                    'rush_hour_stress_test': (100, 70),
                    'evening_peak_v2g': (80, 70),
                    'winter_emergency': (60, 70),
                    'summer_heatwave': (90, 70),
                    'heatwave_crisis': (90, 70),
                    'catastrophic_heat': (100, 70),
                    'late_night_low_load': (20, 70),
                }
                vehicle_count, ev_pct = scenario_vehicles.get(scenario, (50, 70))
                sim_result = self._start_simulation(
                    vehicle_count=vehicle_count,
                    ev_percentage=ev_pct
                )
                result['simulation_started'] = sim_result.get('success', False)
                if sim_result.get('success'):
                    result['events'] = result.get('events', [])
                    result['events'].append(
                        f"SUMO simulation started with {vehicle_count} vehicles ({ev_pct}% EV)"
                    )

            return {"success": True, "scenario": scenario, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # EV CONFIGURATION
    # =========================================================================

    def _configure_ev(self, ev_percentage: int = 70,
                      battery_min_soc: int = 20,
                      battery_max_soc: int = 90) -> dict:
        """Configure EV parameters"""
        ev_percentage = max(0, min(100, ev_percentage))
        battery_min_soc = max(1, min(100, battery_min_soc))
        battery_max_soc = max(1, min(100, battery_max_soc))
        if battery_min_soc >= battery_max_soc:
            battery_min_soc = battery_max_soc - 1

        # Update global config
        self.current_ev_config.update({
            'ev_percentage': ev_percentage,
            'battery_min_soc': battery_min_soc,
            'battery_max_soc': battery_max_soc,
            'updated_at': datetime.now().isoformat()
        })

        # Update SUMO manager if running
        if self.sumo_manager and self.sumo_manager.running:
            self.sumo_manager.ev_percentage = ev_percentage / 100
            self.sumo_manager.battery_min_soc = battery_min_soc / 100
            self.sumo_manager.battery_max_soc = battery_max_soc / 100

        return {
            "success": True,
            "ev_percentage": ev_percentage,
            "battery_min_soc": battery_min_soc,
            "battery_max_soc": battery_max_soc,
        }

    # =========================================================================
    # STATUS & QUERIES
    # =========================================================================

    def _get_system_status(self) -> dict:
        """Get comprehensive system status"""
        try:
            substations = {}
            failed_list = []
            for name, sub in self.integrated_system.substations.items():
                operational = sub.get('operational', True)
                substations[name] = {
                    "operational": operational,
                    "load_mw": round(sub.get('load_mw', 0), 1),
                    "capacity_mva": sub.get('capacity_mva', 0),
                }
                if not operational:
                    failed_list.append(name)

            vehicle_stats = {}
            if self.system_state.get('sumo_running') and self.sumo_manager.running:
                vehicles = self.sumo_manager.get_vehicle_positions_for_visualization()
                vehicle_stats = {
                    "total": len(vehicles),
                    "evs": sum(1 for v in vehicles if v.get('is_ev')),
                    "charging": sum(1 for v in vehicles if v.get('is_charging')),
                }

            return {
                "success": True,
                "substations_online": len(self.integrated_system.substations) - len(failed_list),
                "substations_total": len(self.integrated_system.substations),
                "failed_substations": failed_list,
                "substations": substations,
                "sumo_running": self.system_state.get('sumo_running', False),
                "simulation_speed": self.system_state.get('simulation_speed', 1.0),
                "vehicles": vehicle_stats,
                "ev_stations": len(self.integrated_system.ev_stations),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_scenario_status(self) -> dict:
        """Get current scenario state"""
        if not self.scenario_controller:
            return {"success": False, "error": "Scenario controller not available"}
        try:
            status = self.scenario_controller.get_system_status()
            return {"success": True, **status}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_substation_details(self, substation: str) -> dict:
        """Get detailed info about a specific substation"""
        if substation not in self.integrated_system.substations:
            available = list(self.integrated_system.substations.keys())
            return {"success": False, "error": f"Substation '{substation}' not found. Available: {available}"}

        sub = self.integrated_system.substations[substation]

        # Find connected EV stations
        connected_ev = []
        for ev_id, ev_data in self.integrated_system.ev_stations.items():
            if ev_data.get('substation') == substation:
                connected_ev.append({
                    "id": ev_id,
                    "name": ev_data.get('name', ev_id),
                    "operational": ev_data.get('operational', True),
                    "chargers": ev_data.get('chargers', 0)
                })

        # Find connected traffic lights
        connected_lights = sum(
            1 for tl in self.integrated_system.traffic_lights.values()
            if tl.get('substation') == substation
        )

        return {
            "success": True,
            "name": substation,
            "operational": sub.get('operational', True),
            "load_mw": round(sub.get('load_mw', 0), 1),
            "capacity_mva": sub.get('capacity_mva', 0),
            "location": sub.get('coords', sub.get('location', [])),
            "connected_ev_stations": connected_ev,
            "connected_traffic_lights": connected_lights,
            "v2g_active": substation in self.v2g_manager.get_v2g_status().get('substations_with_v2g', [])
        }

    def _get_load_forecast(self, hours: int = 6) -> dict:
        """Get load forecast"""
        if not self.scenario_controller:
            return {"success": False, "error": "Scenario controller not available"}
        try:
            forecast = self.scenario_controller.get_load_forecast(hours)
            return {"success": True, "hours": hours, "forecast": forecast}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # MAP CONTROL
    # =========================================================================

    # Known locations for map focus
    LOCATIONS = {
        'times square': {'name': 'Times Square', 'coords': [-73.9857, 40.7580], 'zoom': 17},
        'penn station': {'name': 'Penn Station', 'coords': [-73.9937, 40.7505], 'zoom': 17},
        'grand central': {'name': 'Grand Central', 'coords': [-73.9772, 40.7527], 'zoom': 17},
        'columbus circle': {'name': 'Columbus Circle', 'coords': [-73.9819, 40.7681], 'zoom': 17},
        'union square': {'name': 'Union Square', 'coords': [-73.9903, 40.7359], 'zoom': 17},
        'washington square': {'name': 'Washington Square', 'coords': [-73.9973, 40.7308], 'zoom': 17},
        'brooklyn bridge': {'name': 'Brooklyn Bridge', 'coords': [-73.9969, 40.7061], 'zoom': 16},
        'wall street': {'name': 'Wall Street', 'coords': [-74.0090, 40.7068], 'zoom': 17},
        'central park': {'name': 'Central Park', 'coords': [-73.9654, 40.7829], 'zoom': 14},
        'manhattan': {'name': 'Manhattan', 'coords': [-73.9712, 40.7831], 'zoom': 12},
        'murray hill': {'name': 'Murray Hill', 'coords': [-73.9785, 40.7488], 'zoom': 17},
        'turtle bay': {'name': 'Turtle Bay', 'coords': [-73.9680, 40.7527], 'zoom': 17},
        'hells kitchen': {"name": "Hell's Kitchen", 'coords': [-73.9934, 40.7638], 'zoom': 17},
        "hell's kitchen": {"name": "Hell's Kitchen", 'coords': [-73.9934, 40.7638], 'zoom': 17},
        'midtown east': {'name': 'Midtown East', 'coords': [-73.9712, 40.7551], 'zoom': 17},
        'midtown': {'name': 'Midtown', 'coords': [-73.9845, 40.7549], 'zoom': 15},
        'upper east': {'name': 'Upper East Side', 'coords': [-73.9565, 40.7736], 'zoom': 15},
    }

    def _focus_map(self, location: str) -> dict:
        """Focus map on a location"""
        loc_key = location.lower().strip()
        loc_data = self.LOCATIONS.get(loc_key)

        # Also check substations
        if not loc_data:
            for name, sub in self.integrated_system.substations.items():
                if name.lower() == loc_key or loc_key in name.lower():
                    coords = sub.get('coords', sub.get('location', []))
                    loc_data = {'name': name, 'coords': coords, 'zoom': 17}
                    break

        if not loc_data:
            available = list(self.LOCATIONS.keys()) + list(self.integrated_system.substations.keys())
            return {"success": False, "error": f"Location '{location}' not found. Try: {', '.join(available[:10])}"}

        return {
            "success": True,
            "location": loc_data['name'],
            "map_action": {
                "type": "focus_and_highlight",
                "location": loc_data['name'],
                "name": loc_data['name'],
                "coordinates": loc_data['coords'],
                "zoom": loc_data.get('zoom', 17),
                "highlight": True,
                "showConnections": True
            }
        }

    # =========================================================================
    # MAP VIEW (2D / 3D)
    # =========================================================================

    def _set_map_view(self, mode: str = "3d", pitch: float = None, bearing: float = None) -> dict:
        """Switch between 2D and 3D map views"""
        presets = {
            '2d': {'pitch': 0, 'bearing': 0},
            '3d': {'pitch': 60, 'bearing': -17.6},
        }
        preset = presets.get(mode, presets['3d'])
        final_pitch = pitch if pitch is not None else preset['pitch']
        final_bearing = bearing if bearing is not None else preset['bearing']

        return {
            "success": True,
            "mode": mode,
            "pitch": final_pitch,
            "bearing": final_bearing,
            "message": f"Map switched to {mode.upper()} view (pitch={final_pitch}°, bearing={final_bearing}°)"
        }

    # =========================================================================
    # TEST SCENARIOS
    # =========================================================================

    def _run_ev_rush_test(self) -> dict:
        """Run EV rush hour test"""
        if not self.system_state.get('sumo_running'):
            return {"success": False, "error": "Simulation must be running first"}
        try:
            count = 30
            if self.vehicle_spawn_queue is not None:
                for _ in range(count):
                    self.vehicle_spawn_queue.append({
                        'ev_percentage': 1.0,         # 100% EVs for rush test
                        'battery_min_soc': 0.05,      # Very low battery
                        'battery_max_soc': 0.25,      # Still low
                    })
            return {"success": True, "message": f"EV rush test started — spawning {count} low-battery EVs"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_v2g_test(self) -> dict:
        """Run V2G test scenario"""
        # Pick a substation to fail
        target = None
        for name, sub in self.integrated_system.substations.items():
            if sub.get('operational', True):
                target = name
                break

        if not target:
            return {"success": False, "error": "No operational substations to test with"}

        # Fail it
        fail_result = self._fail_substation(target)
        if not fail_result.get('success'):
            return fail_result

        # Enable V2G
        v2g_result = self._enable_v2g(target)

        return {
            "success": True,
            "test_substation": target,
            "failure_result": fail_result,
            "v2g_result": v2g_result,
            "message": f"V2G test started: {target} failed and V2G enabled. Monitor V2G status for restoration progress."
        }

    # =========================================================================
    # MAP LAYER CONTROL
    # =========================================================================

    def _toggle_map_layer(self, layer: str, visible: bool) -> dict:
        """Toggle a map visualization layer on/off"""
        valid_layers = ['lights', 'primary', 'secondary', 'vehicles', 'ev', 'substations']
        if layer not in valid_layers:
            return {"success": False, "error": f"Unknown layer '{layer}'. Valid: {valid_layers}"}

        layer_labels = {
            'lights': 'Traffic Lights',
            'primary': 'Primary Power Cables',
            'secondary': 'Secondary Power Cables',
            'vehicles': 'Vehicles',
            'ev': 'EV Charging Stations',
            'substations': 'Power Substations'
        }

        return {
            "success": True,
            "layer": layer,
            "visible": visible,
            "label": layer_labels[layer],
            "message": f"{'Showing' if visible else 'Hiding'} {layer_labels[layer]} on map"
        }

    # =========================================================================
    # EV STATION CONTROL
    # =========================================================================

    def _fail_ev_station(self, station_id: str) -> dict:
        """Fail an individual EV charging station"""
        if station_id not in self.integrated_system.ev_stations:
            available = list(self.integrated_system.ev_stations.keys())
            return {"success": False, "error": f"Station '{station_id}' not found. Available: {available}"}

        ev_station = self.integrated_system.ev_stations[station_id]
        if not ev_station.get('operational', True):
            return {
                "success": False, 
                "error": f"{station_id} is already offline",
                "map_action": {
                    "type": "highlight_failure",
                    "location": station_id,
                    "coords": [ev_station['lon'], ev_station['lat']],
                    "zoom": 16,
                    "pitch": 60
                }
            }

        # Handle station failure in station manager
        released_vehicles = []
        if (hasattr(self.sumo_manager, 'station_manager') and
                self.sumo_manager.station_manager):
            released_vehicles = self.sumo_manager.station_manager.handle_station_failure(station_id)
            # Clear assignment on released vehicles
            if released_vehicles and hasattr(self.sumo_manager, 'vehicles'):
                for veh_id in released_vehicles:
                    if veh_id in self.sumo_manager.vehicles:
                        v = self.sumo_manager.vehicles[veh_id]
                        if hasattr(v, 'is_charging'):
                            v.is_charging = False
                        if hasattr(v, 'assigned_ev_station'):
                            v.assigned_ev_station = None

        # Update integrated system
        ev_station['operational'] = False

        # Update SUMO station status
        if station_id in getattr(self.sumo_manager, 'ev_stations_sumo', {}):
            self.sumo_manager.ev_stations_sumo[station_id]['available'] = 0

        return {
            "success": True,
            "station_id": station_id,
            "station_name": ev_station.get('name', station_id),
            "released_vehicles": len(released_vehicles),
            "message": f"{ev_station.get('name', station_id)} taken offline — {len(released_vehicles)} vehicles released",
            "map_action": {
                "type": "highlight_failure",
                "location": station_id,
                "coords": [ev_station['lon'], ev_station['lat']],
                "zoom": 16,
                "pitch": 60
            }
        }

    def _restore_ev_station(self, station_id: str) -> dict:
        """Restore a failed EV station"""
        if station_id not in self.integrated_system.ev_stations:
            available = list(self.integrated_system.ev_stations.keys())
            return {"success": False, "error": f"Station '{station_id}' not found. Available: {available}"}

        ev_station = self.integrated_system.ev_stations[station_id]
        if ev_station.get('operational', True):
            return {"success": False, "error": f"{station_id} is already operational"}

        # Check parent substation
        parent_sub = ev_station.get('substation')
        if parent_sub and parent_sub in self.integrated_system.substations:
            if not self.integrated_system.substations[parent_sub].get('operational', True):
                return {
                    "success": False,
                    "error": f"Cannot restore — parent substation '{parent_sub}' is offline. Restore it first."
                }

        ev_station['operational'] = True

        # Restore SUMO station capacity
        if station_id in getattr(self.sumo_manager, 'ev_stations_sumo', {}):
            self.sumo_manager.ev_stations_sumo[station_id]['available'] = ev_station.get('chargers', 4)

        if (hasattr(self.sumo_manager, 'station_manager') and
                self.sumo_manager.station_manager and
                station_id in self.sumo_manager.station_manager.stations):
            self.sumo_manager.station_manager.stations[station_id]['operational'] = True

        return {
            "success": True,
            "station_id": station_id,
            "station_name": ev_station.get('name', station_id),
            "message": f"{ev_station.get('name', station_id)} restored to service",
            "map_action": {
                "type": "highlight_restore",
                "location": station_id,
                "coords": [ev_station['lon'], ev_station['lat']],
                "zoom": 16,
                "pitch": 60
            }
        }

    # =========================================================================
    # BLACKOUT SCENARIO
    # =========================================================================

    def _trigger_blackout(self, spare_substation: str = "Midtown East") -> dict:
        """Trigger city-wide blackout — fail all substations except one spare"""
        failed = []
        skipped = []
        spare_found = False

        for name in list(self.integrated_system.substations.keys()):
            if name == spare_substation:
                spare_found = True
                skipped.append(name)
                continue
            sub_data = self.integrated_system.substations[name]
            if not sub_data.get('operational', True):
                skipped.append(name)
                continue
            result = self._fail_substation(name)
            if result.get('success'):
                failed.append(name)

        if not spare_found:
            # If the specified spare doesn't exist, warn but proceed
            pass

        return {
            "success": True,
            "failed_substations": failed,
            "spare_substation": spare_substation,
            "count_failed": len(failed),
            "already_offline": [s for s in skipped if s != spare_substation],
            "message": f"⚠️ BLACKOUT: {len(failed)} substations taken offline. Only {spare_substation} remains operational.",
            "map_action": {
                "type": "highlight_location",
                "location": "New York City",
                "coords": [-73.980, 40.758],  # Center of Manhattan
                "zoom": 12,
                "pitch": 0,
                "bearing": 0
            }
        }

    # =========================================================================
    # MACRO / MULTI-STEP TOOLS
    # =========================================================================

    def _prepare_for_event(self, event: str) -> dict:
        """Prepare the grid for a specific event — sets time, temperature,
        spawns vehicles, and adjusts EV config automatically."""

        event_profiles = {
            "heatwave": {"hour": 14, "minute": 0, "temp": 102, "vehicles": 90, "ev_pct": 70,
                         "description": "Peak afternoon heatwave — extreme AC demand"},
            "morning_rush": {"hour": 8, "minute": 0, "temp": 68, "vehicles": 100, "ev_pct": 70,
                             "description": "Morning rush hour — high traffic and EV commuting"},
            "evening_peak": {"hour": 18, "minute": 0, "temp": 75, "vehicles": 80, "ev_pct": 70,
                             "description": "Evening peak — commuters returning, V2G opportunity"},
            "storm": {"hour": 16, "minute": 0, "temp": 55, "vehicles": 30, "ev_pct": 70,
                      "description": "Severe storm — reduced traffic, grid stress"},
            "normal": {"hour": 12, "minute": 0, "temp": 72, "vehicles": 50, "ev_pct": 70,
                       "description": "Normal midday conditions"},
        }

        profile = event_profiles.get(event)
        if not profile:
            return {"success": False, "error": f"Unknown event type: {event}. Choose from: {list(event_profiles.keys())}"}

        actions = []

        time_result = self._set_time(profile["hour"], profile["minute"])
        actions.append({"action": "set_time", "success": time_result.get("success", False)})

        temp_result = self._set_temperature(profile["temp"])
        actions.append({"action": "set_temperature", "success": temp_result.get("success", False)})

        if not self.system_state.get('sumo_running'):
            sim_result = self._start_simulation(
                vehicle_count=profile["vehicles"],
                ev_percentage=profile["ev_pct"]
            )
            actions.append({"action": "start_simulation", "success": sim_result.get("success", False)})
        else:
            spawn_result = self._spawn_vehicles(count=profile["vehicles"])
            actions.append({"action": "spawn_vehicles", "success": spawn_result.get("success", False)})

        return {
            "success": True,
            "event": event,
            "description": profile["description"],
            "hour": profile["hour"],
            "minute": profile["minute"],
            "temperature": profile["temp"],
            "vehicles": profile["vehicles"],
            "actions": actions,
            "message": f"Grid prepared for {event}: {profile['description']}. "
                       f"Time set to {profile['hour']:02d}:{profile['minute']:02d}, "
                       f"temperature {profile['temp']}°F, {profile['vehicles']} vehicles."
        }

    def _run_resilience_test(self, substation: str) -> dict:
        """Multi-step resilience test: fail → enable V2G → measure → restore."""
        steps = []

        # Step 1: Record baseline
        status_before = self._get_system_status()
        baseline_load = sum(
            s.get('load_mw', 0)
            for s in self.integrated_system.substations.values()
            if s.get('operational', True)
        )
        steps.append({"step": "baseline", "total_load_mw": round(baseline_load, 1)})

        # Step 2: Fail the substation
        fail_result = self._fail_substation(substation)
        if not fail_result.get('success'):
            return {"success": False, "error": f"Could not fail {substation}: {fail_result.get('error', 'unknown')}", "steps": steps}
        steps.append({"step": "fail_substation", "substation": substation, "result": "offline"})

        # Step 3: Measure impact
        post_fail_load = sum(
            s.get('load_mw', 0)
            for s in self.integrated_system.substations.values()
            if s.get('operational', True)
        )
        load_lost = baseline_load - post_fail_load
        steps.append({"step": "measure_impact", "load_lost_mw": round(load_lost, 1), "remaining_load_mw": round(post_fail_load, 1)})

        # Step 4: Enable V2G on the failed substation
        v2g_result = self._enable_v2g(substation)
        v2g_recovery_kw = 0
        if v2g_result.get('success'):
            v2g_status = self._get_v2g_status()
            v2g_recovery_kw = v2g_status.get('total_v2g_capacity_kw', 0)
        steps.append({"step": "enable_v2g", "success": v2g_result.get('success', False), "recovery_kw": round(v2g_recovery_kw, 1)})

        # Step 5: Calculate resilience score
        recovery_pct = min(100, (v2g_recovery_kw / max(load_lost * 1000, 1)) * 100)
        resilience_grade = 'A' if recovery_pct > 75 else ('B' if recovery_pct > 50 else ('C' if recovery_pct > 25 else 'D'))
        steps.append({"step": "resilience_score", "recovery_pct": round(recovery_pct, 1), "grade": resilience_grade})

        # Step 6: Restore
        restore_result = self._restore_substation(substation)
        steps.append({"step": "restore", "success": restore_result.get('success', False)})

        return {
            "success": True,
            "substation": substation,
            "resilience_grade": resilience_grade,
            "recovery_percentage": round(recovery_pct, 1),
            "load_lost_mw": round(load_lost, 1),
            "v2g_recovery_kw": round(v2g_recovery_kw, 1),
            "steps": steps,
            "message": f"Resilience test complete for {substation}: Grade {resilience_grade} ({recovery_pct:.0f}% V2G recovery of {load_lost:.1f} MW lost)"
        }

    def _analyze_grid_vulnerability(self) -> dict:
        """Analyze all substations and rank by vulnerability."""
        vulnerabilities = []

        for name, sub in self.integrated_system.substations.items():
            if not sub.get('operational', True):
                vulnerabilities.append({
                    "substation": name,
                    "status": "OFFLINE",
                    "load_ratio": 0,
                    "risk": "CRITICAL",
                    "recommendation": "Restore immediately or enable V2G"
                })
                continue

            load = sub.get('load_mw', 0)
            capacity = sub.get('capacity_mva', 1)  # avoid div/0
            load_ratio = load / capacity

            if load_ratio > 0.85:
                risk = "HIGH"
                rec = "Pre-position V2G resources; consider load shedding"
            elif load_ratio > 0.65:
                risk = "MEDIUM"
                rec = "Monitor closely; V2G standby recommended"
            else:
                risk = "LOW"
                rec = "Operating within safe margins"

            vulnerabilities.append({
                "substation": name,
                "status": "ONLINE",
                "load_mw": round(load, 1),
                "capacity_mva": capacity,
                "load_ratio": round(load_ratio, 3),
                "risk": risk,
                "recommendation": rec
            })

        # Sort by load ratio descending
        vulnerabilities.sort(key=lambda x: x.get('load_ratio', 0), reverse=True)

        high_risk = [v for v in vulnerabilities if v['risk'] in ('HIGH', 'CRITICAL')]
        overall_risk = 'HIGH' if len(high_risk) >= 2 else ('MEDIUM' if high_risk else 'LOW')

        return {
            "success": True,
            "overall_risk": overall_risk,
            "substations": vulnerabilities,
            "high_risk_count": len(high_risk),
            "total_substations": len(vulnerabilities),
            "message": f"Grid vulnerability analysis: {overall_risk} overall risk. {len(high_risk)} substations at elevated risk."
        }



    # =========================================================================
    # REPORTS & MEDIA
    # =========================================================================

    def _capture_system_snapshot(self) -> dict:
        """Trigger frontend snapshot download and also save server-side state JSON."""
        try:
            from flask import current_app
            from main_complete_integration import socketio, _collect_comprehensive_state

            # Trigger the frontend PNG + JSON download
            socketio.emit('trigger_snapshot')

            # Also persist comprehensive state as a server-side JSON file
            import json, os, time as _time
            from datetime import datetime as _dt
            state = _collect_comprehensive_state()
            state['meta'] = {
                'snapshot_id': f"SNAP-{int(_time.time() * 1000)}",
                'timestamp': _dt.now().isoformat(),
                'generated_by': 'Manhattan Grid Control — Agentic Tool'
            }
            snap_dir = os.path.join(os.getcwd(), 'static', 'snapshots')
            os.makedirs(snap_dir, exist_ok=True)
            fname = f"snapshot_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
            fpath = os.path.join(snap_dir, fname)
            with open(fpath, 'w') as f:
                json.dump(state, f, indent=2, default=str)

            return {
                "success": True,
                "message": f"Snapshot triggered on dashboard and saved server-side at /static/snapshots/{fname}",
                "server_json": f"/static/snapshots/{fname}"
            }
        except ImportError:
            return {"success": False, "error": "SocketIO not available in this context."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_situation_report(self, notes: str = None) -> dict:
        """Generate comprehensive PDF report with AI analysis."""
        try:
            from main_complete_integration import _collect_comprehensive_state
            state = _collect_comprehensive_state()

            from report_generator import ReportGenerator
            generator = ReportGenerator()
            report_url = generator.generate_status_report(state, notes=notes)

            return {
                "success": True,
                "url": report_url,
                "message": f"Comprehensive report generated. Download here: {report_url}",
                "download_link": report_url
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
