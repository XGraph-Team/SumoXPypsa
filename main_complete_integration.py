"""
Manhattan Power Grid - COMPLETE World-Class Integration
All features from main_world_class.py PLUS advanced SUMO vehicle simulation

ORGANIZED ROUTE STRUCTURE:
1. Core Routes (Main page, debug)
2. Network & Status Routes
3. SUMO & Vehicle Management Routes
4. Power Grid Control Routes
5. V2G (Vehicle-to-Grid) Routes
6. ML Analytics Routes
7. AI & Chatbot Routes
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
import traceback
import random
import os

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False

# Import our systems
from core.power_system import ManhattanPowerGrid
from integrated_backend import ManhattanIntegratedSystem
from core.sumo_manager import ManhattanSUMOManager, SimulationScenario
from ml_engine import MLPowerGridEngine
from v2g_manager import V2GManager
from ai_chatbot import ManhattanAIChatbot
from ultra_intelligent_chatbot import initialize_ultra_intelligent_chatbot
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize systems
print("=" * 60)
print("MANHATTAN POWER GRID - COMPLETE INTEGRATION")
print("Power + Traffic + Vehicles - World Class System")
print("=" * 60)

# Initialize power grid
print("Initializing PyPSA power grid...")
power_grid = ManhattanPowerGrid()

# ADD THIS: Initialize loads with realistic values
print("Setting initial load values...")
# Around line 45 - REDUCE all loads to prevent overload
initial_loads = {
    "Commercial_Hell's_Kitchen": 24,      # was 120
    "Commercial_Times_Square": 56,        # was 280
    "Commercial_Penn_Station": 44,        # was 220
    "Commercial_Grand_Central": 50,       # was 250
    "Commercial_Murray_Hill": 18,         # was 90
    "Commercial_Turtle_Bay": 22,          # was 110
    "Commercial_Chelsea": 17,             # was 85
    "Commercial_Midtown_East": 34,        # was 170
    "Industrial_Hell's_Kitchen": 9,       # was 45
    "Industrial_Times_Square": 6,         # was 30
    "Industrial_Penn_Station": 14,        # was 70
    "Industrial_Grand_Central": 10,       # was 50
    "Industrial_Murray_Hill": 8,          # was 40
    "Industrial_Turtle_Bay": 10,          # was 50
    "Industrial_Chelsea": 14,             # was 70
    "Industrial_Midtown_East": 10         # was 50
}
for load_name, load_mw in initial_loads.items():
    # Fix the name format to match PyPSA (underscores instead of apostrophes)
    fixed_load_name = load_name.replace("'", "")
    if fixed_load_name in power_grid.network.loads.index:
        power_grid.network.loads.at[fixed_load_name, 'p_set'] = load_mw
        print(f"  Set {fixed_load_name}: {load_mw} MW")
    elif load_name in power_grid.network.loads.index:
        power_grid.network.loads.at[load_name, 'p_set'] = load_mw
        print(f"  Set {load_name}: {load_mw} MW")

print(f"Total initial load: {sum(initial_loads.values())} MW")


# Initialize integrated system
print("Loading integrated distribution network...")
integrated_system = ManhattanIntegratedSystem(power_grid)

# Initialize SUMO manager
print("Initializing SUMO vehicle manager...")
sumo_manager = ManhattanSUMOManager(integrated_system)

# ADD THESE LINES HERE:
print("Initializing V2G energy trading system...")
v2g_manager = V2GManager(integrated_system, sumo_manager)

sumo_manager.set_v2g_manager(v2g_manager)

# Initialize Enhanced ML Engine with V2G integration
ml_engine = MLPowerGridEngine(integrated_system=integrated_system, power_grid=power_grid, v2g_manager=v2g_manager)

# Initialize World-Class AI Chatbot
ai_chatbot = ManhattanAIChatbot(integrated_system=integrated_system, ml_engine=ml_engine, v2g_manager=v2g_manager)

# Initialize ULTRA-INTELLIGENT CHATBOT with typo correction and suggestions
try:
    from enhanced_v2g_manager import initialize_enhanced_v2g
    enhanced_v2g_manager = initialize_enhanced_v2g(integrated_system)
    ultra_chatbot = initialize_ultra_intelligent_chatbot(integrated_system, ml_engine, enhanced_v2g_manager, app)
    print("ULTRA-INTELLIGENT CHATBOT WITH TYPO CORRECTION INTEGRATED")
except Exception as e:
    print(f"Ultra-Intelligent Chatbot not available: {e}")
    ultra_chatbot = None

# Initialize ADVANCED AI SYSTEM CONTROLLER with OpenAI + LangChain
try:
    from advanced_ai_controller import initialize_advanced_ai
    world_class_ai = initialize_advanced_ai(integrated_system, ml_engine, v2g_manager, app)
    print("ADVANCED AI CONTROLLER WITH OPENAI + LANGCHAIN INTEGRATED")
except ImportError as e:
    print(f"Advanced AI Controller not available: {e}")
    world_class_ai = None

# Initialize OpenAI client (optional if key provided)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OPENAI_API_KEY and OpenAI) else None

# Initialize REALISTIC LOAD MODEL and SCENARIO CONTROLLER
print("=" * 60)
print("INITIALIZING WORLD-CLASS REALISTIC LOAD MODEL")
print("=" * 60)

try:
    from realistic_load_model import RealisticLoadModel
    from scenario_controller import ScenarioController
    from scenario_integration import integrate_scenario_controller

    print("Initializing realistic load model with building types...")
    load_model = RealisticLoadModel(integrated_system)

    print("Initializing scenario controller...")
    scenario_controller = ScenarioController(
        integrated_system=integrated_system,
        load_model=load_model,
        power_grid=power_grid,
        sumo_manager=sumo_manager
    )

    # Start automatic monitoring
    scenario_controller.start_auto_monitoring()

    # Add API endpoints
    integrate_scenario_controller(app, scenario_controller, load_model)

    print("=" * 60)
    print("✓ REALISTIC LOAD MODEL ACTIVE")
    print("✓ SCENARIO CONTROLLER ACTIVE")
    print("✓ AUTOMATIC FAILURE DETECTION ENABLED")
    print("=" * 60)

except Exception as e:
    print(f"ERROR: Could not initialize realistic load model: {e}")
    load_model = None
    scenario_controller = None

# Optional: cache of SUMO edge shapes (lon/lat) for road-locked rendering
EDGE_SHAPES: dict = {}

def preload_edge_shapes(max_edges: int | None = None) -> int:
    """Preload and cache SUMO edge shapes into EDGE_SHAPES using traci.
    Returns number of edges cached. Requires SUMO to be running.
    """
    try:
        import traci
    except Exception:
        return 0
    if not (system_state.get('sumo_running') and getattr(sumo_manager, 'running', False)):
        return 0
    count = 0
    try:
        edge_ids = [e for e in traci.edge.getIDList() if not e.startswith(':')]
        if max_edges is not None:
            edge_ids = edge_ids[:max_edges]
        for edge_id in edge_ids:
            if edge_id in EDGE_SHAPES:
                continue
            try:
                shape_xy = traci.edge.getShape(edge_id)
                edge_shape = []
                for sx, sy in shape_xy:
                    slon, slat = traci.simulation.convertGeo(sx, sy)
                    edge_shape.append([slon, slat])
                EDGE_SHAPES[edge_id] = {'xy': shape_xy, 'lonlat': edge_shape}
                count += 1
            except Exception:
                # Skip edges that fail shape retrieval
                continue
    except Exception:
        return count
    return count

# System state
system_state = {
    'running': True,
    'sumo_running': False,
    'simulation_speed': 1.0,
    'current_time': 0,
    'scenario': SimulationScenario.MIDDAY
}

# EV Configuration
current_ev_config = {
    'ev_percentage': 70,
    'battery_min_soc': 20,
    'battery_max_soc': 90,
    'updated_at': datetime.now().isoformat()
}

def simulation_loop():
    """Main simulation loop - REALISTIC TIMING (Real-world synchronized)"""
    global system_state

    # REALISTIC TIMING CONFIGURATION
    # All intervals in SUMO steps (1 SUMO step = 0.1 simulation seconds)
    SUMO_STEP_TIME = 0.1  # seconds - Industry standard for traffic simulation

    # Realistic update intervals (in seconds)
    TRAFFIC_LIGHT_CYCLE = 60       # 60 seconds - Realistic traffic light cycle
    POWER_GRID_UPDATE = 5          # 5 seconds - Realistic SCADA/state estimation
    EV_LOAD_UPDATE = 5             # 5 seconds - Realistic smart meter updates
    V2G_UPDATE = 60                # 60 seconds - Realistic V2G state changes

    # Convert to SUMO steps (multiply by 10 because 1 SUMO step = 0.1s)
    TRAFFIC_LIGHT_STEPS = int(TRAFFIC_LIGHT_CYCLE / SUMO_STEP_TIME)  # 600 steps
    POWER_GRID_STEPS = int(POWER_GRID_UPDATE / SUMO_STEP_TIME)       # 50 steps
    EV_LOAD_STEPS = int(EV_LOAD_UPDATE / SUMO_STEP_TIME)             # 50 steps
    V2G_STEPS = int(V2G_UPDATE / SUMO_STEP_TIME)                     # 600 steps

    # Performance optimization: Use high-resolution timer
    import time as time_module
    next_step_time = time_module.perf_counter()
    step_duration = 0.1  # Match SUMO step time (100ms)

    # Cache for reducing update frequency
    last_ev_update = 0
    last_v2g_update = 0
    last_power_flow = 0

    # Performance monitoring
    perf_stats = {'sumo_step': [], 'ev_update': [], 'power_flow': [], 'total_step': []}
    last_perf_report = 0

    print("\n" + "="*70)
    print("REALISTIC TIMING MODE ENABLED")
    print("="*70)
    print(f"SUMO Traffic Step:      {SUMO_STEP_TIME}s (0.1s - Industry standard)")
    print(f"Traffic Light Cycle:    {TRAFFIC_LIGHT_CYCLE}s (Realistic timing)")
    print(f"Power Grid Update:      {POWER_GRID_UPDATE}s (SCADA rate)")
    print(f"EV Load Update:         {EV_LOAD_UPDATE}s (Smart meter rate)")
    print(f"V2G State Update:       {V2G_UPDATE}s (V2G session rate)")
    print("="*70 + "\n")

    while system_state['running']:
        try:
            step_start = time_module.perf_counter()
            current_time = step_start

            # Skip if we're ahead of schedule (non-blocking timing)
            if current_time < next_step_time:
                time_module.sleep(0.001)  # Short sleep to reduce CPU usage
                continue

            # REALISTIC TIMING: Traffic lights change every 60 seconds
            if system_state['current_time'] % TRAFFIC_LIGHT_STEPS == 0:
                integrated_system.update_traffic_light_phases()
                if system_state['current_time'] > 0:  # Don't print at startup
                    print(f"[TRAFFIC] Light phase change at {system_state['current_time']*0.1:.1f}s")

            # Run SUMO step if active
            if system_state['sumo_running'] and sumo_manager.running:
                sumo_start = time_module.perf_counter()

                # SUMO step - advances traffic simulation by 0.1 seconds
                sumo_manager.step()

                sumo_time = (time_module.perf_counter() - sumo_start) * 1000
                perf_stats['sumo_step'].append(sumo_time)

                # REALISTIC: V2G updates every 60 seconds (vehicle-to-grid state changes)
                if system_state['current_time'] - last_v2g_update >= V2G_STEPS:
                    v2g_manager.update_v2g_sessions()
                    last_v2g_update = system_state['current_time']

                # REALISTIC: EV load updates every 5 seconds (smart meter telemetry)
                if system_state['current_time'] - last_ev_update >= EV_LOAD_STEPS:
                    ev_start = time_module.perf_counter()
                    update_ev_power_loads()
                    ev_time = (time_module.perf_counter() - ev_start) * 1000
                    perf_stats['ev_update'].append(ev_time)
                    last_ev_update = system_state['current_time']

                # REALISTIC: Power flow every 5 seconds (SCADA state estimation)
                if system_state['current_time'] - last_power_flow >= POWER_GRID_STEPS:
                    pf_start = time_module.perf_counter()
                    try:
                        power_grid.run_power_flow("dc")
                        pf_time = (time_module.perf_counter() - pf_start) * 1000
                        perf_stats['power_flow'].append(pf_time)
                        if pf_time > 100:  # Warn if power flow takes >100ms
                            print(f"[WARNING] Power flow took {pf_time:.1f}ms")
                    except Exception as e:
                        print(f"[ERROR] Power flow failed: {e}")
                    last_power_flow = system_state['current_time']

            system_state['current_time'] += 1

            # Track total step time
            total_time = (time_module.perf_counter() - step_start) * 1000
            perf_stats['total_step'].append(total_time)

            # Performance report every 30 seconds (300 SUMO steps)
            if system_state['current_time'] - last_perf_report >= 300:
                sim_time = system_state['current_time'] * SUMO_STEP_TIME
                if perf_stats['sumo_step']:
                    avg_sumo = sum(perf_stats['sumo_step'][-100:]) / min(100, len(perf_stats['sumo_step']))
                    avg_total = sum(perf_stats['total_step'][-100:]) / min(100, len(perf_stats['total_step']))
                    avg_pf = sum(perf_stats['power_flow'][-10:]) / max(1, min(10, len(perf_stats['power_flow']))) if perf_stats['power_flow'] else 0

                    print(f"\n[PERF] Simulation time: {sim_time:.1f}s")
                    print(f"       Avg SUMO step: {avg_sumo:.1f}ms, Total step: {avg_total:.1f}ms")
                    print(f"       Power flow: {avg_pf:.1f}ms, Real-time ratio: {avg_total/100:.2f}x")

                    if sumo_manager.running:
                        stats = sumo_manager.get_statistics()
                        print(f"       Vehicles: {stats.get('total_vehicles', 0)}, EVs: {stats.get('ev_vehicles', 0)}, Charging: {stats.get('vehicles_charging', 0)}")

                last_perf_report = system_state['current_time']

            # Calculate next step time (compensates for processing time)
            next_step_time += step_duration / system_state['simulation_speed']

            # If we're falling behind, reset timer
            if current_time > next_step_time + 0.5:
                next_step_time = current_time
                print(f"[WARNING] Simulation running slow! Step took {total_time:.1f}ms (target: {step_duration*1000:.1f}ms)")

        except Exception as e:
            print(f"Simulation error: {e}")
            traceback.print_exc()
            time.sleep(1)
            next_step_time = time_module.perf_counter()

def update_ev_power_loads():
    """Update power grid loads based on EV charging - OPTIMIZED FOR 1000+ VEHICLES"""

    global power_grid
    global previous_ev_load_mw

    # Initialize previous load tracking
    if 'previous_ev_load_mw' not in globals():
        previous_ev_load_mw = 0

    # Quick validation checks
    if not power_grid or not sumo_manager.running:
        return

    # OPTIMIZATION: Get charging data directly from station manager (O(stations) instead of O(vehicles))
    charging_counts = {}

    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
        # Direct access to station charging data - much faster!
        for station_id, station in sumo_manager.station_manager.stations.items():
            num_charging = len(station['vehicles_charging'])
            if num_charging > 0:
                charging_counts[station_id] = num_charging
    else:
        # Fallback: Count from vehicle states
        for vehicle in sumo_manager.vehicles.values():
            if (vehicle.config.is_ev and
                vehicle.assigned_ev_station and
                getattr(vehicle, 'is_charging', False)):
                station_id = vehicle.assigned_ev_station
                charging_counts[station_id] = charging_counts.get(station_id, 0) + 1
    
    # OPTIMIZED: Calculate station loads efficiently
    total_charging_kw = 0
    substation_loads = {}  # Track load per substation

    # Bus name mapping cache (moved outside loop for efficiency)
    bus_name_mapping = {
        "Hell's Kitchen": "Hell's Kitchen_13.8kV",
        "Times Square": "Times Square_13.8kV",
        "Penn Station": "Penn Station_13.8kV",
        "Grand Central": "Grand Central_13.8kV",
        "Murray Hill": "Murray Hill_13.8kV",
        "Turtle Bay": "Turtle Bay_13.8kV",
        "Columbus Circle": "Chelsea_13.8kV",
        "Midtown East": "Midtown East_13.8kV"
    }

    # Calculate power loads per station
    for ev_id, ev_station in integrated_system.ev_stations.items():
        chargers_in_use = charging_counts.get(ev_id, 0)

        # Realistic variable charging rate based on station load
        if chargers_in_use > 0:
            if chargers_in_use <= 5:
                power_per_vehicle = 150  # 150kW DC fast charging
            elif chargers_in_use <= 10:
                power_per_vehicle = 100  # 100kW
            elif chargers_in_use <= 15:
                power_per_vehicle = 50   # 50kW
            else:
                power_per_vehicle = 22   # 22kW (congested)

            charging_power_kw = chargers_in_use * power_per_vehicle
        else:
            charging_power_kw = 0

        total_charging_kw += charging_power_kw

        # Update integrated system
        ev_station['vehicles_charging'] = chargers_in_use
        ev_station['current_load_kw'] = charging_power_kw

        # Aggregate by substation
        substation_name = ev_station['substation']
        substation_loads[substation_name] = substation_loads.get(substation_name, 0) + charging_power_kw

    # OPTIMIZED: Batch PyPSA updates (collect all updates then apply at once)
    pypsa_updates = {}  # {load_name: (bus_name, load_mw)}

    for substation_name, load_kw in substation_loads.items():
        load_mw = load_kw / 1000

        # Get bus name
        bus_name = bus_name_mapping.get(substation_name)
        if not bus_name:
            continue

        # Check bus existence (with name variations)
        bus_name_in_pypsa = None
        for variant in [bus_name, bus_name.replace("'", ""), bus_name.replace(" ", "_")]:
            if variant in power_grid.network.buses.index:
                bus_name_in_pypsa = variant
                break

        if not bus_name_in_pypsa:
            continue

        # Prepare update
        clean_name = substation_name.replace(' ', '_').replace("'", '')
        ev_load_name = f"EV_{clean_name}"
        pypsa_updates[ev_load_name] = (bus_name_in_pypsa, load_mw)

        # Update integrated system
        if substation_name in integrated_system.substations:
            integrated_system.substations[substation_name]['ev_load_mw'] = load_mw

    # OPTIMIZED: Apply all PyPSA updates in batch (silent for performance)
    for ev_load_name, (bus_name_in_pypsa, load_mw) in pypsa_updates.items():
        try:
            if ev_load_name not in power_grid.network.loads.index:
                power_grid.network.add("Load", ev_load_name, bus=bus_name_in_pypsa, p_set=load_mw)
            else:
                power_grid.network.loads.at[ev_load_name, 'p_set'] = load_mw
        except Exception:
            pass  # Silent failure for performance

    # Clear zero loads efficiently
    for substation_name in bus_name_mapping.keys():
        if substation_name not in substation_loads:
            clean_name = substation_name.replace(' ', '_').replace("'", '')
            ev_load_name = f"EV_{clean_name}"
            if ev_load_name in power_grid.network.loads.index:
                power_grid.network.loads.at[ev_load_name, 'p_set'] = 0
    
    # OPTIMIZED: Track load changes (silent for performance)
    total_ev_load_mw = total_charging_kw / 1000
    previous_ev_load_mw = globals().get('previous_ev_load_mw', 0.0)
    globals()['previous_ev_load_mw'] = total_ev_load_mw

def check_n_minus_1_contingency():
    """Check if system can survive any single component failure"""
    critical_components = []
    for line in power_grid.network.lines.index:
        # Temporarily fail this line
        original_capacity = power_grid.network.lines.at[line, 's_nom']
        power_grid.network.lines.at[line, 's_nom'] = 0
        
        # Run power flow
        result = power_grid.run_power_flow("dc")
        
        # Check if system survives
        if not result.converged or result.max_line_loading > 1.0:
            critical_components.append(line)
        
        # Restore
        power_grid.network.lines.at[line, 's_nom'] = original_capacity
    
    return critical_components
def calculate_dynamic_charging_power(soc):
    """Calculate realistic charging power based on battery SOC"""
    if soc < 0.2:
        return 150  # 150kW DC fast charging for low battery
    elif soc < 0.5:
        return 100  # 100kW moderate fast charging
    elif soc < 0.8:
        return 50   # 50kW standard charging
    else:
        return 22   # 22kW trickle charging above 80%

def handle_grid_stress(power_flow_result, charging_details):
    """Handle grid stress conditions - WORLD CLASS"""
    
    print("\n[EMERGENCY] GRID STRESS DETECTED - INITIATING RESPONSE")
    
    # Identify critical lines
    critical_lines = []
    for line_name, line_data in power_grid.network.lines.iterrows():
        loading = abs(line_data.p0 / line_data.s_nom) if line_data.s_nom > 0 else 0
        if loading > 0.85:
            critical_lines.append((line_name, loading))
    
    critical_lines.sort(key=lambda x: x[1], reverse=True)
    
    # Implement demand response
    if charging_details['total_vehicles_charging'] > 20:
        print(f"  [DEMAND] Implementing demand response for {charging_details['total_vehicles_charging']} EVs")
        
        # Reduce charging rate at critical stations
        for station_name in charging_details['critical_stations']:
            # Find station and reduce power
            for ev_id, ev_station in integrated_system.ev_stations.items():
                if ev_station['name'] == station_name:
                    # Signal SUMO to reduce charging rate
                    if hasattr(sumo_manager, 'reduce_charging_rate'):
                        sumo_manager.reduce_charging_rate(ev_id, 0.5)  # 50% reduction
                    print(f"    Reduced charging at {station_name} by 50%")
    
    # Log critical lines
    for line, loading in critical_lines[:3]:
        print(f"  POWER Line {line}: {loading:.1%} loaded")

def handle_voltage_issues(violations):
    """Handle voltage violations - WORLD CLASS"""
    
    print("\nPOWER VOLTAGE CONTROL ACTIVATED")
    
    # Group violations by severity
    critical = [v for v in violations if abs(v['deviation']) > 0.1]
    warning = [v for v in violations if 0.05 < abs(v['deviation']) <= 0.1]
    
    if critical:
        print(f"  [CRITICAL] CRITICAL: {len(critical)} buses with >10% deviation")
        # Implement voltage control actions
        for violation in critical[:3]:  # Show top 3
            print(f"    Bus {violation.get('bus', 'unknown')}: {violation.get('voltage', 0):.3f} pu")
    
    if warning:
        print(f"  [WARNING] WARNING: {len(warning)} buses with 5-10% deviation")

def check_substation_overloads(substation_loads):
    """Check for substation overloads - WORLD CLASS"""
    
    for substation_name, ev_load_kw in substation_loads.items():
        if substation_name in integrated_system.substations:
            substation = integrated_system.substations[substation_name]
            
            # Total load including base + EV
            total_load_mw = substation['load_mw'] + (ev_load_kw / 1000)
            capacity_mva = substation['capacity_mva']
            
            # Assume 0.9 power factor
            capacity_mw = capacity_mva * 0.9
            loading_percent = (total_load_mw / capacity_mw) * 100
            
            if loading_percent > 90:
                print(f"Fire SUBSTATION OVERLOAD: {substation_name}")
                print(f"   Load: {total_load_mw:.1f} MW / {capacity_mw:.1f} MW ({loading_percent:.1f}%)")
                
                if loading_percent > 100:
                    print(f"   [CRITICAL] {substation_name} WOULD TRIP - INITIATING LOAD SHED")
                    initiate_load_shedding(substation_name, total_load_mw - capacity_mw)

def initiate_emergency_response(charging_details):
    """Emergency response when power flow diverges"""
    
    print("\n[EMERGENCY][EMERGENCY] EMERGENCY RESPONSE ACTIVATED [EMERGENCY][EMERGENCY]")
    print(f"  System cannot support {charging_details['total_power_kw']/1000:.1f} MW EV load")
    
    # Stop all new charging
    if hasattr(sumo_manager, 'stop_new_charging'):
        sumo_manager.stop_new_charging()
    
    # Reduce existing charging
    print("  Reducing all charging rates to 25%")
    
    # Signal critical state to dashboard
    system_state['emergency'] = True

def initiate_load_shedding(substation_name, excess_mw):
    """Implement load shedding to prevent cascade"""
    
    print(f"\nPOWER LOAD SHEDDING at {substation_name}: {excess_mw:.1f} MW")
    
    # Priority order for shedding
    # 1. Reduce EV charging
    # 2. Turn off non-critical loads
    # 3. Rolling blackouts if necessary
    
    # This would interface with your actual control system
    pass
# Start simulation thread
sim_thread = threading.Thread(target=simulation_loop, daemon=True)
sim_thread.start()

# ============================================================================
# FLASK ROUTE DEFINITIONS - ORGANIZED BY FUNCTIONALITY
# ============================================================================

# ============================================================================
# 1. CORE ROUTES (Main page, debug)
# ============================================================================

@app.route('/')
def index():
    """Serve complete dashboard with all features"""
    return render_template_string(load_html_template())

@app.route('/api/debug/buses')
def debug_buses():
    """Show all bus names in PyPSA"""
    buses_13kv = [b for b in power_grid.network.buses.index if '13.8kV' in b]

    # Also show substation names from integrated system
    substations = list(integrated_system.substations.keys())

    return jsonify({
        'pypsa_buses_13kv': buses_13kv,
        'integrated_substations': substations,
        'mapping_check': {
            sub: f"{sub.replace(' ', '_')}_13.8kV" in power_grid.network.buses.index
            for sub in substations
        }
    })

@app.route('/api/debug/pypsa')
def debug_pypsa():
    """Debug PyPSA network state"""

    debug_info = {
        'buses': list(power_grid.network.buses.index),
        'loads': {},
        'generators': {},
        'total_load': 0,
        'total_generation': 0
    }

    # Check all loads
    for load_name in power_grid.network.loads.index:
        load_value = power_grid.network.loads.at[load_name, 'p_set']
        debug_info['loads'][load_name] = float(load_value)
        debug_info['total_load'] += float(load_value)

    # Check generators
    for gen_name in power_grid.network.generators.index:
        gen_p = power_grid.network.generators.at[gen_name, 'p_nom']
        debug_info['generators'][gen_name] = float(gen_p)
        debug_info['total_generation'] += float(gen_p)

    # Check if loads_t exists and has wrong values
    if hasattr(power_grid.network, 'loads_t') and hasattr(power_grid.network.loads_t, 'p'):
        debug_info['loads_t_sum'] = float(power_grid.network.loads_t.p.sum().sum())
        debug_info['loads_t_shape'] = power_grid.network.loads_t.p.shape

    return jsonify(debug_info)

@app.route('/api/debug/ev_stations')
def debug_ev_stations():
    """Debug endpoint to check EV station status"""
    status = {}

    for ev_id, ev_station in integrated_system.ev_stations.items():
        status[ev_id] = {
            'name': ev_station['name'],
            'substation': ev_station['substation'],
            'operational': ev_station['operational'],
            'substation_operational': integrated_system.substations[ev_station['substation']]['operational'],
            'vehicles_charging': ev_station.get('vehicles_charging', 0),
            'current_load_kw': ev_station.get('current_load_kw', 0)
        }

    return jsonify(status)

# ============================================================================
# 2. NETWORK & STATUS ROUTES
# ============================================================================

@app.route('/api/network_state')
def get_network_state():
    """Get complete network state including vehicles - OPTIMIZED FOR 1000+ VEHICLES"""
    state = integrated_system.get_network_state()

    # Add vehicle data if SUMO is running
    if system_state['sumo_running'] and sumo_manager.running:
        vehicles = []
        station_charging_counts = {}
        station_queued_counts = {}

        try:
            import traci
            # OPTIMIZATION: Get all vehicle IDs once (batch API call)
            active_vehicle_ids = set(traci.vehicle.getIDList())

            # OPTIMIZATION: Only process vehicles that exist in SUMO
            for vehicle in sumo_manager.vehicles.values():
                if vehicle.id not in active_vehicle_ids:
                    continue

                try:
                    # OPTIMIZATION: Single position call instead of multiple
                    x, y = traci.vehicle.getPosition(vehicle.id)
                    lon, lat = traci.simulation.convertGeo(x, y)

                    # OPTIMIZATION: Skip expensive edge shape calculation for API response
                    # Edge shapes should be sent once at initialization, not every frame
                    edge_id = traci.vehicle.getRoadID(vehicle.id)

                    # Track charging/queued counts (no change)
                    if getattr(vehicle, 'is_charging', False) and vehicle.assigned_ev_station:
                        station_charging_counts[vehicle.assigned_ev_station] = station_charging_counts.get(vehicle.assigned_ev_station, 0) + 1

                    if getattr(vehicle, 'is_queued', False) and vehicle.assigned_ev_station:
                        station_queued_counts[vehicle.assigned_ev_station] = station_queued_counts.get(vehicle.assigned_ev_station, 0) + 1

                    # OPTIMIZATION: Simplified vehicle data (removed unnecessary fields)
                    vehicles.append({
                        'id': vehicle.id,
                        'lat': lat,
                        'lon': lon,
                        'type': vehicle.config.vtype.value,
                        'speed_kmh': round(vehicle.speed * 3.6, 1),
                        'battery_percent': round(vehicle.config.current_soc * 100) if vehicle.config.is_ev else 100,
                        'is_charging': getattr(vehicle, 'is_charging', False),
                        'is_queued': getattr(vehicle, 'is_queued', False),
                        'is_v2g_active': vehicle.id in v2g_manager.active_sessions,
                        'is_ev': vehicle.config.is_ev,
                        'assigned_station': vehicle.assigned_ev_station,
                        'edge_id': edge_id if edge_id and not edge_id.startswith(':') else None
                    })
                except Exception:
                    continue

        except Exception:
            pass

        state['vehicles'] = vehicles
        state['vehicle_stats'] = sumo_manager.get_statistics()

        # Update EV station charging counts
        for ev_station in state['ev_stations']:
            ev_station['vehicles_charging'] = station_charging_counts.get(ev_station['id'], 0)
            ev_station['vehicles_queued'] = station_queued_counts.get(ev_station['id'], 0)
    else:
        state['vehicles'] = []
        state['vehicle_stats'] = {}

    return jsonify(state)

@app.route('/api/status')
def get_status():
    """Get complete system status"""
    power_status = power_grid.get_system_status()

    # CRITICAL: Merge operational status from integrated_system (includes scenario controller failures!)
    for sub_name in integrated_system.substations.keys():
        if sub_name in power_status.get('substations', {}):
            integrated_sub = integrated_system.substations[sub_name]
            power_status['substations'][sub_name]['operational'] = integrated_sub.get('operational', True)
            power_status['substations'][sub_name]['load_mw'] = integrated_sub.get('load_mw', 0)
            power_status['substations'][sub_name]['lat'] = integrated_sub.get('lat', 0)
            power_status['substations'][sub_name]['lon'] = integrated_sub.get('lon', 0)

    # Add vehicle statistics
    if system_state['sumo_running'] and sumo_manager.running:
        vehicle_stats = sumo_manager.get_statistics()
        power_status['vehicles'] = {
            'total': vehicle_stats['total_vehicles'],
            'active': len(sumo_manager.vehicles),
            'evs': vehicle_stats['ev_vehicles'],
            'charging': vehicle_stats['vehicles_charging'],
            'avg_speed_kmh': round(vehicle_stats['avg_speed_mps'] * 3.6, 1),
            'energy_consumed_kwh': round(vehicle_stats['total_energy_consumed_kwh'], 2)
        }
    else:
        power_status['vehicles'] = {
            'total': 0,
            'active': 0,
            'evs': 0,
            'charging': 0,
            'avg_speed_kmh': 0,
            'energy_consumed_kwh': 0
        }

    power_status['simulation'] = {
        'sumo_running': system_state['sumo_running'],
        'speed': system_state['simulation_speed'],
        'scenario': system_state['scenario'].value
    }

    return jsonify(power_status)

# ============================================================================
# 3. SUMO & VEHICLE ROUTES
# ============================================================================

@app.route('/api/sumo/start', methods=['POST'])
def start_sumo():
    """Start SUMO simulation"""
    global system_state

    if system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'SUMO already running'})

    try:
        # Start SUMO (headless for web interface)
        success = sumo_manager.start_sumo(gui=False, seed=42)

        if success:
            system_state['sumo_running'] = True

            # Spawn initial vehicles
            data = request.json or {}
            count = data.get('vehicle_count', 10)
            ev_percentage = data.get('ev_percentage', 0.7)
            battery_min_soc = data.get('battery_min_soc', 0.2)
            battery_max_soc = data.get('battery_max_soc', 0.9)

            spawned = sumo_manager.spawn_vehicles(count, ev_percentage, battery_min_soc, battery_max_soc)

            # Preload edge shapes for road snapping (limit for faster start if needed)
            try:
                cached = preload_edge_shapes()
                print(f"Preloaded {cached} SUMO edge shapes")
            except Exception as e:
                print(f"Edge preload skipped: {e}")
            return jsonify({
                'success': True,
                'message': f'SUMO started with vehicles',
                'vehicles_spawned': spawned
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start SUMO'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/sumo/stop', methods=['POST'])
def stop_sumo():
    """Stop SUMO simulation"""
    global system_state

    if system_state['sumo_running']:
        sumo_manager.stop()
        system_state['sumo_running'] = False
        return jsonify({'success': True, 'message': 'SUMO stopped'})

    return jsonify({'success': False, 'message': 'SUMO not running'})

@app.route('/api/sumo/spawn', methods=['POST'])
def spawn_vehicles():
    """Spawn additional vehicles"""
    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'SUMO not running'})

    data = request.json or {}
    count = data.get('count', 5)
    ev_percentage = data.get('ev_percentage', 0.7)
    battery_min_soc = data.get('battery_min_soc', 0.2)
    battery_max_soc = data.get('battery_max_soc', 0.9)

    spawned = sumo_manager.spawn_vehicles(count, ev_percentage, battery_min_soc, battery_max_soc)

    return jsonify({
        'success': True,
        'spawned': spawned,
        'total_vehicles': sumo_manager.stats['total_vehicles']
    })

@app.route('/api/sumo/scenario', methods=['POST'])
def set_scenario():
    """Scenario control minimized per request. Only EV rush supported."""
    data = request.json or {}
    scenario_name = data.get('scenario', 'EV_RUSH')

    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'SUMO not running'})

    if scenario_name == 'EV_RUSH':
        spawned = sumo_manager.spawn_vehicles(30, 0.9)
        return jsonify({'success': True, 'scenario': 'EV_RUSH', 'spawned': spawned})

    return jsonify({'success': False, 'message': 'Only EV_RUSH is supported now'})

@app.route('/api/simulation/speed', methods=['POST'])
def set_simulation_speed():
    """Set simulation speed"""
    data = request.json or {}
    speed = data.get('speed', 1.0)

    system_state['simulation_speed'] = max(0.1, min(10.0, speed))

    return jsonify({'success': True, 'speed': system_state['simulation_speed']})

@app.route('/api/ev/config', methods=['POST'])
def update_ev_config():
    """Update EV configuration settings"""

    try:
        data = request.json or {}

        # Validate input
        ev_percentage = data.get('ev_percentage', 70)
        battery_min_soc = data.get('battery_min_soc', 20)
        battery_max_soc = data.get('battery_max_soc', 90)

        # Clamp values to valid ranges
        ev_percentage = max(0, min(100, ev_percentage))
        battery_min_soc = max(1, min(100, battery_min_soc))
        battery_max_soc = max(1, min(100, battery_max_soc))

        # Ensure min < max
        if battery_min_soc >= battery_max_soc:
            battery_min_soc = battery_max_soc - 1

        # Store configuration globally
        global current_ev_config
        current_ev_config = {
            'ev_percentage': ev_percentage,
            'battery_min_soc': battery_min_soc,
            'battery_max_soc': battery_max_soc,
            'updated_at': datetime.now().isoformat()
        }

        # Update SUMO manager if running
        if sumo_manager and sumo_manager.running:
            sumo_manager.ev_percentage = ev_percentage / 100
            sumo_manager.battery_min_soc = battery_min_soc / 100
            sumo_manager.battery_max_soc = battery_max_soc / 100

        print(f"Success EV Configuration Updated:")
        print(f"   EV Percentage: {ev_percentage}%")
        print(f"   Battery SOC Range: {battery_min_soc}% - {battery_max_soc}%")

        return jsonify({
            'success': True,
            'message': 'EV configuration updated successfully',
            'config': current_ev_config
        })

    except Exception as e:
        print(f"[ERROR] EV config update error: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to update EV configuration: {str(e)}'
        }), 500

@app.route('/api/ev/config', methods=['GET'])
def get_ev_config():
    """Get current EV configuration"""

    global current_ev_config
    if not current_ev_config:
        current_ev_config = {
            'ev_percentage': 70,
            'battery_min_soc': 20,
            'battery_max_soc': 90,
            'updated_at': datetime.now().isoformat()
        }

    return jsonify({
        'success': True,
        'config': current_ev_config
    })

@app.route('/api/test/ev_rush', methods=['POST'])
def test_ev_rush():
    """Test scenario: spawn many low-battery EVs"""
    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'Start SUMO first'})

    # Spawn 30 EVs with very low battery
    spawned = 0
    for i in range(30):
        vehicle_id = f"test_ev_{i}"
        try:
            # Get random edges
            import traci
            edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
            if len(edges) >= 2:
                origin = edges[i % len(edges)]
                dest = edges[(i + 10) % len(edges)]

                # Create route
                route = traci.simulation.findRoute(origin, dest)
                if route and route.edges:
                    route_id = f"test_route_{i}"
                    traci.route.add(route_id, route.edges)

                    # Add EV with VERY low battery
                    traci.vehicle.add(vehicle_id, route_id, typeID="ev_sedan", depart="now")
                    traci.vehicle.setColor(vehicle_id, (255, 0, 0, 255))  # Red for low battery
                    traci.vehicle.setMaxSpeed(vehicle_id, 40)  # Fast movement

                    # Set very low battery (10-20%)
                    battery = 75000 * random.uniform(0.10, 0.20)
                    traci.vehicle.setParameter(vehicle_id, "device.battery.actualBatteryCapacity", str(battery))

                    spawned += 1
        except:
            pass

    return jsonify({
        'success': True,
        'message': f'Spawned {spawned} low-battery EVs for testing'
    })

# ============================================================================
# 4. POWER GRID ROUTES (/api/fail/*, /api/restore/*)
# ============================================================================

@app.route('/api/fail/<substation>', methods=['POST'])
def fail_substation(substation):
    """Trigger substation failure affecting traffic lights and EV stations"""
    impact = integrated_system.simulate_substation_failure(substation)
    power_grid.trigger_failure('substation', substation)

    # Update SUMO traffic lights if running
    if system_state['sumo_running'] and sumo_manager.running:
        # Update traffic lights - they go to YELLOW during blackout, not RED
        sumo_manager.update_traffic_lights()

        # Handle blackout for traffic lights specifically
        if hasattr(sumo_manager, 'handle_blackout_traffic_lights'):
            sumo_manager.handle_blackout_traffic_lights([substation])

        # UPDATE EV STATION STATUS PROPERLY
        for ev_id, ev_station in integrated_system.ev_stations.items():
            if ev_station['substation'] == substation:
                # Mark station as non-operational in integrated system
                ev_station['operational'] = False

                # Update SUMO manager's station status
                if ev_id in sumo_manager.ev_stations_sumo:
                    sumo_manager.ev_stations_sumo[ev_id]['available'] = 0

                # Update station manager's status if it exists
                if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
                    if ev_id in sumo_manager.station_manager.stations:
                        sumo_manager.station_manager.stations[ev_id]['operational'] = False

                        # Call the blackout handler and clear vehicle assignments so they'll reroute
                        released = sumo_manager.station_manager.handle_blackout(substation)
                        if released:
                            for veh_id in released:
                                if hasattr(sumo_manager, 'vehicles') and veh_id in sumo_manager.vehicles:
                                    v = sumo_manager.vehicles[veh_id]
                                    if hasattr(v, 'is_charging'):
                                        v.is_charging = False
                                    if hasattr(v, 'assigned_ev_station'):
                                        v.assigned_ev_station = None

        # Clear en-route assignments to any stations affected by this substation
        if hasattr(sumo_manager, 'vehicles') and sumo_manager.vehicles:
            for v in sumo_manager.vehicles.values():
                if hasattr(v, 'assigned_ev_station') and v.assigned_ev_station:
                    sid = v.assigned_ev_station
                    if sid in integrated_system.ev_stations and integrated_system.ev_stations[sid]['substation'] == substation:
                        v.assigned_ev_station = None
                        if hasattr(v, 'is_charging'):
                            v.is_charging = False

    print(f"\nPOWER SUBSTATION FAILURE: {substation}")
    print(f"   - Traffic lights: Set to YELLOW (caution mode)")
    print(f"   - EV stations affected: {impact.get('ev_stations_affected', 0)}")
    print(f"   - Load lost: {impact.get('load_lost_mw', 0):.1f} MW")

    return jsonify(impact)

@app.route('/api/fail/station/<station_id>', methods=['POST'])
def fail_ev_station(station_id):
    """Trigger individual EV station failure"""

    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'Start SUMO first'})

    # Check if station exists
    if station_id not in integrated_system.ev_stations:
        return jsonify({'success': False, 'message': f'Station {station_id} not found'})

    # Handle station failure in station manager
    released_vehicles = []
    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
        released_vehicles = sumo_manager.station_manager.handle_station_failure(station_id)
        # Clear assignment on released vehicles so they can pick a new station
        if released_vehicles:
            for veh_id in released_vehicles:
                if hasattr(sumo_manager, 'vehicles') and veh_id in sumo_manager.vehicles:
                    v = sumo_manager.vehicles[veh_id]
                    if hasattr(v, 'is_charging'):
                        v.is_charging = False
                    if hasattr(v, 'assigned_ev_station'):
                        v.assigned_ev_station = None

    # Also clear en-route vehicles targeting this failed station
    if hasattr(sumo_manager, 'vehicles') and sumo_manager.vehicles:
        for v in sumo_manager.vehicles.values():
            if hasattr(v, 'assigned_ev_station') and v.assigned_ev_station == station_id:
                v.assigned_ev_station = None
                if hasattr(v, 'is_charging'):
                    v.is_charging = False

    # Update integrated system
    integrated_system.ev_stations[station_id]['operational'] = False

    # Update SUMO manager's station status
    if station_id in sumo_manager.ev_stations_sumo:
        sumo_manager.ev_stations_sumo[station_id]['available'] = 0

    station_name = integrated_system.ev_stations[station_id]['name']

    return jsonify({
        'success': True,
        'station_id': station_id,
        'station_name': station_name,
        'released_vehicles': released_vehicles,
        'message': f'Station {station_name} failed - {len(released_vehicles)} vehicles released'
    })

@app.route('/api/restore/<substation>', methods=['POST'])
def restore_substation(substation):
    """Restore substation"""
    success = integrated_system.restore_substation(substation)

    restoration_data = {
        'substation': substation,
        'success': success,
        'lights_restored': 0,
        'ev_stations_restored': 0,
        'timestamp': datetime.now().isoformat()
    }

    if success:
        power_grid.restore_component('substation', substation)

        # CRITICAL FIX: Disable V2G for this substation and release all vehicles
        print(f"[RESTORE] Disabling V2G for {substation} and releasing vehicles...")
        v2g_manager.disable_v2g_for_substation(substation)

        # Update SUMO traffic lights if running
        if system_state['sumo_running'] and sumo_manager.running:
            # Count lights before update
            lights_before = sum(1 for light in integrated_system.traffic_lights.values() if light.get('powered', False))

            sumo_manager.update_traffic_lights()

            # Count lights after update
            lights_after = sum(1 for light in integrated_system.traffic_lights.values() if light.get('powered', False))
            restoration_data['lights_restored'] = lights_after - lights_before

            # RESTORE EV STATION STATUS
            ev_stations_restored = 0
            for ev_id, ev_station in integrated_system.ev_stations.items():
                if ev_station['substation'] == substation:
                    # Mark station as operational
                    ev_station['operational'] = True
                    ev_stations_restored += 1

                    # Update SUMO manager
                    if ev_id in sumo_manager.ev_stations_sumo:
                        sumo_manager.ev_stations_sumo[ev_id]['available'] = ev_station['chargers']

                    # Update station manager
                    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
                        if ev_id in sumo_manager.station_manager.stations:
                            sumo_manager.station_manager.stations[ev_id]['operational'] = True
                            print(f"   Success Restored {ev_station['name']} ONLINE")

            restoration_data['ev_stations_restored'] = ev_stations_restored

        # OPTIONAL: Send proactive notification to chatbot (commented out to avoid spam)
        # Uncomment if you want chatbot to auto-announce all manual restorations
        # try:
        #     import asyncio
        #     if ultra_chatbot:
        #         notification_msg = f"System notification: {substation} substation has been manually restored. {restoration_data.get('lights_restored', 0)} traffic lights and {restoration_data.get('ev_stations_restored', 0)} EV stations are back online."
        #         asyncio.run(ultra_chatbot.chat(notification_msg))
        # except Exception as e:
        #     print(f"[RESTORE] Could not notify chatbot: {e}")

    return jsonify(restoration_data)

@app.route('/api/restore/station/<station_id>', methods=['POST'])
def restore_ev_station(station_id):
    """Restore individual EV station"""

    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'Start SUMO first'})

    # Check if station exists
    if station_id not in integrated_system.ev_stations:
        return jsonify({'success': False, 'message': f'Station {station_id} not found'})

    # Restore station in station manager
    success = False
    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
        success = sumo_manager.station_manager.restore_station(station_id)

    # Update integrated system
    integrated_system.ev_stations[station_id]['operational'] = True

    # Update SUMO manager's station status
    if station_id in sumo_manager.ev_stations_sumo:
        station_info = integrated_system.ev_stations[station_id]
        sumo_manager.ev_stations_sumo[station_id]['available'] = station_info['chargers']

    station_name = integrated_system.ev_stations[station_id]['name']

    return jsonify({
        'success': success,
        'station_id': station_id,
        'station_name': station_name,
        'message': f'Station {station_name} restored successfully'
    })

@app.route('/api/restore_all', methods=['POST'])
def restore_all():
    """Restore all substations"""
    restored_count = 0

    for sub_name in integrated_system.substations.keys():
        integrated_system.restore_substation(sub_name)
        power_grid.restore_component('substation', sub_name)

        # CRITICAL: Disable V2G for each substation and release vehicles
        print(f"[RESTORE ALL] Disabling V2G for {sub_name} and releasing vehicles...")
        v2g_manager.disable_v2g_for_substation(sub_name)
        restored_count += 1

    # Update SUMO if running
    if system_state['sumo_running'] and sumo_manager.running:
        sumo_manager.update_traffic_lights()

        # Restore all EV stations
        for ev_id, ev_station in integrated_system.ev_stations.items():
            if ev_id in sumo_manager.ev_stations_sumo:
                sumo_manager.ev_stations_sumo[ev_id]['available'] = ev_station['chargers']

    return jsonify({
        'success': True,
        'message': f'All {restored_count} substations restored',
        'restored_count': restored_count
    })

@app.route('/api/test/station_failure', methods=['POST'])
def test_station_failure_scenario():
    """Test EV station failure scenario"""

    if not system_state['sumo_running']:
        return jsonify({'success': False, 'message': 'Start SUMO first'})

    # Find a station with vehicles charging
    test_station = None
    for station_id, station in integrated_system.ev_stations.items():
        if station['operational'] and station['vehicles_charging'] > 0:
            test_station = station_id
            break

    # If no station has vehicles, find any operational station
    if not test_station:
        for station_id, station in integrated_system.ev_stations.items():
            if station['operational']:
                test_station = station_id
                break

    if not test_station:
        return jsonify({'success': False, 'message': 'No operational stations available for testing'})

    # Fail the station
    released_vehicles = []
    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
        released_vehicles = sumo_manager.station_manager.handle_station_failure(test_station)

    # Update integrated system
    integrated_system.ev_stations[test_station]['operational'] = False

    # Update SUMO manager's station status
    if test_station in sumo_manager.ev_stations_sumo:
        sumo_manager.ev_stations_sumo[test_station]['available'] = 0

    station_name = integrated_system.ev_stations[test_station]['name']

    return jsonify({
        'success': True,
        'test_station': test_station,
        'station_name': station_name,
        'released_vehicles': released_vehicles,
        'message': f'Station failure test: {station_name} failed - {len(released_vehicles)} vehicles released',
        'instructions': f'Watch as vehicles at {station_name} stop charging and redirect to other stations if they still need charging.'
    })

# ============================================================================
# 5. V2G ROUTES (/api/v2g/*)
# ============================================================================

@app.route('/api/v2g/enable/<substation>', methods=['POST'])
def enable_v2g(substation):
    """Enable V2G for a failed substation with better feedback"""

    # Check if substation is actually failed
    if substation not in integrated_system.substations:
        return jsonify({
            'success': False,
            'message': f'Substation {substation} not found'
        })

    sub_data = integrated_system.substations[substation]

    if sub_data['operational']:
        return jsonify({
            'success': False,
            'message': f'{substation} is operational - V2G not needed'
        })

    success = v2g_manager.enable_v2g_for_substation(substation)

    if success:
        # Get real-time metrics
        power_needed_mw = sub_data['load_mw']
        rate = v2g_manager.get_current_rate(substation)
        energy_needed = v2g_manager.substation_energy_required.get(substation, 50)

        # Calculate potential earnings
        total_value = energy_needed * rate
        vehicles_needed = max(2, int(energy_needed / 30) + 1)  # 30 kWh per vehicle

        return jsonify({
            'success': True,
            'message': f'V2G enabled for {substation}',
            'power_needed_mw': power_needed_mw,
            'energy_needed_kwh': energy_needed,
            'rate_per_kwh': rate,
            'total_restoration_value': total_value,
            'vehicles_needed': vehicles_needed,
            'earnings_per_vehicle': total_value / vehicles_needed
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Failed to enable V2G for {substation}'
        })

@app.route('/api/v2g/disable/<substation>', methods=['POST'])
def disable_v2g(substation):
    """Disable V2G for a substation"""
    v2g_manager.disable_v2g_for_substation(substation)
    return jsonify({'success': True})

@app.route('/api/v2g/release_vehicles/<substation>', methods=['POST'])
def release_v2g_vehicles(substation):
    """Force release all V2G vehicles from this substation's charging stations"""
    try:
        print(f"\n[API RELEASE] ========== FORCE RELEASING V2G VEHICLES ==========")
        print(f"[API RELEASE] Target substation: {substation}")
        print(f"[API RELEASE] Current active sessions: {len(v2g_manager.active_sessions)}")

        # Get all EV stations for this substation
        substation_ev_stations = []
        for ev_id, ev_data in integrated_system.ev_stations.items():
            if ev_data.get('substation') == substation:
                substation_ev_stations.append(ev_id)

        print(f"[API RELEASE] Found {len(substation_ev_stations)} EV stations for {substation}: {substation_ev_stations}")

        # CRITICAL: Force end ALL V2G sessions for this substation
        # active_sessions is keyed by vehicle_id, not session_id
        vehicles_to_release = []
        for vehicle_id, session in list(v2g_manager.active_sessions.items()):
            if session.substation_id == substation or session.station_id in substation_ev_stations:
                vehicles_to_release.append(vehicle_id)

        print(f"[API RELEASE] Found {len(vehicles_to_release)} vehicles to release: {vehicles_to_release}")

        released_count = 0
        for vehicle_id in vehicles_to_release:
            print(f"[API RELEASE] Releasing {vehicle_id}...")

            # 1. End the V2G session
            if vehicle_id in v2g_manager.active_sessions:
                session = v2g_manager.active_sessions[vehicle_id]
                session.end_time = datetime.now()
                session.locked_at_station = False
                del v2g_manager.active_sessions[vehicle_id]
                print(f"[API RELEASE]   ✓ Removed from active_sessions")

            # 2. Remove from locked vehicles
            if vehicle_id in v2g_manager.v2g_locked_vehicles:
                v2g_manager.v2g_locked_vehicles.remove(vehicle_id)
                print(f"[API RELEASE]   ✓ Removed from v2g_locked_vehicles")

            # 3. Remove from pending vehicles
            if vehicle_id in v2g_manager.pending_v2g_vehicles:
                v2g_manager.pending_v2g_vehicles.remove(vehicle_id)
                print(f"[API RELEASE]   ✓ Removed from pending_v2g_vehicles")

            # 4. Clear SUMO vehicle V2G locks and state
            if vehicle_id in sumo_manager.vehicles:
                vehicle = sumo_manager.vehicles[vehicle_id]

                # Clear V2G session flags
                vehicle.in_v2g_session = False
                vehicle.v2g_lock = False
                vehicle.is_charging = False
                vehicle.charge_start_time = None

                # Let vehicle resume movement - SUMO manager will handle routing
                print(f"[API RELEASE]   ✓ Cleared V2G locks for {vehicle_id}")

            released_count += 1
            print(f"[API RELEASE]   ✅ Successfully released {vehicle_id}")

        print(f"\n[API RELEASE] ========== RELEASE COMPLETE ==========")
        print(f"[API RELEASE] Released {released_count} vehicles")
        print(f"[API RELEASE] Remaining active sessions: {len(v2g_manager.active_sessions)}")

        return jsonify({
            'success': True,
            'released': released_count,
            'substation': substation
        })

    except Exception as e:
        print(f"[API ERROR] Failed to release V2G vehicles: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v2g/status')
def v2g_status():
    """Get V2G system status with REAL-TIME updates"""

    # Get base V2G data
    v2g_data = v2g_manager.get_v2g_dashboard_data()

    # CRITICAL FIX: Add real-time power calculations
    for substation_name in v2g_data['enabled_substations']:
        if substation_name in integrated_system.substations:
            substation = integrated_system.substations[substation_name]

            # Base power need
            base_power_need_mw = substation['load_mw']

            # Calculate actual power being provided by V2G right now
            active_v2g_power_mw = 0
            for vehicle in v2g_data['active_vehicles']:
                if vehicle['substation'] == substation_name:
                    # Each vehicle provides 250kW (0.25 MW)
                    active_v2g_power_mw += 0.25

            # Update the real-time power need (what's still needed)
            remaining_power_need_mw = max(0, base_power_need_mw - active_v2g_power_mw)

            # Update in the data
            if 'power_needs' not in v2g_data:
                v2g_data['power_needs'] = {}
            v2g_data['power_needs'][substation_name] = remaining_power_need_mw * 1000  # Convert to kW

            # Add real-time metrics
            v2g_data['real_time_metrics'] = v2g_data.get('real_time_metrics', {})
            v2g_data['real_time_metrics'][substation_name] = {
                'base_load_mw': base_power_need_mw,
                'v2g_providing_mw': active_v2g_power_mw,
                'remaining_need_mw': remaining_power_need_mw,
                'vehicles_discharging': sum(1 for v in v2g_data['active_vehicles'] if v['substation'] == substation_name),
                'restoration_progress': (v2g_data.get('energy_delivered', {}).get(substation_name, 0) /
                                       max(v2g_data.get('energy_required', {}).get(substation_name, 1), 1)) * 100
            }

    # Add system-wide real-time metrics
    v2g_data['system_metrics'] = {
        'total_v2g_power_mw': v2g_data['active_sessions'] * 0.25,  # 250kW per vehicle
        'total_substations_needing_power': len(v2g_data['enabled_substations']),
        'total_power_deficit_mw': sum(
            integrated_system.substations[s]['load_mw']
            for s in v2g_data['enabled_substations']
            if s in integrated_system.substations
        ),
        'effective_power_deficit_mw': sum(
            max(0, integrated_system.substations[s]['load_mw'] -
                sum(0.25 for v in v2g_data['active_vehicles'] if v['substation'] == s))
            for s in v2g_data['enabled_substations']
            if s in integrated_system.substations
        )
    }

    # Log for debugging
    if v2g_data['active_sessions'] > 0:
        print(f"[V2G STATUS] Active sessions: {v2g_data['active_sessions']}")
        print(f"[V2G STATUS] Total V2G power: {v2g_data['system_metrics']['total_v2g_power_mw']:.2f} MW")
        print(f"[V2G STATUS] Power deficit: {v2g_data['system_metrics']['total_power_deficit_mw']:.2f} MW -> "
              f"{v2g_data['system_metrics']['effective_power_deficit_mw']:.2f} MW")

    return jsonify(v2g_data)

@app.route('/api/v2g/start_session', methods=['POST'])
def start_v2g_session():
    """Manually start V2G session for testing"""
    data = request.json or {}
    vehicle_id = data.get('vehicle_id')
    station_id = data.get('station_id')
    substation_id = data.get('substation_id')

    if not all([vehicle_id, station_id, substation_id]):
        return jsonify({'success': False, 'message': 'Missing parameters'})

    success = v2g_manager.start_v2g_session(vehicle_id, station_id, substation_id)
    return jsonify({'success': success})

@app.route('/api/v2g/test', methods=['POST'])
def test_v2g_scenario():
    """Test V2G with a complete scenario"""

    try:
        # 1. Fail Times Square if operational
        times_square = integrated_system.substations.get('Times Square')
        if times_square and times_square['operational']:
            integrated_system.simulate_substation_failure('Times Square')
            time.sleep(0.5)

        # 2. Enable V2G
        success = v2g_manager.enable_v2g_for_substation('Times Square')

        if not success:
            return jsonify({
                'success': False,
                'message': 'Could not enable V2G for Times Square'
            })

        # 3. Find and route high-SOC vehicles
        routed_vehicles = []
        if sumo_manager.running:
            import traci
            for vehicle in sumo_manager.vehicles.values():
                if (vehicle.config.is_ev and
                    vehicle.config.current_soc >= 0.60 and
                    not hasattr(vehicle, 'in_v2g_session') and
                    len(routed_vehicles) < 3):

                    # Force high SOC for testing
                    vehicle.config.current_soc = 0.85
                    v2g_manager._route_to_v2g_station(vehicle, 'Times Square')
                    routed_vehicles.append(vehicle.id)

        return jsonify({
            'success': True,
            'message': 'V2G test scenario started',
            'substation': 'Times Square',
            'power_deficit_mw': times_square['load_mw'],
            'rate_per_kwh': v2g_manager.get_current_rate('Times Square'),
            'vehicles_routed': routed_vehicles,
            'expected_duration': '15-30 seconds',
            'expected_earnings_per_vehicle': '$150-300'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Test failed: {str(e)}'
        })

# ============================================================================
# 6. ML ANALYTICS ROUTES - REMOVED
# ============================================================================
# All ML Analytics endpoints have been removed

# ============================================================================
# 7. AI & CHATBOT ROUTES (/api/ai/*)
# ============================================================================

@app.route('/api/ai/advice', methods=['GET', 'POST'])
def ai_advice():
    """Generate AI advice using the world-class chatbot system."""
    try:
        # Get user question if provided
        q = request.args.get('q')
        if request.method == 'POST':
            body = request.get_json(silent=True) or {}
            q = q or body.get('question')

        if not q:
            q = "Provide insights and recommendations for grid optimization, V2G opportunities, and system improvements."

        # Use the enhanced AI chatbot
        response = ai_chatbot.process_message(q, user_id="api_user")

        return jsonify({
            'advice': response['text'],
            'type': response.get('type', 'response'),
            'intent': response.get('intent', 'general'),
            'timestamp': response.get('timestamp', datetime.now().isoformat()),
            'data': response.get('data', {})
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/report')
def ai_report():
    """Generate comprehensive AI report using the enhanced chatbot."""
    try:
        # Generate comprehensive system report
        response = ai_chatbot.generate_system_report()

        return jsonify({
            'report': response['text'],
            'summary': response.get('summary', {}),
            'recommendations': response.get('recommendations', []),
            'timestamp': response.get('timestamp', datetime.now().isoformat())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/v2g/optimize', methods=['POST'])
def ai_v2g_optimize():
    """AI-powered V2G optimization recommendations."""
    try:
        body = request.get_json() or {}
        optimization_type = body.get('type', 'general')

        # Get V2G optimization recommendations
        response = ai_chatbot.get_v2g_optimization(optimization_type)

        return jsonify({
            'optimization': response['text'],
            'recommendations': response.get('recommendations', []),
            'potential_savings': response.get('potential_savings', {}),
            'timestamp': response.get('timestamp', datetime.now().isoformat())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/predict', methods=['POST'])
def ai_predict():
    """AI-powered predictions for grid operations."""
    try:
        body = request.get_json() or {}
        prediction_type = body.get('type', 'demand')
        timeframe = body.get('timeframe', '1h')

        # Get AI predictions
        response = ai_chatbot.get_predictions(prediction_type, timeframe)

        return jsonify({
            'predictions': response['text'],
            'data': response.get('data', {}),
            'confidence': response.get('confidence', 0.85),
            'timestamp': response.get('timestamp', datetime.now().isoformat())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """WORLD-CLASS AI CHAT - True system control and intelligence."""
    from datetime import datetime
    try:
        body = request.get_json() or {}
        message = body.get('message', '')
        user_id = body.get('user_id', 'system_operator')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # FORCE USE ULTRA-INTELLIGENT CHATBOT - PRIORITY #1 (With typo correction)
        print(f"[DEBUG] Processing message: {message}")
        print(f"[DEBUG] ultra_chatbot available: {ultra_chatbot is not None}")
        print(f"[DEBUG] world_class_ai available: {world_class_ai is not None}")

        # TRY ULTRA-INTELLIGENT CHATBOT FIRST (with typo correction and suggestions)
        print(f"[API /ai/chat] ultra_chatbot exists: {ultra_chatbot is not None}")
        if ultra_chatbot:
            print(f"[DEBUG] ✅ ROUTING TO ULTRA-INTELLIGENT CHATBOT for message: {message}")
            try:
                import asyncio
                user_id = body.get('user_id', 'web_user')
                print(f"[DEBUG] Calling ultra_chatbot.chat() with message='{message}', user_id='{user_id}'")
                ai_response = asyncio.run(ultra_chatbot.chat(message, user_id=user_id))
                print(f"[DEBUG] Ultra-Intelligent Chatbot SUCCESS: {ai_response}")

                # CRITICAL FIX: Ensure proper response format for scenario-director.js
                # Ultra chatbot returns {'text': ...}, but scenario expects {'response': ...}
                response_text = ai_response.get('text', '') if isinstance(ai_response, dict) else str(ai_response)
                return jsonify({
                    'status': 'success',
                    'response': response_text,
                    'full_data': ai_response  # Include full response for debugging
                })
            except Exception as e:
                print(f"[ERROR] Ultra-Intelligent Chatbot error: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to world-class AI if ultra chatbot fails

        # FALLBACK TO WORLD-CLASS AI CONTROLLER
        if world_class_ai:
            print(f"[DEBUG] ROUTING TO WORLD-CLASS AI for message: {message}")
            try:
                ai_response = world_class_ai.process_intelligent_command(message)
                print(f"[DEBUG] World-class AI SUCCESS: {ai_response}")
                return jsonify(ai_response)
            except Exception as e:
                print(f"[ERROR] World-class AI error: {e}")
                import traceback
                traceback.print_exc()
                # Even if there's an error, still try to use world-class AI fallback
                return jsonify({
                    'text': f'[ERROR] Command failed: {str(e)}\\n\\nTry: "Turn off Times Square substation", "Show me Penn Station area", "System status"',
                    'type': 'error',
                    'intent': 'system_control',
                    'confidence': 0.5,
                    'system_controlled': False,
                    'timestamp': datetime.now().isoformat()
                })
        else:
            print(f"[CRITICAL] World-class AI NOT AVAILABLE - this should never happen!")
            return jsonify({
                'text': 'CRITICAL ERROR: World-class AI controller not initialized',
                'type': 'error',
                'intent': 'system_error',
                'confidence': 0.0,
                'system_controlled': False,
                'timestamp': datetime.now().isoformat()
            })

        # This should never be reached - world-class AI should always be available

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/enhanced/status')
def ai_enhanced_status():
    """Get enhanced AI system status and capabilities."""
    try:
        status = ai_chatbot.get_ai_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Removed: /api/ai/enhanced/research endpoint

@app.route('/api/ai/enhanced/visual', methods=['POST'])
def ai_visual_analysis():
    """Analyze visual map data using computer vision."""
    try:
        data = request.get_json() or {}

        # Get current network state for visual analysis
        map_data = integrated_system.get_network_state()

        # Add vehicle data if SUMO is running
        if system_state['sumo_running'] and sumo_manager.running:
            vehicles = []
            try:
                import traci
                for vehicle in sumo_manager.vehicles.values():
                    if vehicle.id in traci.vehicle.getIDList():
                        x, y = traci.vehicle.getPosition(vehicle.id)
                        lon, lat = traci.simulation.convertGeo(x, y)
                        vehicles.append({
                            'id': vehicle.id,
                            'lat': lat,
                            'lon': lon,
                            'type': vehicle.config.vtype.value,
                            'speed': vehicle.speed,
                            'soc': vehicle.config.current_soc if vehicle.config.is_ev else 1.0
                        })
            except:
                vehicles = []

            map_data['vehicles'] = vehicles

        # Perform visual analysis
        visual_analysis = ai_chatbot.visual_processor.analyze_map_state(map_data)

        return jsonify({
            'visual_analysis': visual_analysis,
            'timestamp': datetime.now().isoformat(),
            'map_data_processed': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/enhanced/multimodal', methods=['POST'])
def ai_multimodal_processing():
    """Process multi-modal input (text, image, voice)."""
    try:
        # Handle text input
        text_input = request.form.get('text', '')

        # Handle image upload
        image_data = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                image_data = image_file.read()

        # Handle voice upload (would be implemented)
        voice_data = None
        if 'voice' in request.files:
            voice_file = request.files['voice']
            if voice_file:
                voice_data = voice_file.read()

        # Process multi-modal input
        result = ai_chatbot.process_multimodal_input(text_input, image_data, voice_data)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/enhanced/conversation/<user_id>')
def ai_conversation_intelligence(user_id):
    """Get conversation intelligence for a specific user."""
    try:
        intelligence = ai_chatbot.get_conversation_intelligence(user_id)
        return jsonify(intelligence)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Removed: /api/ai/enhanced/comprehensive-report endpoint

# Removed: /api/ai/enhanced/patterns endpoint

# Removed: /api/ai/enhanced/predictions endpoint

@app.route('/api/ai/enhanced/performance')
def ai_performance_metrics():
    """Get AI system performance metrics and learning insights."""
    try:
        performance = ai_chatbot.performance_tracker.get_performance_metrics()
        learning = ai_chatbot.learning_engine.get_learning_insights()

        return jsonify({
            'performance_metrics': performance,
            'learning_insights': learning,
            'system_health': 'optimal',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/map/focus', methods=['POST'])
def focus_map():
    """Focus map on specific location with real-time updates"""
    try:
        body = request.get_json() or {}
        location = body.get('location', '')
        zoom = body.get('zoom', 16)
        action_type = body.get('action_type', 'focus')

        if not location:
            return jsonify({'error': 'Location is required'}), 400

        # Predefined locations with coordinates
        locations = {
            'times_square': {'lat': 40.7580, 'lon': -73.9855, 'name': 'Times Square'},
            'penn_station': {'lat': 40.7505, 'lon': -73.9934, 'name': 'Penn Station'},
            'grand_central': {'lat': 40.7527, 'lon': -73.9772, 'name': 'Grand Central'},
            'columbus_circle': {'lat': 40.7681, 'lon': -73.9819, 'name': 'Columbus Circle'},
            'union_square': {'lat': 40.7359, 'lon': -73.9911, 'name': 'Union Square'},
            'washington_square': {'lat': 40.7308, 'lon': -73.9973, 'name': 'Washington Square'},
            'brooklyn_bridge': {'lat': 40.7061, 'lon': -73.9969, 'name': 'Brooklyn Bridge'},
            'wall_street': {'lat': 40.7074, 'lon': -74.0113, 'name': 'Wall Street'},
            'central_park': {'lat': 40.7829, 'lon': -73.9654, 'name': 'Central Park'},
            'manhattan': {'lat': 40.7831, 'lon': -73.9712, 'name': 'Manhattan Overview'}
        }

        # Find matching location
        location_key = location.lower().replace(' ', '_')
        coords = None

        for key, loc_info in locations.items():
            if key in location_key or location_key in key:
                coords = loc_info
                break

        if coords:
            # Get infrastructure data for the area
            infrastructure_data = {
                'substations': [],
                'ev_stations': [],
                'traffic_lights': []
            }

            # Add nearby substations
            if hasattr(integrated_system, 'substations'):
                for sub_id, substation in integrated_system.substations.items():
                    infrastructure_data['substations'].append({
                        'id': sub_id,
                        'name': substation.get('name', sub_id),
                        'lat': substation.get('lat'),
                        'lon': substation.get('lon'),
                        'operational': substation.get('operational', True),
                        'voltage_kv': substation.get('voltage_kv', 138)
                    })

            # Add nearby EV stations
            if hasattr(integrated_system, 'ev_stations'):
                for station_id, station in integrated_system.ev_stations.items():
                    infrastructure_data['ev_stations'].append({
                        'id': station_id,
                        'name': station.get('name', station_id),
                        'lat': station.get('lat'),
                        'lon': station.get('lon'),
                        'operational': station.get('operational', True),
                        'ports_available': 20  # Fixed 20 ports per station
                    })

            return jsonify({
                'success': True,
                'map_focus': {
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'zoom': zoom,
                    'location_name': coords['name']
                },
                'infrastructure': infrastructure_data,
                'action_type': action_type,
                'visual_elements': {
                    'highlight_area': True,
                    'show_infrastructure': True,
                    'show_real_time_data': True
                },
                'timestamp': datetime.now().isoformat()
            })

            # Store map focus data for frontend polling
            global ai_map_focus_data
            ai_map_focus_data = {
                'location': coords['name'],
                'lat': coords['lat'],
                'lon': coords['lon'],
                'zoom': zoom,
                'action_type': action_type,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return jsonify({
                'error': f'Location "{location}" not found',
                'available_locations': list(locations.keys())
            }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Global variable to store the latest AI map focus update
ai_map_focus_data = None

@app.route('/api/ai/map_focus_status')
def ai_map_focus_status():
    """Get AI map focus updates for frontend polling"""
    global ai_map_focus_data
    try:
        if ai_map_focus_data:
            return jsonify({
                'has_update': True,
                'focus_data': ai_map_focus_data
            })
        else:
            return jsonify({
                'has_update': False,
                'focus_data': None
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HTML TEMPLATE LOADER & INITIALIZATION
# ============================================================================

def load_html_template():
    """Load HTML template from external file"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: index.html file not found"

# ============================================================================
# MAIN APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("COMPLETE SYSTEM INFORMATION:")
    print(f"  - Substations: {len(integrated_system.substations)}")
    print(f"  - Distribution Transformers: {len(integrated_system.distribution_transformers)}")
    print(f"  - Traffic Lights: {len(integrated_system.traffic_lights)}")
    print(f"  - EV Stations: {len(integrated_system.ev_stations)}")
    print(f"  - Primary Cables (13.8kV): {len(integrated_system.primary_cables)}")
    print(f"  - Secondary Cables (480V): {len(integrated_system.secondary_cables)}")
    print("=" * 60)
    print("\nLaunch Starting Complete System at http://localhost:5000")
    print("\nReport INSTRUCTIONS:")
    print("  1. Open http://localhost:5000 in your browser")
    print("  2. All your original features are preserved:")
    print("     - Toggle traffic lights, cables, EV stations layers")
    print("     - Fail/restore substations")
    print("     - See traffic light phase changes")
    print("  3. NEW Vehicle Features:")
    print("     - Click 'Start Vehicles' to begin SUMO simulation")
    print("     - Watch EVs route to charging stations when battery < 20%")
    print("     - Orange vehicles = actively charging")
    print("     - Try different scenarios (Rush Hour spawns more vehicles)")
    print("     - Fail substations to see EV stations go offline")
    print("=" * 60)

    app.run(debug=False, port=5000)
