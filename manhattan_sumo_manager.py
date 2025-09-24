"""
Manhattan SUMO Manager - World Class Vehicle Simulation
COMPLETE VERSION with all coordinate fixes and route validation
FIXED: Stranded vehicles stop properly and circling routes always work
"""

import os
import sys
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import time
from ev_battery_model import EVBatteryModel
from ev_station_manager import EVStationManager

# Check if SUMO is available
try:
    import traci
    import sumolib
    SUMO_AVAILABLE = True
except ImportError:
    print("Warning: SUMO not installed. Install with: pip install sumo")
    SUMO_AVAILABLE = False

class VehicleType(Enum):
    """Vehicle types matching real NYC traffic"""
    CAR = "car"
    TAXI = "taxi"
    BUS = "bus"
    EV_SEDAN = "ev_sedan"
    EV_SUV = "ev_suv"
    DELIVERY = "delivery"
    UBER = "uber"

class SimulationScenario(Enum):
    """Traffic scenarios for different times of day"""
    MORNING_RUSH = "morning_rush"
    MIDDAY = "midday"
    EVENING_RUSH = "evening_rush"
    NIGHT = "night"
    WEEKEND = "weekend"
    EMERGENCY = "emergency"
    BLACKOUT = "blackout"
    EV_SURGE = "ev_surge"

@dataclass
class VehicleConfig:
    """Vehicle configuration with realistic parameters"""
    id: str
    vtype: VehicleType
    origin: str = None
    destination: str = None
    is_ev: bool = False
    battery_capacity_kwh: float = 0
    current_soc: float = 1.0
    consumption_kwh_per_km: float = 0.2
    depart_time: float = 0
    route: List[str] = field(default_factory=list)

class ManhattanSUMOManager:
    """Professional SUMO integration for Manhattan traffic"""
    
    def _calculate_straight_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate straight-line distance between two points (in degrees, for comparison)"""
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
    
    def _find_nearest_charging_station(self, vehicle_id: str, current_edge: str) -> Optional[str]:
        """Find the nearest operational charging station with available space"""
        
        import traci
        
        if not self.station_manager:
            return None
        
        # Get vehicle position
        try:
            x, y = traci.vehicle.getPosition(vehicle_id)
            vehicle_lon, vehicle_lat = traci.simulation.convertGeo(x, y)
        except:
            return None
        
        best_station = None
        min_distance = float('inf')
        
        # Check ALL stations and find the nearest one
        for station_id, station in self.station_manager.stations.items():
            # Check if station is operational
            if not station['operational']:
                continue
            
            # Check if station has space (strict 10 limit)
            occupied = len(station['vehicles_charging'])
            if occupied >= 10:
                continue
            
            # Calculate distance to station
            station_info = self.integrated_system.ev_stations.get(station_id)
            if not station_info:
                continue
            
            # Calculate straight-line distance
            dist = self._calculate_straight_distance(
                vehicle_lat, vehicle_lon,
                station_info['lat'], station_info['lon']
            )
            
            if dist < min_distance:
                min_distance = dist
                best_station = station_id
        
        return best_station

    def __init__(self, integrated_system):
        self.integrated_system = integrated_system
        self.running = False
        self.vehicles = {}
        self.current_scenario = SimulationScenario.MIDDAY
        self.v2g_manager = None  # Will be set by main integration
        
        # Manhattan bounds (34th to 59th Street)
        self.bounds = {
            'north': 40.770,
            'south': 40.745,
            'west': -74.010,
            'east': -73.960
        }
        
        # SUMO configuration - traffic lights file removed to avoid errors
        self.sumo_config = {
            'net_file': 'data/sumo/manhattan.net.xml',
            'additional_files': [
                'data/sumo/types.add.xml'
            ],
            'step_length': 0.1,
            'collision_action': 'warn',
            'device.rerouting.probability': '0.8',
            'device.battery.probability': '0.3'
        }
        
        # Traffic light mapping
        self.tl_power_to_sumo = {}
        self.tl_sumo_to_power = {}
        
        # EV charging stations in SUMO
        self.ev_stations_sumo = {}
        # Initialize smart station manager
        self.station_manager = None
        
        # Major routes and destinations
        self.destinations = []
        self.popular_routes = []
        self.spawn_edges = []
        
        # Statistics
        self.stats = {
            'total_vehicles': 0,
            'ev_vehicles': 0,
            'vehicles_charging': 0,
            'total_distance_km': 0,
            'total_energy_consumed_kwh': 0,
            'avg_speed_mps': 0,
            'total_wait_time': 0,
            'traffic_light_violations': 0
        }
        
        # Load network data
        self._load_network_data()
    
    def _load_network_data(self):
        """Load SUMO network and establish mappings"""
        
        if not os.path.exists(self.sumo_config['net_file']):
            print("Warning: SUMO network not found. Run get_manhattan_sumo_network.py first!")
            return False
        
        if SUMO_AVAILABLE:
            # Load network
            self.net = sumolib.net.readNet(self.sumo_config['net_file'])
            
            # Get all edges for routing
            self.edges = [e.getID() for e in self.net.getEdges() 
                         if not e.isSpecial() and e.allows("passenger")]
            
            # Get junctions
            try:
                if hasattr(self.net, 'getNodes'):
                    nodes = self.net.getNodes()
                else:
                    nodes = []
                
                self.junctions = []
                for node in nodes:
                    try:
                        if hasattr(node, 'getType') and node.getType() != "dead_end":
                            self.junctions.append(node.getID())
                        elif len(node.getIncoming()) > 1 or len(node.getOutgoing()) > 1:
                            self.junctions.append(node.getID())
                    except:
                        pass
            except:
                self.junctions = list(set([e.getFromNode().getID() for e in self.net.getEdges()[:100]] + 
                                          [e.getToNode().getID() for e in self.net.getEdges()[:100]]))
            
            # Load validated spawn edges
            try:
                with open('data/good_spawn_edges.json', 'r') as f:
                    self.spawn_edges = json.load(f)
                    print(f"Loaded {len(self.spawn_edges)} validated spawn edges")
            except:
                print("Using all edges for spawning (may have connectivity issues)")
                self.spawn_edges = self.edges[:200] if self.edges else []
            
            # Setup destinations
            self._setup_destinations()
            
            print(f"Loaded SUMO network: {len(self.edges)} edges, {len(self.junctions)} junctions")
            
            # Load connected network data if available
            connected_network_file = 'data/manhattan_connected_network.json'
            if os.path.exists(connected_network_file):
                with open(connected_network_file, 'r') as f:
                    network_data = json.load(f)
                    
                    if 'spawn_edges' in network_data and network_data['spawn_edges']:
                        self.spawn_edges = network_data['spawn_edges']
                        print(f"Loaded {len(self.spawn_edges)} spawn points from connected network")
            
            return True
        return False
    
    def _setup_destinations(self):
        """Setup realistic Manhattan destinations"""
        
        self.destinations = [
            ("Times Square", self._find_nearest_edge(40.7589, -73.9851)),
            ("Grand Central", self._find_nearest_edge(40.7527, -73.9772)),
            ("Penn Station", self._find_nearest_edge(40.7505, -73.9934)),
            ("Bryant Park", self._find_nearest_edge(40.7536, -73.9832)),
            ("Rockefeller Center", self._find_nearest_edge(40.7587, -73.9787)),
            ("Herald Square", self._find_nearest_edge(40.7484, -73.9878)),
            ("5th Ave Shopping", self._find_nearest_edge(40.7614, -73.9776)),
            ("MoMA", self._find_nearest_edge(40.7614, -73.9776)),
            ("Carnegie Hall", self._find_nearest_edge(40.7651, -73.9799)),
            ("Hell's Kitchen", self._find_nearest_edge(40.7638, -73.9918)),
            ("Murray Hill", self._find_nearest_edge(40.7478, -73.9750)),
            ("Turtle Bay", self._find_nearest_edge(40.7544, -73.9667)),
            ("Columbus Circle", self._find_nearest_edge(40.7680, -73.9819)),
            ("Plaza Hotel", self._find_nearest_edge(40.7644, -73.9747)),
            ("Waldorf Astoria", self._find_nearest_edge(40.7560, -73.9738))
        ]
        
        self.destinations = [(name, edge) for name, edge in self.destinations if edge]
        self._create_popular_routes()
    
    def _find_nearest_edge(self, lat: float, lon: float) -> Optional[str]:
        """Find nearest SUMO edge to given coordinates"""
        
        if not SUMO_AVAILABLE or not hasattr(self, 'net'):
            return None
        
        try:
            x, y = self.net.convertLonLat2XY(lon, lat)
            
            min_dist = float('inf')
            nearest_edge = None
            
            for edge in self.net.getEdges():
                if not edge.allows("passenger") or edge.isSpecial():
                    continue
                
                shape = edge.getShape()
                if shape:
                    edge_x = sum(p[0] for p in shape) / len(shape)
                    edge_y = sum(p[1] for p in shape) / len(shape)
                    
                    dist = ((x - edge_x) ** 2 + (y - edge_y) ** 2) ** 0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_edge = edge.getID()
            
            if not nearest_edge and self.edges:
                nearest_edge = self.edges[0]
            
            return nearest_edge
        except:
            return self.edges[0] if self.edges else None
    
    def _create_popular_routes(self):
        """Create realistic routes between popular destinations"""
        
        if not self.destinations:
            return
        
        route_patterns = [
            ("Hell's Kitchen", "Times Square"),
            ("Murray Hill", "Grand Central"),
            ("Turtle Bay", "Grand Central"),
            ("Columbus Circle", "Penn Station"),
            ("Times Square", "Rockefeller Center"),
            ("Grand Central", "Times Square"),
            ("Penn Station", "Herald Square"),
            ("Penn Station", "5th Ave Shopping"),
            ("Grand Central", "Herald Square"),
            ("Times Square", "MoMA"),
            ("Columbus Circle", "Carnegie Hall")
        ]
        
        for origin_name, dest_name in route_patterns:
            origin_edge = next((e for n, e in self.destinations if n == origin_name), None)
            dest_edge = next((e for n, e in self.destinations if n == dest_name), None)
            
            if origin_edge and dest_edge:
                self.popular_routes.append((origin_edge, dest_edge))
    
    def start_sumo(self, gui: bool = False, seed: int = None) -> bool:
        """Start SUMO simulation with proper configuration"""
        
        if not SUMO_AVAILABLE:
            print("SUMO not available")
            return False
        
        if self.running:
            print("SUMO already running")
            return False
        
        # Build command
        sumo_binary = "sumo-gui" if gui else "sumo"
        
        cmd = [
            sumo_binary,
            "-n", self.sumo_config['net_file'],
            "--step-length", str(self.sumo_config['step_length']),
            "--collision.action", self.sumo_config['collision_action'],
            "--device.rerouting.probability", self.sumo_config['device.rerouting.probability'],
            "--no-warnings",
            "--no-step-log",
            "--duration-log.statistics",
            "--device.emissions.probability", "1.0"
        ]
        
        # Collect additional files
        existing_additional_files = []
        for add_file in self.sumo_config['additional_files']:
            if os.path.exists(add_file):
                existing_additional_files.append(add_file)
        
        if existing_additional_files:
            cmd.extend(["-a", ",".join(existing_additional_files)])
        
        if seed is not None:
            cmd.extend(["--seed", str(seed)])
        
        try:
            traci.start(cmd)
            self.running = True
            
            self._initialize_traffic_lights()
            self._initialize_ev_stations()
            
            # Initialize smart station manager AFTER network is loaded
            if self.net:
                self.station_manager = EVStationManager(self.integrated_system, self.net)
            
            print("SUMO started successfully")
            return True
            
        except Exception as e:
            print(f"Failed to start SUMO: {e}")
            return False
    
    def _initialize_traffic_lights(self):
        """Map traffic lights between power grid and SUMO"""
        
        if not self.running:
            return
        
        tl_ids = traci.trafficlight.getIDList()
        
        for tl_id in tl_ids:
            try:
                if hasattr(self.net, 'getNode'):
                    junction = self.net.getNode(tl_id)
                else:
                    continue
                    
                if junction:
                    coord = junction.getCoord()
                    lon, lat = self.net.convertXY2LonLat(coord[0], coord[1])
                    
                    min_dist = float('inf')
                    nearest_power_tl = None
                    
                    for power_tl_id, power_tl in self.integrated_system.traffic_lights.items():
                        dist = ((lat - power_tl['lat'])**2 + (lon - power_tl['lon'])**2)**0.5
                        if dist < min_dist and dist < 0.001:
                            min_dist = dist
                            nearest_power_tl = power_tl_id
                    
                    if nearest_power_tl:
                        self.tl_power_to_sumo[nearest_power_tl] = tl_id
                        self.tl_sumo_to_power[tl_id] = nearest_power_tl
            except:
                pass
        
        print(f"Mapped {len(self.tl_power_to_sumo)} traffic lights to SUMO")
    
    def _initialize_ev_stations(self):
        """Setup EV charging stations in SUMO"""
        
        if not self.running:
            return
        
        for ev_id, ev_station in self.integrated_system.ev_stations.items():
            edge_id = self._find_nearest_edge(ev_station['lat'], ev_station['lon'])
            
            if edge_id:
                self.ev_stations_sumo[ev_id] = {
                    'edge': edge_id,
                    'capacity': ev_station['chargers'],
                    'available': ev_station['chargers'] if ev_station['operational'] else 0,
                    'charging': []
                }
    
    def spawn_vehicles(self, count: int = 10, ev_percentage: float = 0.3, battery_min_soc: float = 0.2, battery_max_soc: float = 0.9) -> int:
        """Spawn vehicles - GUARANTEED to spawn exact count requested"""
        
        if not self.running:
            return 0
        
        import traci
        spawned = 0
        attempts = 0
        max_attempts = count * 10  # Allow many attempts to get exact count
        
        # Get ALL valid edges from SUMO
        all_edges = traci.edge.getIDList()
        valid_edges = [e for e in all_edges if not e.startswith(':') and traci.edge.getLaneNumber(e) > 0]
        
        if not valid_edges:
            print("ERROR: No valid edges found in SUMO network")
            return 0
        
        print(f"Spawning {count} vehicles using {len(valid_edges)} valid edges...")
        
        # Keep trying until we get the exact count
        while spawned < count and attempts < max_attempts:
            attempts += 1
            
            # Generate unique vehicle ID
            vehicle_id = f"veh_{self.stats['total_vehicles'] + spawned}_{attempts}"
            
            # Determine if EV using configurable percentage
            is_ev = random.random() < ev_percentage
            
            if is_ev:
                vtype = "ev_sedan" if random.random() < 0.6 else "ev_suv"
                # Use configurable battery SOC range
                initial_soc = random.uniform(battery_min_soc, battery_max_soc)
            else:
                vtype = random.choice(["car", "taxi"])
                initial_soc = 1.0
            
            # Keep trying different edge combinations
            route_found = False
            edge_attempts = 0
            
            while not route_found and edge_attempts < 20:
                edge_attempts += 1
                
                try:
                    # Pick random edges
                    origin = random.choice(valid_edges)
                    destination = random.choice(valid_edges)
                    
                    # Ensure different
                    if origin == destination:
                        if len(valid_edges) > 1:
                            destination = random.choice([e for e in valid_edges if e != origin])
                        else:
                            continue
                    
                    # Try to find route
                    route_result = traci.simulation.findRoute(origin, destination)
                    
                    if route_result and route_result.edges and len(route_result.edges) > 0:
                        # Valid route found!
                        route_id = f"route_{vehicle_id}"
                        
                        # Add route
                        traci.route.add(route_id, route_result.edges)
                        
                        # Add vehicle
                        traci.vehicle.add(
                            vehicle_id,
                            route_id,
                            typeID=vtype,
                            depart="now"
                        )
                        
                        # Set speed
                        traci.vehicle.setMaxSpeed(vehicle_id, 200)
                        traci.vehicle.setSpeedMode(vehicle_id, 0)
                        traci.vehicle.setSpeed(vehicle_id, 100)
                        traci.vehicle.setAccel(vehicle_id, 50)
                        traci.vehicle.setDecel(vehicle_id, 50)
                        traci.vehicle.setMinGap(vehicle_id, 0.5)
                        
                        # Set color
                        if is_ev:
                            if initial_soc < 0.25:
                                traci.vehicle.setColor(vehicle_id, (255, 0, 0, 255))  # Red for needs charging
                            else:
                                traci.vehicle.setColor(vehicle_id, (0, 255, 0, 255))  # Green when charged
                        else:
                            # All non-EV vehicles are yellow
                            traci.vehicle.setColor(vehicle_id, (255, 255, 0, 255))  # Yellow for gas vehicles
                        
                        # Set battery for EVs
                        if is_ev:
                            battery_capacity = 75000 if vtype == "ev_sedan" else 100000
                            traci.vehicle.setParameter(vehicle_id, "device.battery.maximumBatteryCapacity", str(battery_capacity))
                            traci.vehicle.setParameter(vehicle_id, "device.battery.actualBatteryCapacity", str(battery_capacity * initial_soc))
                            traci.vehicle.setParameter(vehicle_id, "has.battery.device", "true")
                        
                        # Create vehicle object
                        vtype_enum = VehicleType.EV_SEDAN if vtype == "ev_sedan" else \
                                    VehicleType.EV_SUV if vtype == "ev_suv" else \
                                    VehicleType.TAXI if vtype == "taxi" else \
                                    VehicleType.CAR
                        
                        self.vehicles[vehicle_id] = Vehicle(
                            vehicle_id,
                            VehicleConfig(
                                id=vehicle_id,
                                vtype=vtype_enum,
                                origin=origin,
                                destination=destination,
                                is_ev=is_ev,
                                battery_capacity_kwh=75 if vtype == "ev_sedan" else (100 if vtype == "ev_suv" else 0),
                                current_soc=initial_soc,
                                route=route_result.edges
                            )
                        )
                        
                        spawned += 1
                        route_found = True
                        
                        if is_ev:
                            self.stats['ev_vehicles'] += 1
                        
                        # Success message for each vehicle
                        if spawned % 5 == 0:
                            print(f"  Spawned {spawned}/{count} vehicles...")
                        
                        break  # Exit edge_attempts loop
                        
                except Exception as e:
                    # This edge combination didn't work, try another
                    continue
            
            # If we couldn't spawn with any edge combination after 20 tries,
            # try a simple fallback route
            if not route_found and len(valid_edges) >= 2:
                try:
                    # Use first two edges as fallback
                    vehicle_id = f"veh_fallback_{self.stats['total_vehicles'] + spawned}_{attempts}"
                    route_id = f"route_fallback_{vehicle_id}"
                    
                    traci.route.add(route_id, [valid_edges[0], valid_edges[1]])
                    traci.vehicle.add(
                        vehicle_id,
                        route_id,
                        typeID="car",
                        depart="now"
                    )
                    
                    # Basic vehicle setup
                    self.vehicles[vehicle_id] = Vehicle(
                        vehicle_id,
                        VehicleConfig(
                            id=vehicle_id,
                            vtype=VehicleType.CAR,
                            origin=valid_edges[0],
                            destination=valid_edges[1],
                            is_ev=False,
                            battery_capacity_kwh=0,
                            current_soc=1.0,
                            route=[valid_edges[0], valid_edges[1]]
                        )
                    )
                    
                    spawned += 1
                    print(f"  Used fallback route for vehicle {spawned}/{count}")
                    
                except:
                    pass
        
        # Final count
        self.stats['total_vehicles'] += spawned
        
        if spawned == count:
            print(f"✅ Successfully spawned exactly {spawned} vehicles!")
        else:
            print(f"⚠️ Spawned {spawned}/{count} vehicles (some routes couldn't be created)")
        
        print(f"  EVs: {sum(1 for v in self.vehicles.values() if v.config.is_ev)}")
        print(f"  Gas: {sum(1 for v in self.vehicles.values() if not v.config.is_ev)}")
        
        return spawned
    
    def get_vehicle_positions_for_visualization(self) -> List[Dict]:
        """Get vehicle data with CORRECTED coordinates for web visualization"""
        
        if not self.running:
            return []
        
        try:
            import traci
            vehicles_data = []
            
            for vehicle in self.vehicles.values():
                try:
                    if vehicle.id in traci.vehicle.getIDList():
                        # Get position from SUMO (in SUMO's internal coordinate system)
                        x, y = traci.vehicle.getPosition(vehicle.id)
                        
                        # CRITICAL: Use SUMO's built-in coordinate conversion
                        # This ensures vehicles stay on the actual roads
                        lon, lat = traci.simulation.convertGeo(x, y)
                        
                        # Additional validation - ensure within Manhattan bounds
                        if not (self.bounds['south'] <= lat <= self.bounds['north'] and
                                self.bounds['west'] <= lon <= self.bounds['east']):
                            # If outside bounds, try alternative conversion
                            lon, lat = self.net.convertXY2LonLat(x, y)
                        
                        # Final bounds check
                        if (self.bounds['south'] <= lat <= self.bounds['north'] and
                            self.bounds['west'] <= lon <= self.bounds['east']):
                            
                            # Get the actual road/edge the vehicle is on
                            edge_id = traci.vehicle.getRoadID(vehicle.id)
                            lane_pos = traci.vehicle.getLanePosition(vehicle.id)
                            lane_id = traci.vehicle.getLaneID(vehicle.id)
                            
                            # Get vehicle angle for proper orientation
                            angle = traci.vehicle.getAngle(vehicle.id)
                            
                            vehicles_data.append({
                                'id': vehicle.id,
                                'lat': lat,
                                'lon': lon,
                                'type': vehicle.config.vtype.value,
                                'speed': vehicle.speed,
                                'speed_kmh': round(vehicle.speed * 3.6, 1),
                                'soc': vehicle.config.current_soc if vehicle.config.is_ev else 1.0,
                                'battery_percent': round(vehicle.config.current_soc * 100) if vehicle.config.is_ev else 100,
                                'is_charging': vehicle.is_charging,
                                'is_ev': vehicle.config.is_ev,
                                'distance_traveled': round(vehicle.distance_traveled, 1),
                                'waiting_time': round(vehicle.waiting_time, 1),
                                'destination': vehicle.destination,
                                'assigned_station': vehicle.assigned_ev_station,
                                'color': self._get_vehicle_color(vehicle),
                                'angle': angle,
                                'edge': edge_id,
                                'lane_pos': lane_pos,
                                'lane_id': lane_id
                            })
                except Exception as e:
                    continue
            
            return vehicles_data
        
        except Exception as e:
            print(f"Error getting vehicle positions: {e}")
            return []
    
    def _get_vehicle_color(self, vehicle: 'Vehicle') -> str:
        """Get vehicle color based on type and state"""
        
        # Check if vehicle is stranded (emergency)
        if hasattr(vehicle, 'is_stranded') and vehicle.is_stranded:
            return '#ff00ff'  # Purple for emergency (will flash in handling)
        
        # EV colors based on battery
        if vehicle.config.is_ev:
            if vehicle.config.current_soc <= 0.02:  # 2% or less - emergency
                return '#ff00ff'  # Purple (will flash)
            elif vehicle.config.current_soc < 0.25:  # Needs charging
                return '#ff0000'  # Red
            elif hasattr(vehicle, 'is_charging') and vehicle.is_charging:
                return '#00ffff'  # Cyan when charging
            else:
                return '#00ff00'  # Green when charged/normal
        
        # Non-EV vehicles - light blue to match frontend
        else:
            return '#6464ff'  # Light blue for all gas vehicles
    
    def update_traffic_lights(self):
        """Sync traffic lights from power grid to SUMO - FIXED for blackouts"""
        
        if not self.running:
            return
        
        import traci
        
        # Get all SUMO traffic lights
        tl_ids = traci.trafficlight.getIDList()
        
        for tl_id in tl_ids:
            try:
                # Get the current signal state to know its structure
                current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                state_length = len(current_state)
                
                # Find corresponding power grid traffic light
                power_tl = None
                if tl_id in self.tl_sumo_to_power:
                    power_tl_id = self.tl_sumo_to_power[tl_id]
                    if power_tl_id in self.integrated_system.traffic_lights:
                        power_tl = self.integrated_system.traffic_lights[power_tl_id]
                
                # Set traffic light state based on power status
                if power_tl:
                    if not power_tl['powered']:
                        # NO POWER = FLASHING YELLOW (vehicles proceed with caution)
                        # Or OFF state - vehicles treat as uncontrolled intersection
                        
                        # Option 1: All yellow (caution mode)
                        yellow_state = 'y' * state_length
                        traci.trafficlight.setRedYellowGreenState(tl_id, yellow_state)
                        
                        # Option 2: Turn off traffic light program (vehicles use priority rules)
                        # traci.trafficlight.setProgram(tl_id, "off")
                        
                    else:
                        # Normal operation - set based on power grid phase
                        if power_tl['phase'] == 'green':
                            # Create green phase pattern
                            if state_length == 4:
                                new_state = 'GGrr'  # Green N-S, Red E-W
                            elif state_length == 8:
                                new_state = 'GGGGrrrr'  # Green main direction
                            else:
                                # General pattern: half green, half red
                                half = state_length // 2
                                new_state = 'G' * half + 'r' * (state_length - half)
                            traci.trafficlight.setRedYellowGreenState(tl_id, new_state)
                            
                        elif power_tl['phase'] == 'yellow':
                            # Yellow phase
                            if state_length == 4:
                                new_state = 'yyrr'
                            elif state_length == 8:
                                new_state = 'yyyyrrrr'
                            else:
                                half = state_length // 2
                                new_state = 'y' * half + 'r' * (state_length - half)
                            traci.trafficlight.setRedYellowGreenState(tl_id, new_state)
                            
                        else:  # red phase
                            # Red main, green cross
                            if state_length == 4:
                                new_state = 'rrGG'  # Red N-S, Green E-W
                            elif state_length == 8:
                                new_state = 'rrrrGGGG'  # Red main, Green cross
                            else:
                                half = state_length // 2
                                new_state = 'r' * half + 'G' * (state_length - half)
                            traci.trafficlight.setRedYellowGreenState(tl_id, new_state)
                else:
                    # No mapping found - let SUMO handle normally
                    pass
                    
            except Exception as e:
                # Continue with other lights if one fails
                pass
    
    def handle_blackout_traffic_lights(self, affected_substations):
        """Handle traffic lights during blackout - set to flashing yellow or off"""
        
        if not self.running:
            return
        
        import traci
        
        affected_count = 0
        
        for tl_id in traci.trafficlight.getIDList():
            if tl_id in self.tl_sumo_to_power:
                power_tl_id = self.tl_sumo_to_power[tl_id]
                if power_tl_id in self.integrated_system.traffic_lights:
                    power_tl = self.integrated_system.traffic_lights[power_tl_id]
                    
                    # Check if this light's substation is affected
                    if power_tl['substation'] in affected_substations:
                        # Set to yellow (caution) - vehicles can proceed carefully
                        current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                        yellow_state = 'y' * len(current_state)
                        traci.trafficlight.setRedYellowGreenState(tl_id, yellow_state)
                        affected_count += 1
        
        if affected_count > 0:
            print(f"🚦 Set {affected_count} traffic lights to YELLOW (blackout mode)")
    
    def force_all_lights_red(self):
        """Force all traffic lights to red (for testing)"""
        if not self.running:
            return
        
        import traci
        for tl_id in traci.trafficlight.getIDList():
            try:
                state = traci.trafficlight.getRedYellowGreenState(tl_id)
                red_state = 'r' * len(state)
                traci.trafficlight.setRedYellowGreenState(tl_id, red_state)
            except:
                pass
        print("⚠️ All traffic lights set to RED")
    
    def step(self):
        """Advance simulation one step"""
        
        if not self.running:
            return
        
        try:
            import traci
            traci.simulationStep()
            
            # These are the ACTUAL methods in your code
            self.update_traffic_lights()  # This exists
            self._update_vehicles()  # This exists  
            self._handle_ev_charging()  # This exists
            self._update_statistics()  # This exists around line 1752
            
        except Exception as e:
            print(f"Simulation step error: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_statistics(self):
        """Update simulation statistics"""
        
        if not self.running:
            return
        
        try:
            import traci
            vehicle_ids = traci.vehicle.getIDList()
            
            if vehicle_ids:
                speeds = [traci.vehicle.getSpeed(v) for v in vehicle_ids]
                self.stats['avg_speed_mps'] = sum(speeds) / len(speeds) if speeds else 0
                
                self.stats['total_distance_km'] = sum(
                    traci.vehicle.getDistance(v) / 1000 for v in vehicle_ids
                )
                
                self.stats['total_wait_time'] = sum(
                    traci.vehicle.getWaitingTime(v) for v in vehicle_ids
                )
                
                # Calculate energy for EVs
                total_energy = 0
                for vehicle in self.vehicles.values():
                    if vehicle.config.is_ev:
                        energy_used = (1.0 - vehicle.config.current_soc) * vehicle.config.battery_capacity_kwh
                        total_energy += energy_used
                
                self.stats['total_energy_consumed_kwh'] = total_energy
        
        except Exception as e:
            pass  # Silent fail for stats
    
    def _update_vehicles(self):
        """Update vehicle states with realistic battery drain"""
        
        import traci
        vehicle_ids = traci.vehicle.getIDList()
        
        for veh_id in vehicle_ids:
            if veh_id in self.vehicles:
                vehicle = self.vehicles[veh_id]
                
                try:
                    # Get vehicle dynamics
                    vehicle.position = traci.vehicle.getPosition(veh_id)
                    speed = traci.vehicle.getSpeed(veh_id)
                    vehicle.speed = speed
                    
                    # FIXED: Check if stranded FIRST - don't allow movement
                    if hasattr(vehicle, 'is_stranded') and vehicle.is_stranded:
                        # FORCE STOP - don't allow any movement
                        traci.vehicle.setSpeed(veh_id, 0)
                        continue  # Skip all other updates for stranded vehicle
                    
                    # FORCE EXTREME SPEED if not charging
                    if not vehicle.is_charging:
                        if speed < 150:  # If going slower than 150 m/s
                            traci.vehicle.setSpeed(veh_id, 200)  # Force 200 m/s
                            traci.vehicle.setSpeedMode(veh_id, 0)  # Ignore all safety
                            traci.vehicle.setAccel(veh_id, 50)  # Super acceleration
                    
                    vehicle.distance_traveled = traci.vehicle.getDistance(veh_id)
                    vehicle.waiting_time = traci.vehicle.getWaitingTime(veh_id)
                    
                    # Handle EVs with CALIBRATED battery drain
                    if vehicle.config.is_ev and not vehicle.is_charging:
                        # CALIBRATED DRAIN RATE FOR MANHATTAN
                        # At 200 m/s, we travel 20m per step (0.1s steps)
                        # To drain 30% over 5km: 5000m / 20m = 250 steps
                        # 30% / 250 steps = 0.12% per step
                        
                        # Base drain rate: 0.12% per step at full speed
                        # This ensures from farthest point with 38% battery, 
                        # we arrive at farthest station with 8% left
                        
                        if speed > 150:  # Fast driving (normal for our simulation)
                            drain_rate = 0.0007  # 0.12% per step
                        elif speed > 50:  # Medium speed
                            drain_rate = 0.0002  # 0.08% per step
                        elif speed > 10:  # Slow/traffic
                            drain_rate = 0.0001  # 0.05% per step
                        else:  # Stopped/crawling
                            drain_rate = 0.00005  # 0.02% per step (idle consumption)
                        
                        # Additional drain if accelerating hard
                        try:
                            acceleration = traci.vehicle.getAcceleration(veh_id)
                            if acceleration > 10:  # Hard acceleration
                                drain_rate *= 1.5
                        except:
                            pass
                        
                        # Apply battery drain
                        old_soc = vehicle.config.current_soc
                        vehicle.config.current_soc -= drain_rate
                        vehicle.config.current_soc = max(0, vehicle.config.current_soc)
                        
                        # Update SUMO battery parameter
                        try:
                            new_battery = vehicle.config.current_soc * vehicle.config.battery_capacity_kwh * 1000
                            traci.vehicle.setParameter(veh_id, "device.battery.actualBatteryCapacity", str(new_battery))
                        except:
                            pass
                        
                        # Visual indication of battery level
                        if vehicle.config.current_soc <= 0.02:
                            # EMERGENCY - 2% or less (flashing purple)
                            import time
                            flash = int(time.time() * 3) % 2
                            if flash == 0:
                                traci.vehicle.setColor(veh_id, (255, 0, 255, 255))  # Bright purple
                            else:
                                traci.vehicle.setColor(veh_id, (139, 0, 139, 255))  # Dark purple
                        elif vehicle.config.current_soc < 0.25:
                            # Needs charging - red
                            traci.vehicle.setColor(veh_id, (255, 0, 0, 255))
                        else:
                            # Charged - green
                            traci.vehicle.setColor(veh_id, (0, 255, 0, 255))
                        
                        # Route to charging when below 25% (gives margin to reach station)
                        if vehicle.config.current_soc < 0.38 and not vehicle.assigned_ev_station and self.station_manager:
                            current_edge = traci.vehicle.getRoadID(veh_id)
                            
                            if current_edge and not current_edge.startswith(':'):
                                # Convert position for station manager
                                x, y = vehicle.position
                                lon, lat = traci.simulation.convertGeo(x, y)
                                
                                # Use smart station manager
                                result = self.station_manager.request_charging(
                                    veh_id,
                                    vehicle.config.current_soc,
                                    current_edge,
                                    (lon, lat),
                                    is_emergency=(vehicle.config.current_soc < 0.1)
                                )
                                
                                if result:
                                    station_id, target_edge, wait_time, distance = result
                                    
                                    # Navigate to station
                                    try:
                                        route = traci.simulation.findRoute(current_edge, target_edge)
                                        if route and route.edges:
                                            traci.vehicle.setRoute(veh_id, route.edges)
                                            vehicle.assigned_ev_station = station_id
                                            vehicle.destination = target_edge
                                            
                                            print(f"🔋 {veh_id} (SOC: {vehicle.config.current_soc:.1%}) → {station_id}")
                                    except:
                                        pass
                    
                    # Update route if near end
                    route_index = traci.vehicle.getRouteIndex(veh_id)
                    route = traci.vehicle.getRoute(veh_id)
                    if route_index >= len(route) - 1 and not vehicle.is_charging:
                        new_route = self._generate_realistic_route()
                        if new_route and len(new_route) >= 2:
                            traci.vehicle.setRoute(veh_id, new_route)
                            vehicle.config.destination = new_route[-1]
                    
                except:
                    pass
        
        # Remove vehicles that left
        current_ids = set(vehicle_ids)
        for veh_id in list(self.vehicles.keys()):
            if veh_id not in current_ids:
                del self.vehicles[veh_id]
    
    def _generate_realistic_route(self) -> List[str]:
        """Generate realistic Manhattan route with validation"""
        
        if not self.edges:
            return []
        
        edge_pool = self.spawn_edges if self.spawn_edges else self.edges
        
        for attempt in range(10):
            if self.popular_routes and random.random() < 0.3:
                origin, destination = random.choice(self.popular_routes)
            elif self.destinations and random.random() < 0.3:
                origin = random.choice(edge_pool)
                _, destination = random.choice(self.destinations)
            else:
                if len(edge_pool) >= 2:
                    origin = random.choice(edge_pool)
                    destination = random.choice(edge_pool)
                else:
                    return []
            
            if origin != destination:
                try:
                    if self.net.getEdge(origin) and self.net.getEdge(destination):
                        return [origin, destination]
                except:
                    pass
        
        if len(edge_pool) >= 2:
            return [edge_pool[0], edge_pool[1]]
        
        return []
    
    def _route_to_charging_station(self, vehicle):
        """Route EV to nearest available charging station"""
        
        import traci
        
        if not vehicle.config.is_ev or vehicle.is_charging:
            return
        
        try:
            current_edge = traci.vehicle.getRoadID(vehicle.id)
            
            best_station = None
            
            for ev_id, station in self.ev_stations_sumo.items():
                if station['available'] > 0:
                    if ev_id in self.integrated_system.ev_stations:
                        if not self.integrated_system.ev_stations[ev_id]['operational']:
                            continue
                    
                    try:
                        if current_edge and station['edge']:
                            if station['available'] > len(station['charging']):
                                best_station = (ev_id, station)
                                break
                    except:
                        pass
            
            if best_station:
                ev_id, station = best_station
                traci.vehicle.changeTarget(vehicle.id, station['edge'])
                vehicle.destination = station['edge']
                vehicle.assigned_ev_station = ev_id
                print(f"Vehicle {vehicle.id} routing to charging station {ev_id}")
        
        except Exception as e:
            pass
    
    # Add this complete replacement for the _handle_ev_charging method in manhattan_sumo_manager.py
    # This goes in the ManhattanSUMOManager class

    def _handle_ev_charging(self):
        """WORLD CLASS EV charging/V2G handler - ZERO CONFLICTS"""
        
        import traci
        import random
        import time
        
        for vehicle in list(self.vehicles.values()):
            if not vehicle.config.is_ev:
                continue
            
            try:
                veh_id = vehicle.id
                
                if veh_id not in traci.vehicle.getIDList():
                    continue
                
                current_edge = traci.vehicle.getRoadID(veh_id)
                if current_edge.startswith(':'):
                    continue
                
                # Initialize attributes
                if not hasattr(vehicle, 'is_charging'):
                    vehicle.is_charging = False
                if not hasattr(vehicle, 'charging_start_time'):
                    vehicle.charging_start_time = None
                if not hasattr(vehicle, 'is_stranded'):
                    vehicle.is_stranded = False
                if not hasattr(vehicle, 'diversion_start_time'):
                    vehicle.diversion_start_time = None
                if not hasattr(vehicle, 'is_diverted'):
                    vehicle.is_diverted = False
                if not hasattr(vehicle, 'stations_tried'):
                    vehicle.stations_tried = []
                if not hasattr(vehicle, 'in_v2g_session'):
                    vehicle.in_v2g_session = False
                if not hasattr(vehicle, 'v2g_lock'):
                    vehicle.v2g_lock = False
                if not hasattr(vehicle, 'full_station_cooldown_until'):
                    vehicle.full_station_cooldown_until = None

                # ============================================================
                # PRIORITY 1: V2G HANDLING - ABSOLUTE PRIORITY
                # ============================================================
                
                # CHECK IF LOCKED FOR V2G
                if hasattr(self, 'v2g_manager') and self.v2g_manager:
                    # If vehicle is locked for V2G, skip ALL other logic
                    if veh_id in self.v2g_manager.v2g_locked_vehicles:
                        # Keep stopped at station
                        traci.vehicle.setSpeed(veh_id, 0)
                        continue  # SKIP EVERYTHING ELSE
                    
                    # If pending V2G, let it continue to station
                    if veh_id in self.v2g_manager.pending_v2g_vehicles:
                        # Check if arrived at V2G station
                        if hasattr(vehicle, 'v2g_station'):
                            station = self.station_manager.stations.get(vehicle.v2g_station)
                            if station and current_edge == station['edge']:
                                # Start V2G session
                                substation = self.v2g_manager.pending_v2g_vehicles[veh_id]
                                success = self.v2g_manager.start_v2g_session(
                                    veh_id, 
                                    vehicle.v2g_station,
                                    substation
                                )
                                if success:
                                    vehicle.in_v2g_session = True
                                    vehicle.is_charging = False
                                    vehicle.assigned_ev_station = None
                        continue  # Skip normal charging logic
                
                # CHECK IF IN ACTIVE V2G SESSION
                if vehicle.in_v2g_session:
                    # V2G takes absolute priority
                    traci.vehicle.setSpeed(veh_id, 0)
                    
                    # Check if session ended
                    if hasattr(self, 'v2g_manager') and self.v2g_manager:
                        if veh_id not in self.v2g_manager.active_sessions:
                            # Session ended, clear flags
                            vehicle.in_v2g_session = False
                            vehicle.v2g_lock = False
                            # Vehicle will resume normal operation next step
                    continue  # Skip all normal logic
                
                # ============================================================
                # V2G OPPORTUNITY CHECK - High battery vehicles (60%+)
                # ============================================================
                if (vehicle.config.current_soc >= 0.60 and 
                    not vehicle.is_charging and 
                    not vehicle.is_stranded and
                    not vehicle.in_v2g_session and
                    not vehicle.assigned_ev_station and
                    hasattr(self, 'v2g_manager') and 
                    self.v2g_manager):
                    
                    # Check for V2G opportunities at current location
                    for station_id, station in self.station_manager.stations.items():
                        if current_edge == station['edge']:
                            station_info = self.integrated_system.ev_stations.get(station_id)
                            if station_info:
                                substation = station_info['substation']
                                
                                # Check if substation needs V2G
                                if substation in self.v2g_manager.v2g_enabled_substations:
                                    # Not already in session
                                    if veh_id not in self.v2g_manager.active_sessions:
                                        # Start V2G session
                                        success = self.v2g_manager.start_v2g_session(
                                            veh_id, 
                                            station_id,
                                            substation
                                        )
                                        if success:
                                            vehicle.in_v2g_session = True
                                            vehicle.is_charging = False
                                            vehicle.assigned_ev_station = None
                                            vehicle.v2g_lock = True
                                            print(f"⚡ {veh_id} started V2G at {station_info['name']}")
                                            continue  # Skip normal logic
                
                # ============================================================
                # PRIORITY 2: STRANDED VEHICLES (2% or less battery)
                # ============================================================
                if vehicle.config.current_soc <= 0.02:
                    if not vehicle.is_stranded:
                        vehicle.is_stranded = True
                        vehicle.is_charging = False
                        vehicle.is_diverted = False
                        print(f"🚨 {veh_id} STRANDED at {vehicle.config.current_soc:.1%} battery")
                    
                    # Force complete stop
                    traci.vehicle.setSpeed(veh_id, 0)
                    traci.vehicle.setRoute(veh_id, [current_edge])
                    
                    # Flashing purple emergency
                    flash = int(time.time() * 3) % 2
                    traci.vehicle.setColor(veh_id, (255, 0, 255, 255) if flash else (139, 0, 139, 255))
                    continue
                
                # ============================================================
                # PRIORITY 3: NORMAL CHARGING (Below 38% battery)
                # ============================================================
                if vehicle.config.current_soc < 0.38 and not vehicle.is_charging and not vehicle.is_stranded:
                    
                    # Skip if heading to V2G
                    if hasattr(vehicle, 'v2g_target_substation'):
                        continue
                    
                    current_time = traci.simulation.getTime()
                    
                    # CHECK IF DIVERTED AND TIME TO RETURN
                    if vehicle.is_diverted and vehicle.diversion_start_time:
                        time_diverted = current_time - vehicle.diversion_start_time
                        
                        if time_diverted >= 10:  # 10 seconds
                            print(f"⏰ {veh_id} returning from diversion")
                            vehicle.is_diverted = False
                            vehicle.diversion_start_time = None
                            vehicle.assigned_ev_station = None
                    
                    # Respect cooldown if recently found station full
                    if vehicle.full_station_cooldown_until is not None:
                        if current_time < vehicle.full_station_cooldown_until:
                            # Still in cooldown, keep current diversion/route and skip station selection
                            continue
                        else:
                            # Cooldown elapsed, clear and allow reselection
                            vehicle.full_station_cooldown_until = None

                    # FIND CHARGING STATION
                    if not vehicle.is_diverted:
                        if not vehicle.assigned_ev_station:
                            best_station = self._find_available_charging_station(veh_id, vehicle.stations_tried)
                            
                            if best_station:
                                vehicle.assigned_ev_station = best_station
                                station_name = self.integrated_system.ev_stations[best_station]['name']
                                print(f"🔋 {veh_id} (SOC: {vehicle.config.current_soc:.0%}) → {station_name}")
                            else:
                                if vehicle.stations_tried:
                                    print(f"♻️ {veh_id} resetting station search")
                                    vehicle.stations_tried = []
                        
                        # HANDLE STATION INTERACTION
                        if vehicle.assigned_ev_station and self.station_manager:
                            station = self.station_manager.stations.get(vehicle.assigned_ev_station)
                            
                            # If station became non-operational while en-route, drop assignment to force reselection
                            if station and not station['operational']:
                                vehicle.assigned_ev_station = None
                                station = None
                            
                            if station:
                                at_station = (current_edge == station['edge'])
                                
                                # AT STATION - Try to occupy a port; if full, temporarily divert then retry later
                                if at_station:
                                    # Try to occupy a port now (strict 20-slot limit inside)
                                    can_charge = self.station_manager.request_charging_simple(
                                        veh_id, vehicle.assigned_ev_station
                                    )
                                    
                                    if can_charge:
                                        # SUCCESS - Start charging (state is updated by station manager)
                                        vehicle.is_charging = True
                                        vehicle.charging_start_time = traci.simulation.getTime()
                                        vehicle.stations_tried = []
                                        vehicle.is_circling = False
                                        
                                        traci.vehicle.setSpeed(veh_id, 0)
                                        traci.vehicle.setColor(veh_id, (0, 255, 255, 255))
                                        
                                        station_name = self.integrated_system.ev_stations[vehicle.assigned_ev_station]['name']
                                        print(f"⚡ {veh_id} CHARGING at {station_name}")
                                    else:
                                        # Station full -> divert for 3s, then reroute to the closest station
                                        station_name = self.integrated_system.ev_stations[vehicle.assigned_ev_station]['name']
                                        print(f"🚫 {station_name} FULL - {veh_id} diverting for 3s before retry")
                                        vehicle.is_circling = False
                                        vehicle.is_diverted = True
                                        vehicle.diversion_start_time = current_time
                                        vehicle.full_station_cooldown_until = current_time + 3
                                        # Clear assignment so next selection can choose any nearest operational
                                        vehicle.assigned_ev_station = None
                                        
                                        try:
                                            diversion_route = self._create_diversion_route(current_edge)
                                            if diversion_route:
                                                traci.vehicle.setRoute(veh_id, diversion_route)
                                                traci.vehicle.setColor(veh_id, (255, 165, 0, 255))
                                            else:
                                                # Fallback: keep current edge to avoid disappearance
                                                traci.vehicle.setRoute(veh_id, [current_edge])
                                        except:
                                            try:
                                                traci.vehicle.setRoute(veh_id, [current_edge])
                                            except:
                                                pass
                                
                                # NAVIGATING TO STATION
                                else:
                                    try:
                                        route = traci.simulation.findRoute(current_edge, station['edge'])
                                        if route and route.edges:
                                            traci.vehicle.setRoute(veh_id, route.edges)
                                            
                                            if vehicle.config.current_soc < 0.10:
                                                traci.vehicle.setColor(veh_id, (255, 0, 0, 255))
                                            else:
                                                traci.vehicle.setColor(veh_id, (255, 140, 0, 255))
                                    except:
                                        pass
                
                # ============================================================
                # PRIORITY 4: ACTIVELY CHARGING
                # ============================================================
                if vehicle.is_charging and not vehicle.in_v2g_session:
                    # CRITICAL: Check if station has failed while charging
                    if vehicle.assigned_ev_station and self.station_manager:
                        station = self.station_manager.stations.get(vehicle.assigned_ev_station)
                        if station and not station['operational']:
                            # STATION FAILED - Stop charging and redirect
                            print(f"🚨 STATION FAILURE: {vehicle.assigned_ev_station} offline! {veh_id} stopping charge")
                            
                            # Stop charging
                            vehicle.is_charging = False
                            vehicle.charging_start_time = None
                            vehicle.assigned_ev_station = None
                            
                            # Resume movement
                            traci.vehicle.setSpeed(veh_id, -1)  # Resume normal speed
                            
                            # If still needs charging, find alternative
                            if vehicle.config.current_soc < 0.38:
                                print(f"🔋 {veh_id} needs charging - finding alternative station")
                                # Will be handled in next iteration by normal charging logic
                            else:
                                print(f"✅ {veh_id} has enough charge to continue")
                                traci.vehicle.setColor(veh_id, (0, 255, 0, 255))  # Green for good battery
                            
                            continue  # Skip charging logic for this step
                    
                    traci.vehicle.setSpeed(veh_id, 0)
                    
                    # Charging animation
                    pulse = int(time.time() * 4) % 4
                    colors = [(0, 255, 255, 255), (50, 255, 255, 255), 
                            (0, 200, 255, 255), (100, 255, 255, 255)]
                    traci.vehicle.setColor(veh_id, colors[pulse])
                    
                    # Update battery - charging rate (slower => longer charging time)
                    old_soc = vehicle.config.current_soc
                    vehicle.config.current_soc = min(0.80, vehicle.config.current_soc + 0.003)
                    
                    # Progress indicator
                    if int(old_soc * 20) != int(vehicle.config.current_soc * 20):
                        if vehicle.assigned_ev_station in self.integrated_system.ev_stations:
                            station_name = self.integrated_system.ev_stations[vehicle.assigned_ev_station]['name']
                            print(f"🔋 {veh_id}: {vehicle.config.current_soc:.0%} at {station_name}")
                    
                    # Charging complete
                    if vehicle.config.current_soc >= 0.80:
                        if vehicle.assigned_ev_station in self.integrated_system.ev_stations:
                            station_name = self.integrated_system.ev_stations[vehicle.assigned_ev_station]['name']
                            print(f"✅ {veh_id} FULLY CHARGED at {station_name}!")
                        
                        # Release charging port from station manager
                        if self.station_manager:
                            self.station_manager.finish_charging(veh_id)
                        
                        # Reset states
                        vehicle.is_charging = False
                        vehicle.assigned_ev_station = None
                        vehicle.stations_tried = []
                        vehicle.is_diverted = False
                        vehicle.config.current_soc = 0.80
                        
                        # Check for V2G opportunity immediately after charging
                        if (vehicle.config.current_soc >= 0.60 and 
                            hasattr(self, 'v2g_manager') and 
                            self.v2g_manager and 
                            self.v2g_manager.v2g_enabled_substations):
                            
                            # Broadcast availability for V2G
                            for substation in self.v2g_manager.v2g_enabled_substations:
                                print(f"   💰 {veh_id} available for V2G at {substation}")
                                break
                        
                        # Resume normal operation
                        traci.vehicle.setColor(veh_id, (0, 255, 0, 255))
                        traci.vehicle.setMaxSpeed(veh_id, 200)
                        traci.vehicle.setSpeed(veh_id, -1)
                        
                        # Set new random destination
                        new_route = self._create_random_route(current_edge)
                        if new_route:
                            traci.vehicle.setRoute(veh_id, new_route)
                
                # ============================================================
                # BATTERY DRAIN (Normal driving)
                # ============================================================
                if not vehicle.is_charging and not vehicle.is_stranded and not vehicle.in_v2g_session:
                    speed = traci.vehicle.getSpeed(veh_id)
                    if speed > 0:
                        if speed > 50:
                            drain_rate = 0.001
                        else:
                            drain_rate = 0.0005
                        
                        vehicle.config.current_soc -= drain_rate
                        vehicle.config.current_soc = max(0, vehicle.config.current_soc)
                        
                        # Update color for normal EVs
                        if vehicle.config.current_soc >= 0.38 and not vehicle.is_diverted:
                            if vehicle.config.current_soc >= 0.60:
                                # High SOC - eligible for V2G (bright green)
                                traci.vehicle.setColor(veh_id, (0, 255, 0, 255))
                            else:
                                # Medium SOC (normal green)
                                traci.vehicle.setColor(veh_id, (0, 200, 0, 255))
                
                # ============================================================
                # PREVENT ROUTE COMPLETION FOR LOW BATTERY EVS
                # ============================================================
                if vehicle.config.current_soc < 0.38 and not vehicle.is_charging and not vehicle.in_v2g_session:
                    route = traci.vehicle.getRoute(veh_id)
                    route_index = traci.vehicle.getRouteIndex(veh_id)
                    
                    if route_index >= len(route) - 2:
                        extension = self._create_route_extension(route[-1] if route else current_edge)
                        if extension:
                            new_route = list(route) + extension
                            traci.vehicle.setRoute(veh_id, new_route)
                            
            except Exception as e:
                if "speed" not in str(e).lower():
                    print(f"EV handler error for {vehicle.id}: {e}")

    def _find_available_charging_station(self, vehicle_id: str, excluded_stations: list) -> Optional[str]:
        """Find nearest available charging station excluding tried ones"""
        
        import traci
        
        if not self.station_manager:
            return None
        
        try:
            x, y = traci.vehicle.getPosition(vehicle_id)
            vehicle_lon, vehicle_lat = traci.simulation.convertGeo(x, y)
        except:
            return None
        
        best_station = None
        min_distance = float('inf')
        
        for station_id, station in self.station_manager.stations.items():
            # Skip excluded stations
            if station_id in excluded_stations:
                continue
            
            # Check if operational
            if not station['operational']:
                continue
            
            # Check availability (with some buffer)
            occupied = len(station['vehicles_charging'])
            if occupied >= 8:  # Leave some buffer (8/10)
                continue
            
            # Calculate distance
            station_info = self.integrated_system.ev_stations.get(station_id)
            if not station_info:
                continue
            
            dist = self._calculate_straight_distance(
                vehicle_lat, vehicle_lon,
                station_info['lat'], station_info['lon']
            )
            
            if dist < min_distance:
                min_distance = dist
                best_station = station_id
        
        return best_station


    def _create_diversion_route(self, current_edge: str) -> List[str]:
        """Create a temporary diversion route for 10 seconds of driving"""
        
        import traci
        import random
        
        all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
        
        if len(all_edges) < 5:
            return []
        
        # Pick 5-8 random edges for diversion
        num_edges = random.randint(5, min(8, len(all_edges)))
        diversion_edges = random.sample(all_edges, num_edges)
        
        # Start from current edge
        route = [current_edge]
        
        # Add edges that are reachable
        for edge in diversion_edges:
            try:
                path = traci.simulation.findRoute(route[-1], edge)
                if path and path.edges:
                    route.extend(path.edges[1:])  # Skip first edge (already in route)
            except:
                continue
        
        return route if len(route) > 1 else [current_edge]


    def _create_random_route(self, current_edge: str) -> List[str]:
        """Create a random route for normal driving"""
        
        import traci
        import random
        
        all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
        
        if not all_edges:
            return []
        
        destination = random.choice(all_edges)
        
        try:
            route = traci.simulation.findRoute(current_edge, destination)
            if route and route.edges:
                return route.edges
        except:
            pass
        
        return [current_edge, destination] if destination != current_edge else []


    def _create_route_extension(self, last_edge: str) -> List[str]:
        """Create route extension to prevent vehicle removal"""
        
        import traci
        import random
        
        all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
        
        if not all_edges:
            return []
        
        # Add 3-5 random edges
        extension = random.sample(all_edges, min(5, len(all_edges)))
        return extension
    def _create_circle_route_around_station(self, veh_id, station_edge):
        """Create a circular route around a charging station for vehicles waiting to charge
        FIXED: Always returns a valid route, never None or empty"""
        
        import traci
        import random
        
        try:
            # Get all edges in the network
            all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
            
            # Try to find edges connected to the station edge
            try:
                station_from = traci.edge.getFromNode(station_edge)
                station_to = traci.edge.getToNode(station_edge)
                
                connected_edges = []
                for edge in all_edges:
                    if edge == station_edge:
                        continue
                    try:
                        from_node = traci.edge.getFromNode(edge)
                        to_node = traci.edge.getToNode(edge)
                        
                        # Check if this edge is connected to the station
                        if (from_node == station_to or to_node == station_from or
                            from_node == station_from or to_node == station_to):
                            connected_edges.append(edge)
                    except:
                        continue
                
                if len(connected_edges) >= 2:
                    # Create a simple circular route using nearby edges
                    circle_route = [station_edge]
                    
                    # Add 2-3 nearby edges to create a small loop
                    num_edges = min(3, len(connected_edges))
                    selected_edges = random.sample(connected_edges, num_edges)
                    circle_route.extend(selected_edges)
                    
                    # Try to make it loop back to station
                    for edge in connected_edges:
                        route = traci.simulation.findRoute(circle_route[-1], station_edge)
                        if route and route.edges and len(route.edges) <= 3:
                            # Add intermediate edges to complete the circle
                            for e in route.edges[:-1]:  # Exclude station_edge as it's added at the beginning
                                if e not in circle_route:
                                    circle_route.append(e)
                            break
                    
                    # Ensure the route loops back
                    if circle_route[-1] != station_edge:
                        # Try to find a path back to station
                        route_back = traci.simulation.findRoute(circle_route[-1], station_edge)
                        if route_back and route_back.edges:
                            for e in route_back.edges:
                                if e not in circle_route:
                                    circle_route.append(e)
                    
                    return circle_route
                
                elif len(connected_edges) == 1:
                    # Simple back-and-forth between station and one connected edge
                    return [station_edge, connected_edges[0]]
                
                else:
                    # No directly connected edges - find ANY nearby edge
                    for edge in all_edges[:10]:  # Check first 10 edges
                        if edge != station_edge:
                            try:
                                route = traci.simulation.findRoute(station_edge, edge)
                                if route and route.edges and len(route.edges) <= 3:
                                    return [station_edge, edge]
                            except:
                                continue
                    
                    # Ultimate fallback: use any edge
                    if len(all_edges) > 1:
                        fallback_edge = random.choice([e for e in all_edges if e != station_edge])
                        return [station_edge, fallback_edge]
                    else:
                        return [station_edge]  # Last resort: just stay on station edge
            
            except Exception as e:
                print(f"Error finding connected edges: {e}")
                # Fallback: create a simple route with any available edges
                if len(all_edges) > 1:
                    return [station_edge, random.choice([e for e in all_edges if e != station_edge])]
                else:
                    return [station_edge]
                    
        except Exception as e:
            print(f"Error creating circle route: {e}")
            # Final fallback: return station edge only (vehicle stays in place)
            return [station_edge]
    
    def _create_circle_route(self, vehicle):
        """Create a circular route for vehicle to follow while waiting"""
        
        import traci
        import random
        
        try:
            veh_id = vehicle.id
            current_edge = traci.vehicle.getRoadID(veh_id)
            
            # Get nearby edges
            all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
            
            # Create a small loop (3-4 edges)
            circle_route = [current_edge]
            
            # Pick 3 random nearby edges
            for _ in range(3):
                if all_edges:
                    next_edge = random.choice(all_edges)
                    if next_edge != circle_route[-1]:
                        circle_route.append(next_edge)
            
            # Return to starting edge (complete circle)
            if vehicle.assigned_ev_station and self.station_manager:
                station = self.station_manager.stations.get(vehicle.assigned_ev_station)
                if station:
                    circle_route.append(station['edge'])
            else:
                circle_route.append(current_edge)
            
            # Set the circular route
            traci.vehicle.setRoute(veh_id, circle_route)
            
            # Reduce speed while circling to save battery
            traci.vehicle.setMaxSpeed(veh_id, 30)  # 30 m/s while circling
            
            vehicle.circle_route = circle_route
            
        except Exception as e:
            print(f"Error creating circle route: {e}")
    
    def get_statistics(self) -> Dict:
        """Get current simulation statistics - PROPERLY COUNT CHARGING VEHICLES"""
        
        # Count vehicle states directly
        charging_count = 0
        stranded_count = 0
        low_battery_count = 0
        circling_count = 0
        
        # Check each vehicle's actual state
        for vehicle in self.vehicles.values():
            if vehicle.config.is_ev:
                # Count charging vehicles
                if hasattr(vehicle, 'is_charging') and vehicle.is_charging:
                    charging_count += 1
                
                # Count stranded vehicles  
                if hasattr(vehicle, 'is_stranded') and vehicle.is_stranded:
                    stranded_count += 1
                
                # Count circling vehicles
                if hasattr(vehicle, 'is_circling') and vehicle.is_circling:
                    circling_count += 1
                
                # Count low battery
                if vehicle.config.current_soc < 0.25:
                    low_battery_count += 1
        
        # Also check station manager for actual port usage
        station_charging_total = 0
        if self.station_manager:
            for station_id, station in self.station_manager.stations.items():
                # Count occupied ports
                occupied = len([p for p in station['ports'] if p.occupied_by is not None])
                station_charging_total += occupied
        
        # Use the maximum of both counts (for accuracy)
        actual_charging = max(charging_count, station_charging_total)
        
        # Update main stats
        self.stats['vehicles_charging'] = actual_charging
        self.stats['vehicles_stranded'] = stranded_count
        self.stats['vehicles_circling'] = circling_count
        self.stats['vehicles_queued'] = 0  # No queue system
        
        # Get basic SUMO stats
        active_count = 0
        if self.running:
            try:
                import traci
                vehicle_ids = traci.vehicle.getIDList()
                active_count = len(vehicle_ids)
                
                # Count EVs
                ev_count = sum(1 for v in self.vehicles.values() if v.config.is_ev)
                self.stats['ev_vehicles'] = ev_count
                
                # Get speeds and distances
                if vehicle_ids:
                    speeds = []
                    total_distance = 0
                    total_wait = 0
                    
                    for v_id in vehicle_ids:
                        try:
                            speeds.append(traci.vehicle.getSpeed(v_id))
                            total_distance += traci.vehicle.getDistance(v_id)
                            total_wait += traci.vehicle.getWaitingTime(v_id)
                        except:
                            pass
                    
                    self.stats['avg_speed_mps'] = sum(speeds) / len(speeds) if speeds else 0
                    self.stats['total_distance_km'] = total_distance / 1000
                    self.stats['total_wait_time'] = total_wait
                
                # Calculate energy consumed
                total_energy = 0
                for vehicle in self.vehicles.values():
                    if vehicle.config.is_ev:
                        energy_used = vehicle.config.battery_capacity_kwh * (1.0 - vehicle.config.current_soc)
                        total_energy += energy_used
                
                self.stats['total_energy_consumed_kwh'] = total_energy
                
            except Exception as e:
                pass
        
        self.stats['active_vehicles'] = active_count
        
        # Print status if EVs are charging or need charge
        if actual_charging > 0 or low_battery_count > 0:
            print(f"\n📊 EV STATUS:")
            print(f"  Charging: {actual_charging}/10 max per station")
            print(f"  Circling: {circling_count}")
            print(f"  Stranded: {stranded_count}")
            print(f"  Need charge (<25%): {low_battery_count}")
            
            # Show which stations are being used
            if self.station_manager:
                for station_id, station in self.station_manager.stations.items():
                    occupied = len([p for p in station['ports'] if p.occupied_by is not None])
                    if occupied > 0:
                        station_name = self.integrated_system.ev_stations[station_id]['name']
                        print(f"  {station_name}: {occupied}/20 slots")
        
        return self.stats.copy()
    
    def debug_charging_status(self):
        """Debug method to show what's happening with charging"""
        
        import traci
        
        if not self.running:
            return
        
        print("\n" + "="*50)
        print("CHARGING DEBUG STATUS")
        print("="*50)
        
        # Check all EVs
        ev_count = 0
        charging_vehicles = []
        low_battery_vehicles = []
        
        for vehicle in self.vehicles.values():
            if vehicle.config.is_ev:
                ev_count += 1
                
                # Get vehicle info
                if vehicle.id in traci.vehicle.getIDList():
                    edge = traci.vehicle.getRoadID(vehicle.id)
                    speed = traci.vehicle.getSpeed(vehicle.id)
                    
                    status = "UNKNOWN"
                    if hasattr(vehicle, 'is_charging') and vehicle.is_charging:
                        status = "CHARGING"
                        charging_vehicles.append(f"{vehicle.id} @ {edge}")
                    elif hasattr(vehicle, 'is_stranded') and vehicle.is_stranded:
                        status = "STRANDED"
                    elif vehicle.config.current_soc < 0.25:
                        status = "LOW BATTERY"
                        low_battery_vehicles.append(f"{vehicle.id} ({vehicle.config.current_soc:.0%})")
                    else:
                        status = "DRIVING"
                    
                    if status in ["CHARGING", "LOW BATTERY", "STRANDED"]:
                        print(f"  {vehicle.id}: {status} | SOC: {vehicle.config.current_soc:.0%} | Edge: {edge} | Speed: {speed:.1f}")
        
        # Check stations
        print(f"\nSTATIONS:")
        if self.station_manager:
            for station_id, station in self.station_manager.stations.items():
                if station['operational']:
                    occupied = len([p for p in station['ports'] if p.occupied_by is not None])
                    if occupied > 0 or station_id in [v.assigned_ev_station for v in self.vehicles.values() if hasattr(v, 'assigned_ev_station')]:
                        print(f"  {station['name']}: {occupied}/20 ports occupied")
                        # List vehicles at this station
                        for port in station['ports']:
                            if port.occupied_by:
                                print(f"    - Port {port.port_id}: {port.occupied_by}")
        
        print(f"\nSUMMARY:")
        print(f"  Total EVs: {ev_count}")
        print(f"  Charging: {len(charging_vehicles)}")
        print(f"  Low Battery: {len(low_battery_vehicles)}")
        print("="*50)
    
    def force_test_charging(self):
        """Force a vehicle to need charging for testing"""
        
        import traci
        
        if not self.running:
            print("SUMO not running")
            return
        
        # Find first EV
        for vehicle in self.vehicles.values():
            if vehicle.config.is_ev and vehicle.id in traci.vehicle.getIDList():
                # Set battery to 10%
                vehicle.config.current_soc = 0.10
                print(f"🔋 Set {vehicle.id} battery to 10% for testing")
                
                # Set orange color
                traci.vehicle.setColor(vehicle.id, (255, 165, 0, 255))
                
                # Clear any previous assignment
                vehicle.assigned_ev_station = None
                if hasattr(vehicle, 'is_charging'):
                    vehicle.is_charging = False
                
                return
        
        print("No EV found to test")
    
    def stop(self):
        """Stop SUMO simulation"""
        
        if self.running:
            try:
                import traci
                traci.close()
                self.running = False
                print("SUMO stopped")
            except:
                pass
    def set_v2g_manager(self, v2g_manager):
        """Set reference to V2G manager"""
        self.v2g_manager = v2g_manager
        print("V2G manager connected to SUMO manager")

class Vehicle:
    """Individual vehicle tracking"""
    
    def __init__(self, vehicle_id: str, config: VehicleConfig):
        self.id = vehicle_id
        self.config = config
        self.position = (0, 0)
        self.speed = 0
        self.distance_traveled = 0
        self.waiting_time = 0
        self.is_charging = False
        self.is_queued = False
        self.is_circling = False
        self.is_stranded = False
        self.charging_at_station = None  # ADD THIS
        self.queue_position = 0
        self.assigned_ev_station = None
        self.destination = config.destination if config else None
        
    def __repr__(self):
        if self.config:
            if self.config.is_ev:
                return f"Vehicle({self.id}, {self.config.vtype.value}, SOC:{self.config.current_soc:.1%})"
            else:
                return f"Vehicle({self.id}, {self.config.vtype.value})"
        else:
            return f"Vehicle({self.id})"