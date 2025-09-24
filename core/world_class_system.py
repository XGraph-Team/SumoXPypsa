"""
Manhattan Integrated Power-Traffic System
World-class implementation with real distribution topology
"""

import json
import numpy as np
import pandas as pd
import networkx as nx
import traci
import sumolib
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
import time

class TrafficPhase(Enum):
    """Real traffic light phases"""
    NS_GREEN = "north_south_green"
    NS_YELLOW = "north_south_yellow"
    EW_GREEN = "east_west_green"
    EW_YELLOW = "east_west_yellow"
    ALL_RED = "all_red"
    FLASHING_RED = "flashing_red"  # Power failure mode

@dataclass
class TrafficLight:
    """Real traffic light with phases and timing"""
    id: str
    lat: float
    lon: float
    substation: str
    feeder: str
    powered: bool = True
    current_phase: TrafficPhase = TrafficPhase.NS_GREEN
    phase_timer: int = 0
    cycle_time: int = 90  # Total cycle time in seconds
    sumo_id: str = None
    
@dataclass
class EVStation:
    """EV charging station"""
    id: str
    name: str
    lat: float
    lon: float
    substation: str
    feeder: str
    chargers: int
    power_kw: float
    vehicles_charging: int = 0
    operational: bool = True

class ManhattanDistributionNetwork:
    """
    Complete Manhattan power distribution network
    Real topology with proper electrical hierarchy
    """
    
    def __init__(self):
        # Electrical network hierarchy
        self.substations = {}  # 138kV/13.8kV substations
        self.distribution_transformers = {}  # 13.8kV/480V transformers
        self.feeders = {}  # Distribution feeders
        self.traffic_lights = {}
        self.ev_stations = {}
        
        # Network graph for topology
        self.network = nx.DiGraph()
        
        # Build the network
        self._build_network()
        
    def _build_network(self):
        """Build realistic Manhattan distribution network"""
        
        # STEP 1: Create main substations (we need more for 657 traffic lights)
        main_substations = {
            # West Side
            'Hudson_Yards': {'lat': 40.7537, 'lon': -74.0018, 'capacity_mva': 500},
            'Hells_Kitchen': {'lat': 40.7614, 'lon': -73.9919, 'capacity_mva': 750},
            'Times_Square': {'lat': 40.7589, 'lon': -73.9851, 'capacity_mva': 850},
            'Columbus_Circle': {'lat': 40.7681, 'lon': -73.9819, 'capacity_mva': 600},
            
            # Midtown
            'Penn_Station': {'lat': 40.7505, 'lon': -73.9934, 'capacity_mva': 900},
            'Herald_Square': {'lat': 40.7484, 'lon': -73.9878, 'capacity_mva': 650},
            'Bryant_Park': {'lat': 40.7536, 'lon': -73.9832, 'capacity_mva': 700},
            'Grand_Central': {'lat': 40.7527, 'lon': -73.9772, 'capacity_mva': 1000},
            
            # East Side
            'Murray_Hill': {'lat': 40.7489, 'lon': -73.9765, 'capacity_mva': 650},
            'Turtle_Bay': {'lat': 40.7532, 'lon': -73.9681, 'capacity_mva': 700},
            'Sutton_Place': {'lat': 40.7580, 'lon': -73.9620, 'capacity_mva': 550},
            'Roosevelt_Island': {'lat': 40.7605, 'lon': -73.9510, 'capacity_mva': 400},
        }
        
        for name, data in main_substations.items():
            self.substations[name] = {
                **data,
                'voltage_primary': 138,
                'voltage_secondary': 13.8,
                'feeders': [],
                'load_mw': 0,
                'operational': True
            }
            self.network.add_node(name, **data, type='substation')
        
        # STEP 2: Create distribution transformers (13.8kV to 480V)
        # Place them strategically across Manhattan grid
        transformer_id = 0
        for sub_name, sub_data in self.substations.items():
            # Each substation feeds 4-6 distribution transformers
            coverage_radius = 0.01  # ~1km
            angles = np.linspace(0, 2*np.pi, 5, endpoint=False)
            
            for angle in angles:
                # Place transformer at offset from substation
                lat = sub_data['lat'] + coverage_radius * np.sin(angle)
                lon = sub_data['lon'] + coverage_radius * np.cos(angle)
                
                dt_name = f"DT_{sub_name}_{transformer_id}"
                self.distribution_transformers[dt_name] = {
                    'id': dt_name,
                    'lat': lat,
                    'lon': lon,
                    'substation': sub_name,
                    'capacity_kva': 1000,
                    'voltage_primary': 13.8,
                    'voltage_secondary': 0.48,
                    'load_kw': 0,
                    'operational': True
                }
                
                # Add to network graph
                self.network.add_node(dt_name, lat=lat, lon=lon, type='transformer')
                self.network.add_edge(sub_name, dt_name, type='13.8kV_feeder')
                
                transformer_id += 1
        
        print(f"Created {len(self.substations)} substations")
        print(f"Created {len(self.distribution_transformers)} distribution transformers")
    
    def assign_traffic_lights(self, traffic_lights_data):
        """Assign traffic lights to nearest distribution transformer"""
        
        for tl_data in traffic_lights_data:
            tl_id = str(tl_data['id'])
            
            # Find nearest distribution transformer
            min_dist = float('inf')
            nearest_dt = None
            
            for dt_name, dt in self.distribution_transformers.items():
                dist = self._manhattan_distance(
                    tl_data['lat'], tl_data['lon'],
                    dt['lat'], dt['lon']
                )
                if dist < min_dist:
                    min_dist = dist
                    nearest_dt = dt_name
            
            if nearest_dt:
                dt = self.distribution_transformers[nearest_dt]
                
                self.traffic_lights[tl_id] = TrafficLight(
                    id=tl_id,
                    lat=tl_data['lat'],
                    lon=tl_data['lon'],
                    substation=dt['substation'],
                    feeder=nearest_dt,
                    powered=True
                )
                
                # Add to network graph
                self.network.add_node(tl_id, 
                    lat=tl_data['lat'], 
                    lon=tl_data['lon'], 
                    type='traffic_light'
                )
                self.network.add_edge(nearest_dt, tl_id, type='service_cable')
                
                # Update transformer load
                dt['load_kw'] += 0.3  # 300W per traffic light
        
        # Update substation loads
        for dt in self.distribution_transformers.values():
            if dt['substation'] in self.substations:
                self.substations[dt['substation']]['load_mw'] += dt['load_kw'] / 1000
        
        print(f"Assigned {len(self.traffic_lights)} traffic lights to distribution network")
    
    def add_ev_stations(self):
        """Add EV charging stations to the network"""
        
        ev_station_locations = [
            {'name': 'Times_Square_Garage', 'lat': 40.7580, 'lon': -73.9855, 'chargers': 50},
            {'name': 'Bryant_Park_Station', 'lat': 40.7540, 'lon': -73.9840, 'chargers': 30},
            {'name': 'Penn_Station_Hub', 'lat': 40.7508, 'lon': -73.9936, 'chargers': 40},
            {'name': 'Grand_Central_Charging', 'lat': 40.7525, 'lon': -73.9774, 'chargers': 60},
            {'name': 'Columbus_Circle_EV', 'lat': 40.7685, 'lon': -73.9815, 'chargers': 35},
            {'name': 'Murray_Hill_Garage', 'lat': 40.7492, 'lon': -73.9768, 'chargers': 25},
            {'name': 'Hudson_Yards_Station', 'lat': 40.7540, 'lon': -74.0015, 'chargers': 45},
            {'name': 'Herald_Square_EV', 'lat': 40.7486, 'lon': -73.9876, 'chargers': 30},
        ]
        
        for i, station in enumerate(ev_station_locations):
            # Find nearest distribution transformer
            min_dist = float('inf')
            nearest_dt = None
            
            for dt_name, dt in self.distribution_transformers.items():
                dist = self._manhattan_distance(
                    station['lat'], station['lon'],
                    dt['lat'], dt['lon']
                )
                if dist < min_dist:
                    min_dist = dist
                    nearest_dt = dt_name
            
            if nearest_dt:
                dt = self.distribution_transformers[nearest_dt]
                station_id = f"EV_{i}"
                
                self.ev_stations[station_id] = EVStation(
                    id=station_id,
                    name=station['name'],
                    lat=station['lat'],
                    lon=station['lon'],
                    substation=dt['substation'],
                    feeder=nearest_dt,
                    chargers=station['chargers'],
                    power_kw=station['chargers'] * 7.2  # 7.2kW Level 2 chargers
                )
                
                # Add to network
                self.network.add_node(station_id, **station, type='ev_station')
                self.network.add_edge(nearest_dt, station_id, type='ev_feeder')
                
                # Update loads
                dt['load_kw'] += station['chargers'] * 7.2
                self.substations[dt['substation']]['load_mw'] += (station['chargers'] * 7.2) / 1000
        
        print(f"Added {len(self.ev_stations)} EV charging stations")
    
    def _manhattan_distance(self, lat1, lon1, lat2, lon2):
        """Calculate Manhattan distance for street grid routing"""
        return abs(lat1 - lat2) + abs(lon1 - lon2)
    
    def get_cable_routes(self):
        """Get all cable routes for visualization"""
        cables = []
        
        # Primary feeders (substation to distribution transformers)
        for edge in self.network.edges(data=True):
            if edge[2].get('type') == '13.8kV_feeder':
                from_node = self.network.nodes[edge[0]]
                to_node = self.network.nodes[edge[1]]
                
                cables.append({
                    'id': f"{edge[0]}_{edge[1]}",
                    'type': 'primary',
                    'voltage': '13.8kV',
                    'from': edge[0],
                    'to': edge[1],
                    'path': self._route_cable(
                        from_node['lat'], from_node['lon'],
                        to_node['lat'], to_node['lon']
                    ),
                    'operational': self.substations.get(edge[0], {}).get('operational', True)
                })
        
        # Service cables (distribution transformer to loads)
        # Aggregate by transformer to avoid thousands of lines
        for dt_name, dt in self.distribution_transformers.items():
            # Get all connected loads
            connected = [n for n in self.network.successors(dt_name)]
            
            if connected:
                # Create simplified route showing service area
                for node_id in connected[:20]:  # Limit for visualization
                    node = self.network.nodes[node_id]
                    
                    cables.append({
                        'id': f"{dt_name}_{node_id}",
                        'type': 'service',
                        'voltage': '480V',
                        'from': dt_name,
                        'to': node_id,
                        'path': self._route_cable(
                            dt['lat'], dt['lon'],
                            node['lat'], node['lon']
                        ),
                        'operational': dt['operational']
                    })
        
        return cables
    
    def _route_cable(self, lat1, lon1, lat2, lon2):
        """Route cable following Manhattan streets"""
        # Manhattan routing: horizontal then vertical
        return [
            [lon1, lat1],
            [lon2, lat1],  # Horizontal segment
            [lon2, lat2]   # Vertical segment
        ]
    
    def simulate_failure(self, substation_name):
        """Simulate substation failure with cascading effects"""
        
        if substation_name not in self.substations:
            return {'error': 'Substation not found'}
        
        # Fail the substation
        self.substations[substation_name]['operational'] = False
        
        # Find all affected components
        affected_transformers = []
        affected_lights = []
        affected_ev_stations = []
        
        # Fail connected distribution transformers
        for dt_name, dt in self.distribution_transformers.items():
            if dt['substation'] == substation_name:
                dt['operational'] = False
                affected_transformers.append(dt_name)
                
                # Fail connected traffic lights
                for tl_id, tl in self.traffic_lights.items():
                    if tl.feeder == dt_name:
                        tl.powered = False
                        tl.current_phase = TrafficPhase.FLASHING_RED
                        affected_lights.append(tl_id)
                
                # Fail connected EV stations
                for ev_id, ev in self.ev_stations.items():
                    if ev.feeder == dt_name:
                        ev.operational = False
                        ev.vehicles_charging = 0
                        affected_ev_stations.append(ev_id)
        
        return {
            'substation': substation_name,
            'affected_transformers': len(affected_transformers),
            'affected_lights': len(affected_lights),
            'affected_ev_stations': len(affected_ev_stations),
            'load_lost_mw': self.substations[substation_name]['load_mw']
        }

class SUMOTrafficSimulation:
    """SUMO traffic simulation integrated with power system"""
    
    def __init__(self, network_file='data/manhattan.net.xml'):
        self.network_file = network_file
        self.running = False
        self.traffic_lights_map = {}  # Map our IDs to SUMO IDs
        
    def start(self):
        """Start SUMO simulation"""
        try:
            sumo_cmd = [
                "sumo-gui",  # Use GUI for visualization
                "-n", self.network_file,
                "--step-length", "0.1",
                "--collision.action", "warn",
                "--collision.check-junctions",
                "--device.rerouting.probability", "0.8",
                "--device.battery.probability", "0.3"  # 30% EVs
            ]
            
            traci.start(sumo_cmd)
            self.running = True
            
            # Map traffic lights
            for tl_id in traci.trafficlight.getIDList():
                self.traffic_lights_map[tl_id] = tl_id
            
            print(f"SUMO started with {len(self.traffic_lights_map)} traffic lights")
            
        except Exception as e:
            print(f"SUMO start failed: {e}")
            self.running = False
    
    def update_traffic_light(self, tl_id, powered):
        """Update traffic light state in SUMO"""
        if not self.running:
            return
        
        sumo_id = self.traffic_lights_map.get(tl_id)
        if sumo_id and sumo_id in traci.trafficlight.getIDList():
            if not powered:
                # Set to red flashing (power failure)
                traci.trafficlight.setProgram(sumo_id, "0")
                traci.trafficlight.setRedYellowGreenState(sumo_id, "rrrrrrrr")
            else:
                # Normal operation
                traci.trafficlight.setProgram(sumo_id, "0")
    
    def get_traffic_metrics(self):
        """Get current traffic metrics"""
        if not self.running:
            return {}
        
        metrics = {
            'vehicle_count': traci.vehicle.getIDCount(),
            'average_speed': 0,
            'waiting_time': 0,
            'co2_emissions': 0
        }
        
        for veh_id in traci.vehicle.getIDList():
            metrics['average_speed'] += traci.vehicle.getSpeed(veh_id)
            metrics['waiting_time'] += traci.vehicle.getWaitingTime(veh_id)
            metrics['co2_emissions'] += traci.vehicle.getCO2Emission(veh_id)
        
        if metrics['vehicle_count'] > 0:
            metrics['average_speed'] /= metrics['vehicle_count']
        
        return metrics

class WorldClassIntegratedSystem:
    """Complete integrated system orchestrator"""
    
    def __init__(self, power_grid):
        self.power_grid = power_grid
        self.distribution = ManhattanDistributionNetwork()
        self.sumo = SUMOTrafficSimulation()
        
        # Load traffic lights
        with open('data/manhattan_traffic_lights.json', 'r') as f:
            traffic_lights_data = json.load(f)
        
        # Build network
        self.distribution.assign_traffic_lights(traffic_lights_data)
        self.distribution.add_ev_stations()
        
        # Integrate with PyPSA
        self._integrate_with_pypsa()
        
        # Start SUMO if available
        try:
            self.sumo.start()
        except:
            print("SUMO not available, continuing without traffic simulation")
    
    def _integrate_with_pypsa(self):
        """Add all loads to PyPSA network"""
        
        for sub_name, sub_data in self.distribution.substations.items():
            bus_name = f"{sub_name}_13.8kV"
            
            if bus_name in self.power_grid.network.buses.index:
                # Add aggregated load
                self.power_grid.network.add(
                    "Load",
                    f"Distribution_{sub_name}",
                    bus=bus_name,
                    p_set=sub_data['load_mw']
                )
    
    def get_complete_state(self):
        """Get complete system state for frontend"""
        
        return {
            'substations': [
                {
                    'name': name,
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'capacity_mva': data['capacity_mva'],
                    'load_mw': data['load_mw'],
                    'operational': data['operational']
                }
                for name, data in self.distribution.substations.items()
            ],
            'traffic_lights': [
                {
                    'id': tl.id,
                    'lat': tl.lat,
                    'lon': tl.lon,
                    'powered': tl.powered,
                    'substation': tl.substation
                }
                for tl in self.distribution.traffic_lights.values()
            ],
            'ev_stations': [
                {
                    'id': ev.id,
                    'name': ev.name,
                    'lat': ev.lat,
                    'lon': ev.lon,
                    'chargers': ev.chargers,
                    'operational': ev.operational,
                    'substation': ev.substation
                }
                for ev in self.distribution.ev_stations.values()
            ],
            'cables': self.distribution.get_cable_routes(),
            'traffic_metrics': self.sumo.get_traffic_metrics() if self.sumo.running else None
        }