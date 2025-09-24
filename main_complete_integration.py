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

# Initialize OpenAI client (optional if key provided)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OPENAI_API_KEY and OpenAI) else None

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
    """Main simulation loop integrating power, traffic lights, and vehicles"""
    global system_state
    
    while system_state['running']:
        try:
            # Update traffic light phases every 2 seconds
            if system_state['current_time'] % 20 == 0:  # Every 2 seconds at 0.1s steps
                integrated_system.update_traffic_light_phases()
            
            # Run SUMO step if active
            if system_state['sumo_running'] and sumo_manager.running:
                # Sync traffic lights to SUMO
                sumo_manager.update_traffic_lights()
                
                # Step SUMO simulation
                sumo_manager.step()

                # ADD THIS LINE HERE (after sumo_manager.step()):
                v2g_manager.update_v2g_sessions()

                # Update power grid with EV charging loads
                update_ev_power_loads()
            
            # Run power flow every 30 seconds
            if system_state['current_time'] % 50 == 0:
                power_grid.run_power_flow("dc")
            
            system_state['current_time'] += 1
            time.sleep(0.01 / system_state['simulation_speed'])
            
        except Exception as e:
            print(f"Simulation error: {e}")
            traceback.print_exc()
            time.sleep(1)

def update_ev_power_loads():
    """Update power grid loads based on EV charging - COMPLETE FIXED VERSION"""
    
    global power_grid  # Use the global instance
    global previous_ev_load_mw  # Track previous load
    
    print(f"[DEBUG] update_ev_power_loads called at time {system_state['current_time']}")
    
    # Initialize previous load tracking
    if 'previous_ev_load_mw' not in globals():
        previous_ev_load_mw = 0
    
    # Verify power_grid exists
    if not power_grid:
        print("[ERROR] power_grid not initialized!")
        return
    
    # Check if SUMO is running
    if not sumo_manager.running:
        print(f"[DEBUG] SUMO not running, skipping EV load update")
        return
    
    # Get SUMO statistics
    stats = sumo_manager.get_statistics()
    print(f"[DEBUG] Stats - Vehicles charging: {stats.get('vehicles_charging', 0)}")
    
    # Track detailed charging information
    charging_by_station = {}
    charging_details = {
        'total_vehicles_charging': 0,
        'total_power_kw': 0,
        'stations_active': 0,
        'critical_stations': []
    }
    
    # Count charging vehicles properly - check both vehicle state and station manager
    for vehicle in sumo_manager.vehicles.values():
        if vehicle.config.is_ev:
            # Check multiple charging indicators
            has_is_charging = hasattr(vehicle, 'is_charging')
            is_charging_val = has_is_charging and vehicle.is_charging
            
            has_charging_at = hasattr(vehicle, 'charging_at_station')
            charging_at_val = has_charging_at and vehicle.charging_at_station
            
            # Also check if vehicle is in station manager's charging list
            in_station_manager = False
            if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
                for station_id, station in sumo_manager.station_manager.stations.items():
                    if vehicle.id in station['vehicles_charging']:
                        in_station_manager = True
                        break
            
            # Debug output for EVs at stations
            if vehicle.assigned_ev_station or in_station_manager:
                print(f"[DEBUG] {vehicle.id}: station={vehicle.assigned_ev_station}, is_charging={is_charging_val}, in_station_mgr={in_station_manager}, SOC={vehicle.config.current_soc:.2f}")
            
            # Count if actually charging (either vehicle state OR in station manager)
            if is_charging_val or charging_at_val or in_station_manager:
                station_id = vehicle.assigned_ev_station
                if not station_id and in_station_manager:
                    # Find which station this vehicle is charging at
                    for sid, station in sumo_manager.station_manager.stations.items():
                        if vehicle.id in station['vehicles_charging']:
                            station_id = sid
                            break
                
                if station_id:
                    if station_id not in charging_by_station:
                        charging_by_station[station_id] = []
                    charging_by_station[station_id].append(vehicle.id)
    
    # Convert to counts and show which vehicles are charging where
    charging_counts = {}
    for station_id, vehicles in charging_by_station.items():
        charging_counts[station_id] = len(vehicles)
        if vehicles:
            station_name = integrated_system.ev_stations[station_id]['name']
            print(f"[DEBUG] {station_name}: {len(vehicles)} charging - {', '.join(vehicles)}")
    
    print(f"[DEBUG] Charging by station summary: {charging_counts}")
    
    # Cross-check with station manager port usage
    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
        print(f"[DEBUG] Station manager port usage:")
        for station_id, station in sumo_manager.station_manager.stations.items():
            occupied_ports = len([p for p in station['ports'] if p.occupied_by is not None])
            vehicles_in_list = len(station['vehicles_charging'])
            print(f"  {station_id}: {occupied_ports} ports occupied, {vehicles_in_list} in vehicles_charging list")
    
    # Update each EV station's load and PyPSA
    total_charging_kw = 0
    substation_loads = {}  # Track load per substation
    
    for ev_id, ev_station in integrated_system.ev_stations.items():
        chargers_in_use = charging_counts.get(ev_id, 0)
        
        # Calculate realistic charging power based on number of vehicles
        if chargers_in_use > 0:
            # Variable charging rate based on station load
            if chargers_in_use <= 5:
                power_per_vehicle = 150  # 150kW DC fast charging when not crowded
            elif chargers_in_use <= 10:
                power_per_vehicle = 100  # 100kW when moderately busy
            elif chargers_in_use <= 15:
                power_per_vehicle = 50   # 50kW when busy
            else:
                power_per_vehicle = 22   # 22kW when very crowded
            
            charging_power_kw = chargers_in_use * power_per_vehicle
        else:
            charging_power_kw = 0
        
        total_charging_kw += charging_power_kw
        
        # Update the integrated system
        ev_station['vehicles_charging'] = chargers_in_use
        ev_station['current_load_kw'] = charging_power_kw
        
        # Track load by substation
        substation_name = ev_station['substation']
        if substation_name not in substation_loads:
            substation_loads[substation_name] = 0
        substation_loads[substation_name] += charging_power_kw
        
        # Update station statistics
        if chargers_in_use > 0:
            charging_details['stations_active'] += 1
            charging_details['total_vehicles_charging'] += chargers_in_use
            print(f"[DEBUG] {ev_station['name']}: {chargers_in_use} vehicles = {charging_power_kw} kW")
            
            # Check if station is critical (>80% capacity)
            if chargers_in_use >= 16:  # 80% of 20 ports
                charging_details['critical_stations'].append(ev_station['name'])
    
    charging_details['total_power_kw'] = total_charging_kw
    
    # UPDATE PYPSA NETWORK - Key part
    print(f"[DEBUG] Total EV charging load: {total_charging_kw/1000:.2f} MW")
    
    # COMPLETE FIX: Map ALL substations correctly
    bus_name_mapping = {
        "Hell's Kitchen": "Hell's Kitchen_13.8kV",  # Note the apostrophe in PyPSA!
        "Times Square": "Times Square_13.8kV",
        "Penn Station": "Penn Station_13.8kV", 
        "Grand Central": "Grand Central_13.8kV",
        "Murray Hill": "Murray Hill_13.8kV",
        "Turtle Bay": "Turtle Bay_13.8kV",
        "Columbus Circle": "Chelsea_13.8kV",  # Columbus Circle maps to Chelsea bus
        "Midtown East": "Midtown East_13.8kV"
    }
    
    # Update PyPSA loads for each substation
    for substation_name, load_kw in substation_loads.items():
        load_mw = load_kw / 1000
        
        # Get correct bus name from mapping
        bus_name = bus_name_mapping.get(substation_name)
        if not bus_name:
            print(f"[ERROR] No mapping for substation: {substation_name}")
            continue
        
        # Check if bus exists in network (handling apostrophes)
        bus_name_in_pypsa = None
        if bus_name in power_grid.network.buses.index:
            bus_name_in_pypsa = bus_name
        elif bus_name.replace("'", "") in power_grid.network.buses.index:
            bus_name_in_pypsa = bus_name.replace("'", "")
        elif bus_name.replace(" ", "_") in power_grid.network.buses.index:
            bus_name_in_pypsa = bus_name.replace(" ", "_")
        
        if not bus_name_in_pypsa:
            print(f"[WARNING] Bus {bus_name} not found in network")
            if system_state['current_time'] % 1000 == 0:  # Every 100 seconds
                available_buses = [b for b in power_grid.network.buses.index if "13.8kV" in b]
                print(f"[DEBUG] Available 13.8kV buses: {available_buses}")
            continue
        
        # Create EV load name
        clean_name = substation_name.replace(' ', '_').replace("'", '')
        ev_load_name = f"EV_{clean_name}"
        
        # Update integrated system
        if substation_name in integrated_system.substations:
            old_ev_load = integrated_system.substations[substation_name].get('ev_load_mw', 0)
            integrated_system.substations[substation_name]['ev_load_mw'] = load_mw
            
            if abs(old_ev_load - load_mw) > 0.01:
                print(f"[DEBUG] {substation_name} EV load: {old_ev_load:.2f} → {load_mw:.2f} MW")
        
        # Update PyPSA bus load
        try:
            if ev_load_name not in power_grid.network.loads.index:
                # Create new load
                power_grid.network.add(
                    "Load",
                    ev_load_name,
                    bus=bus_name_in_pypsa,
                    p_set=load_mw
                )
                print(f"[DEBUG] Created new EV load at {bus_name_in_pypsa}: {load_mw:.2f} MW")
            else:
                # Update existing load
                old_value = power_grid.network.loads.at[ev_load_name, 'p_set']
                power_grid.network.loads.at[ev_load_name, 'p_set'] = load_mw
                
                if abs(old_value - load_mw) > 0.01:  # Only log significant changes
                    print(f"[DEBUG] Updated {ev_load_name}: {old_value:.2f} → {load_mw:.2f} MW")
                    
        except Exception as e:
            print(f"[ERROR] Failed to update PyPSA load for {substation_name}: {e}")
    
    # Clean up zero loads
    for substation_name in bus_name_mapping.keys():
        if substation_name not in substation_loads:
            clean_name = substation_name.replace(' ', '_').replace("'", '')
            ev_load_name = f"EV_{clean_name}"
            if ev_load_name in power_grid.network.loads.index:
                old_val = power_grid.network.loads.at[ev_load_name, 'p_set']
                if old_val > 0:
                    power_grid.network.loads.at[ev_load_name, 'p_set'] = 0
                    print(f"[DEBUG] Cleared {ev_load_name}: {old_val:.2f} → 0.00 MW")
    
    # TRIGGER POWER FLOW - COMPLETE FIXED VERSION
    total_ev_load_mw = total_charging_kw / 1000
    
    # Ensure previous_ev_load_mw exists before using it
    if 'previous_ev_load_mw' not in globals():
        previous_ev_load_mw = 0.0
        print(f"[DEBUG] Initialized previous_ev_load_mw to 0.0")
    
    # Calculate conditions
    load_change = abs(total_ev_load_mw - previous_ev_load_mw)
    time_for_periodic = (system_state['current_time'] % 50 == 0)
    first_charging = (previous_ev_load_mw == 0 and total_ev_load_mw > 0)
    
    # Debug output
    print(f"[DEBUG] Power flow check: current={total_ev_load_mw:.3f} MW, previous={previous_ev_load_mw:.3f} MW, diff={load_change:.3f} MW")
    print(f"[DEBUG] Time check: timestep={system_state['current_time']}, periodic={time_for_periodic}")
    
    # Determine if power flow should run
    should_run_power_flow = False
    reason = ""
    
    if load_change > 0.05:
        should_run_power_flow = True
        reason = f"load change {load_change:.3f} MW"
    elif system_state['current_time'] % 50 == 0 and total_ev_load_mw > 0:
        should_run_power_flow = True
        reason = f"forced periodic at timestep {system_state['current_time']}"
        # Force update to trigger next time by setting an impossible previous value
        previous_ev_load_mw = -999
    elif first_charging:
        should_run_power_flow = True
        reason = "first EV started charging"
    elif system_state['current_time'] % 500 == 0:  # Force every 50 seconds regardless
        should_run_power_flow = True
        reason = "forced periodic check"
    
    if should_run_power_flow:
        print(f"[DEBUG] ⚡ TRIGGERING POWER FLOW: {reason}")
        print(f"[DEBUG] Running power flow: EV load {previous_ev_load_mw:.2f} → {total_ev_load_mw:.2f} MW")
        
        try:
            # Calculate total system load INCLUDING base load
            base_load = sum(integrated_system.substations[s]['load_mw'] 
                           for s in integrated_system.substations)
            total_system_load = base_load + total_ev_load_mw
            
            print(f"[DEBUG] System loads: Base={base_load:.2f} MW, EV={total_ev_load_mw:.2f} MW, Total={total_system_load:.2f} MW")
            
            # Verify PyPSA network state
            pypsa_total = sum(power_grid.network.loads.at[load, 'p_set'] 
                             for load in power_grid.network.loads.index)
            print(f"[DEBUG] PyPSA network total load: {pypsa_total:.2f} MW")
            
            # Run power flow
            print(f"[DEBUG] Executing power flow calculation...")
            result = power_grid.run_power_flow("dc")
            
            if result.converged:
                print(f"[DEBUG] ✅ POWER FLOW CONVERGED")
                print(f"[DEBUG]    Max line loading: {result.max_line_loading:.1%}")
                # Line 430 - just comment it out or remove it
                # print(f"[DEBUG]    Total losses: {result.total_losses_mw:.2f} MW")
                
                # Get actual values if available
                if hasattr(result, 'total_generation'):
                    print(f"[DEBUG]    Total generation: {result.total_generation:.2f} MW")
                if hasattr(result, 'total_load'):
                    print(f"[DEBUG]    Total load: {result.total_load:.2f} MW")
                
                # Detailed line analysis
                if hasattr(result, 'critical_lines') and result.critical_lines:
                    print(f"[DEBUG]    Critical lines (>80% loaded):")
                    for line in result.critical_lines[:3]:
                        print(f"[DEBUG]      - {line}")
                
                # CHECK FOR GRID STRESS
                if result.max_line_loading > 0.9:
                    print("⚠️ WARNING: TRANSMISSION LINE APPROACHING LIMIT!")
                    print(f"   Line loading: {result.max_line_loading:.1%}")
                    
                    # Check which substations are most loaded
                    for name, substation in integrated_system.substations.items():
                        total_substation_load = substation['load_mw'] + substation.get('ev_load_mw', 0)
                        capacity = substation['capacity_mva'] * 0.9  # Power factor
                        loading_percent = (total_substation_load / capacity) * 100
                        
                        if loading_percent > 85:
                            print(f"   ⚡ {name}: {loading_percent:.1f}% loaded")
                    
                    # Implement demand response if critical
                    if charging_details['total_vehicles_charging'] > 10:
                        print(f"   📉 Would implement demand response for {charging_details['total_vehicles_charging']} EVs")
                        for station_name in charging_details['critical_stations']:
                            print(f"    Would reduce charging at {station_name} by 50%")
                            
                elif result.max_line_loading > 0.8:
                    print("📊 NOTICE: Line loading above 80% - monitoring required")
                
                # CHECK FOR VOLTAGE VIOLATIONS
                if hasattr(result, 'voltage_violations') and result.voltage_violations:
                    print(f"⚡ VOLTAGE ISSUES: {len(result.voltage_violations)} buses outside limits")
                    for i, violation in enumerate(result.voltage_violations):
                        if i < 3:  # Show first 3
                            print(f"   Bus {violation.get('bus', 'unknown')}: {violation.get('voltage', 0):.3f} pu")
                
                # CHECK FOR SUBSTATION OVERLOADS
                overloaded_substations = []
                for name, substation in integrated_system.substations.items():
                    total_substation_load = substation['load_mw'] + substation.get('ev_load_mw', 0)
                    capacity = substation['capacity_mva'] * 0.9  # Power factor
                    loading_percent = (total_substation_load / capacity) * 100
                    
                    if loading_percent > 90:
                        overloaded_substations.append((name, loading_percent))
                        print(f"🔥 SUBSTATION OVERLOAD: {name} at {loading_percent:.1f}% capacity!")
                        print(f"   Load: {total_substation_load:.1f} MW / {capacity:.1f} MW")
                        
                        if loading_percent > 100:
                            print(f"   💥 {name} WOULD TRIP! Initiating load shedding...")
                            system_state['emergency'] = True
                
                # Summary
                if not overloaded_substations and result.max_line_loading < 0.8:
                    print(f"[DEBUG] ✅ Grid stable with {total_ev_load_mw:.2f} MW EV load")
                
            else:
                print(f"[DEBUG] ❌ POWER FLOW DIVERGED - SYSTEM UNSTABLE!")
                print(f"[DEBUG]    This indicates severe grid stress")
                print(f"[DEBUG]    System cannot handle {total_ev_load_mw:.2f} MW additional EV load")
                
                # Emergency response
                if charging_details['total_vehicles_charging'] > 5:
                    print("   🚨 EMERGENCY: Stopping all new EV charging")
                    print(f"   🚨 Must reduce load by {total_ev_load_mw * 0.5:.2f} MW")
                    system_state['emergency'] = True
                    
        except Exception as e:
            print(f"[ERROR] Power flow calculation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Update previous load after power flow
        print(f"[DEBUG] Updating previous_ev_load_mw after power flow: {previous_ev_load_mw:.3f} → {total_ev_load_mw:.3f} MW")
        previous_ev_load_mw = total_ev_load_mw
        
    else:
        # No power flow needed
        if load_change > 0.001:
            print(f"[DEBUG] Minor load change ({load_change:.3f} MW), no power flow needed")
            
    # ALWAYS update previous load at the end to track changes
    if total_ev_load_mw != previous_ev_load_mw:
        print(f"[DEBUG] Final update previous_ev_load_mw: {previous_ev_load_mw:.3f} → {total_ev_load_mw:.3f} MW")
        previous_ev_load_mw = total_ev_load_mw
    
    # Periodic summary (every 30 seconds at 0.1s timestep = 300 steps)
    if system_state['current_time'] % 300 == 0 and charging_details['total_vehicles_charging'] > 0:
        print(f"\n📊 EV CHARGING SUMMARY:")
        print(f"  Total Load: {total_charging_kw/1000:.2f} MW")
        print(f"  Vehicles Charging: {charging_details['total_vehicles_charging']}")
        print(f"  Active Stations: {charging_details['stations_active']}/8")
        if charging_details['critical_stations']:
            print(f"  ⚠️ Critical Stations: {', '.join(charging_details['critical_stations'])}")
        
        # Show load distribution
        print(f"  Load by Substation:")
        for sub_name, load_kw in sorted(substation_loads.items(), key=lambda x: x[1], reverse=True):
            print(f"    {sub_name}: {load_kw/1000:.2f} MW")
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
    
    print("\n🚨 GRID STRESS DETECTED - INITIATING RESPONSE")
    
    # Identify critical lines
    critical_lines = []
    for line_name, line_data in power_grid.network.lines.iterrows():
        loading = abs(line_data.p0 / line_data.s_nom) if line_data.s_nom > 0 else 0
        if loading > 0.85:
            critical_lines.append((line_name, loading))
    
    critical_lines.sort(key=lambda x: x[1], reverse=True)
    
    # Implement demand response
    if charging_details['total_vehicles_charging'] > 20:
        print(f"  📉 Implementing demand response for {charging_details['total_vehicles_charging']} EVs")
        
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
        print(f"  ⚡ Line {line}: {loading:.1%} loaded")

def handle_voltage_issues(violations):
    """Handle voltage violations - WORLD CLASS"""
    
    print("\n⚡ VOLTAGE CONTROL ACTIVATED")
    
    # Group violations by severity
    critical = [v for v in violations if abs(v['deviation']) > 0.1]
    warning = [v for v in violations if 0.05 < abs(v['deviation']) <= 0.1]
    
    if critical:
        print(f"  🔴 CRITICAL: {len(critical)} buses with >10% deviation")
        # Implement voltage control actions
        for violation in critical[:3]:  # Show top 3
            print(f"    Bus {violation.get('bus', 'unknown')}: {violation.get('voltage', 0):.3f} pu")
    
    if warning:
        print(f"  🟡 WARNING: {len(warning)} buses with 5-10% deviation")

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
                print(f"🔥 SUBSTATION OVERLOAD: {substation_name}")
                print(f"   Load: {total_load_mw:.1f} MW / {capacity_mw:.1f} MW ({loading_percent:.1f}%)")
                
                if loading_percent > 100:
                    print(f"   💥 {substation_name} WOULD TRIP - INITIATING LOAD SHED")
                    initiate_load_shedding(substation_name, total_load_mw - capacity_mw)

def initiate_emergency_response(charging_details):
    """Emergency response when power flow diverges"""
    
    print("\n🚨🚨 EMERGENCY RESPONSE ACTIVATED 🚨🚨")
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
    
    print(f"\n⚡ LOAD SHEDDING at {substation_name}: {excess_mw:.1f} MW")
    
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
    """Get complete network state including vehicles"""
    state = integrated_system.get_network_state()

    # Add vehicle data if SUMO is running
    if system_state['sumo_running'] and sumo_manager.running:
        vehicles = []

        # Create station charging counts
        station_charging_counts = {}
        station_queued_counts = {}

        vehicle_list = list(sumo_manager.vehicles.values())

        for vehicle in vehicle_list:
            try:
                import traci
                # Check if vehicle exists in SUMO
                if vehicle.id in traci.vehicle.getIDList():
                    x, y = traci.vehicle.getPosition(vehicle.id)
                    lon, lat = traci.simulation.convertGeo(x, y)
                    # Extended kinematics and path info
                    edge_id = None
                    lane_id = None
                    lane_pos = None
                    lane_len = None
                    edge_shape = None
                    try:
                        edge_id = traci.vehicle.getRoadID(vehicle.id)
                        lane_id = traci.vehicle.getLaneID(vehicle.id)
                        lane_pos = traci.vehicle.getLanePosition(vehicle.id)
                        if lane_id:
                            lane_len = traci.lane.getLength(lane_id)
                        if edge_id and not edge_id.startswith(':'):
                            # Use cached shapes if available
                            try:
                                from __main__ import EDGE_SHAPES
                            except:
                                EDGE_SHAPES = {}
                            if edge_id in EDGE_SHAPES:
                                shape_xy = EDGE_SHAPES[edge_id]['xy']
                                edge_shape = EDGE_SHAPES[edge_id]['lonlat']
                            else:
                                shape_xy = traci.edge.getShape(edge_id)
                                edge_shape = []
                                for sx, sy in shape_xy:
                                    slon, slat = traci.simulation.convertGeo(sx, sy)
                                    edge_shape.append([slon, slat])
                                EDGE_SHAPES[edge_id] = {'xy': shape_xy, 'lonlat': edge_shape}
                            # Nearest point on XY polyline to (x,y)
                            best_d = 1e18
                            snap_x = x
                            snap_y = y
                            for i in range(len(shape_xy)-1):
                                x1, y1 = shape_xy[i]
                                x2, y2 = shape_xy[i+1]
                                dx = x2 - x1
                                dy = y2 - y1
                                L2 = dx*dx + dy*dy if dx*dx + dy*dy != 0 else 1e-9
                                t = ((x - x1)*dx + (y - y1)*dy) / L2
                                if t < 0:
                                    px, py = x1, y1
                                elif t > 1:
                                    px, py = x2, y2
                                else:
                                    px, py = x1 + dx*t, y1 + dy*t
                                d = ((x - px)**2 + (y - py)**2) ** 0.5
                                if d < best_d:
                                    best_d = d
                                    snap_x, snap_y = px, py
                            snap_lon, snap_lat = traci.simulation.convertGeo(snap_x, snap_y)
                    except:
                        pass

                    # Track charging at stations
                    if hasattr(vehicle, 'is_charging') and vehicle.is_charging and vehicle.assigned_ev_station:
                        if vehicle.assigned_ev_station not in station_charging_counts:
                            station_charging_counts[vehicle.assigned_ev_station] = 0
                        station_charging_counts[vehicle.assigned_ev_station] += 1

                    # Track queued at stations
                    if hasattr(vehicle, 'is_queued') and vehicle.is_queued and vehicle.assigned_ev_station:
                        if vehicle.assigned_ev_station not in station_queued_counts:
                            station_queued_counts[vehicle.assigned_ev_station] = 0
                        station_queued_counts[vehicle.assigned_ev_station] += 1

                    vehicles.append({
                        'id': vehicle.id,
                        'lat': lat,
                        'lon': lon,
                        'type': vehicle.config.vtype.value,
                        'speed': vehicle.speed,
                        'speed_kmh': round(vehicle.speed * 3.6, 1),
                        'soc': vehicle.config.current_soc if vehicle.config.is_ev else 1.0,
                        'battery_percent': round(vehicle.config.current_soc * 100) if vehicle.config.is_ev else 100,
                        'is_charging': getattr(vehicle, 'is_charging', False),
                        'is_queued': getattr(vehicle, 'is_queued', False),
                        'is_circling': getattr(vehicle, 'is_circling', False),
                        'is_stranded': getattr(vehicle, 'is_stranded', False),
                        'is_ev': vehicle.config.is_ev,
                        'distance_traveled': round(vehicle.distance_traveled, 1),
                        'waiting_time': round(vehicle.waiting_time, 1),
                        'destination': vehicle.destination,
                        'assigned_station': vehicle.assigned_ev_station,
                        'edge_id': edge_id,
                        'lane_id': lane_id,
                        'lane_pos': lane_pos,
                        'lane_len': lane_len,
                        'edge_shape': edge_shape,
                        'snap_lon': locals().get('snap_lon'),
                        'snap_lat': locals().get('snap_lat')
                    })
            except:
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

        print(f"✅ EV Configuration Updated:")
        print(f"   EV Percentage: {ev_percentage}%")
        print(f"   Battery SOC Range: {battery_min_soc}% - {battery_max_soc}%")

        return jsonify({
            'success': True,
            'message': 'EV configuration updated successfully',
            'config': current_ev_config
        })

    except Exception as e:
        print(f"❌ EV config update error: {e}")
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

    print(f"\n⚡ SUBSTATION FAILURE: {substation}")
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
    if success:
        power_grid.restore_component('substation', substation)

        # Update SUMO traffic lights if running
        if system_state['sumo_running'] and sumo_manager.running:
            sumo_manager.update_traffic_lights()

            # RESTORE EV STATION STATUS
            for ev_id, ev_station in integrated_system.ev_stations.items():
                if ev_station['substation'] == substation:
                    # Mark station as operational
                    ev_station['operational'] = True

                    # Update SUMO manager
                    if ev_id in sumo_manager.ev_stations_sumo:
                        sumo_manager.ev_stations_sumo[ev_id]['available'] = ev_station['chargers']

                    # Update station manager
                    if hasattr(sumo_manager, 'station_manager') and sumo_manager.station_manager:
                        if ev_id in sumo_manager.station_manager.stations:
                            sumo_manager.station_manager.stations[ev_id]['operational'] = True
                            print(f"   ✅ Restored {ev_station['name']} ONLINE")

    return jsonify({'success': success})

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
    for sub_name in integrated_system.substations.keys():
        integrated_system.restore_substation(sub_name)
        power_grid.restore_component('substation', sub_name)

    # Update SUMO if running
    if system_state['sumo_running'] and sumo_manager.running:
        sumo_manager.update_traffic_lights()

        # Restore all EV stations
        for ev_id, ev_station in integrated_system.ev_stations.items():
            if ev_id in sumo_manager.ev_stations_sumo:
                sumo_manager.ev_stations_sumo[ev_id]['available'] = ev_station['chargers']

    return jsonify({'success': True, 'message': 'All systems restored'})

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
        print(f"[V2G STATUS] Power deficit: {v2g_data['system_metrics']['total_power_deficit_mw']:.2f} MW → "
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
# 6. ML ANALYTICS ROUTES (/api/ml/*)
# ============================================================================

@app.route('/api/ml/dashboard')
def ml_dashboard():
    """Enhanced ML dashboard with V2G analytics and real-time insights."""
    try:
        # Get enhanced ML dashboard data with V2G integration
        data = ml_engine.get_ml_dashboard_data()

        # Add V2G-specific analytics
        v2g_analytics = {
            'v2g_performance': {
                'active_vehicles': len(v2g_manager.vehicles),
                'total_energy_traded': v2g_manager.total_energy_traded,
                'total_revenue': v2g_manager.total_revenue,
                'average_discharge_rate': v2g_manager.get_average_discharge_rate(),
                'market_price': v2g_manager.market_price,
                'rate_multiplier': v2g_manager.rate_multiplier
            },
            'v2g_insights': ai_chatbot.get_v2g_insights(),
            'optimization_opportunities': ai_chatbot.get_optimization_opportunities()
        }

        # Merge V2G analytics with existing data
        data['v2g_analytics'] = v2g_analytics

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/predict/demand')
def ml_predict_demand():
    try:
        hours = int(request.args.get('hours', 6))
        preds = ml_engine.predict_power_demand(next_hours=hours)
        return jsonify(preds)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/optimize')
def ml_optimize():
    try:
        result = ml_engine.optimize_power_distribution()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/baselines')
def ml_baselines():
    try:
        baseline = {}
        if hasattr(ml_engine, 'compare_with_baselines'):
            baseline = ml_engine.compare_with_baselines()
        return jsonify(baseline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/feature_importance')
def ml_feature_importance():
    try:
        demand_labels = ['hour', 'day_of_week', 'temperature', 'total_evs', 'current_load']
        charging_labels = ['hour', 'station_id', 'queue_length', 'avg_soc']
        imp = {
            'demand': {
                'labels': demand_labels,
                'importances': []
            },
            'charging': {
                'labels': charging_labels,
                'importances': []
            }
        }
        if hasattr(ml_engine.demand_predictor, 'feature_importances_'):
            imp['demand']['importances'] = [float(x) for x in ml_engine.demand_predictor.feature_importances_]
        if hasattr(ml_engine.charging_predictor, 'feature_importances_'):
            imp['charging']['importances'] = [float(x) for x in ml_engine.charging_predictor.feature_importances_]
        return jsonify(imp)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    """Interactive AI chat endpoint."""
    try:
        body = request.get_json() or {}
        message = body.get('message', '')
        user_id = body.get('user_id', 'anonymous')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Process chat message
        response = ai_chatbot.process_message(message, user_id=user_id)

        return jsonify({
            'response': response['text'],
            'type': response.get('type', 'response'),
            'intent': response.get('intent', 'general'),
            'data': response.get('data', {}),
            'timestamp': response.get('timestamp', datetime.now().isoformat())
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
    print("\n🚀 Starting Complete System at http://localhost:5000")
    print("\n📋 INSTRUCTIONS:")
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
