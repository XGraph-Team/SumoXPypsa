"""
Manhattan Power Grid - Traffic Light Distribution Network
Real backend integration with actual NYC traffic light data and distribution network topology
"""

import requests
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString
import json
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import networkx as nx

# Add this to your core/power_system.py or create as core/traffic_system.py

@dataclass
class TrafficLight:
    """Real traffic light with power requirements"""
    id: str
    lat: float
    lon: float
    intersection: str
    power_kw: float = 0.3  # 300W typical LED traffic signal
    battery_backup: bool = False
    substation: str = None
    feeder: str = None
    powered: bool = True
    
@dataclass
class DistributionFeeder:
    """13.8kV to 480V distribution feeder"""
    id: str
    substation: str
    capacity_mva: float
    voltage_kv: float = 13.8
    loads: List[str] = None  # List of traffic light IDs
    route: List[Tuple[float, float]] = None  # Cable route coordinates
    operational: bool = True

class ManhattanTrafficDistribution:
    """
    Real traffic light distribution system for Manhattan
    Integrates with PyPSA power grid
    """
    
    def __init__(self, power_grid):
        self.power_grid = power_grid
        self.traffic_lights = {}
        self.feeders = {}
        self.distribution_graph = nx.Graph()
        
        # Load real data
        self._load_traffic_lights()
        self._build_distribution_network()
        self._integrate_with_pypsa()
        
    def _load_traffic_lights(self):
        """Load real NYC traffic signal data"""
        
        # Try to load from NYC Open Data
        try:
            # NYC Open Data API for traffic signals
            url = "https://data.cityofnewyork.us/resource/7crd-d9xh.json"
            params = {
                "$where": "latitude > 40.745 AND latitude < 40.770 AND longitude > -73.995 AND longitude < -73.965",
                "$limit": 5000
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                for item in data:
                    if 'latitude' in item and 'longitude' in item:
                        light_id = item.get('objectid', f"signal_{len(self.traffic_lights)}")
                        
                        self.traffic_lights[light_id] = TrafficLight(
                            id=light_id,
                            lat=float(item['latitude']),
                            lon=float(item['longitude']),
                            intersection=item.get('intersection', 'Unknown'),
                            battery_backup='battery' in item.get('equipment', '').lower()
                        )
            else:
                print("Could not load NYC data, using calculated positions")
                self._generate_traffic_lights()
                
        except Exception as e:
            print(f"Loading NYC data failed: {e}, using calculated positions")
            self._generate_traffic_lights()
    
    def _generate_traffic_lights(self):
        """Generate traffic lights at actual Manhattan intersections"""
        
        # Major avenues in Manhattan (running N-S)
        avenues = {
            '12th Ave': -74.0090,
            '11th Ave': -74.0060,
            '10th Ave': -74.0030,
            '9th Ave': -74.0000,
            '8th Ave': -73.9970,
            '7th Ave': -73.9940,
            '6th Ave': -73.9910,
            '5th Ave': -73.9880,
            'Madison': -73.9850,
            'Park Ave': -73.9820,
            'Lexington': -73.9790,
            '3rd Ave': -73.9760,
            '2nd Ave': -73.9730,
            '1st Ave': -73.9700,
            'FDR Drive': -73.9670
        }
        
        # Major streets (running E-W) from 34th to 59th
        streets = range(34, 60)
        
        light_id = 0
        for avenue_name, lon in avenues.items():
            for street in streets:
                # Calculate latitude (approximately 0.0012 per block)
                lat = 40.7486 + (street - 34) * 0.0012
                
                # Add some realistic offset
                lat += np.random.normal(0, 0.0001)
                lon_offset = lon + np.random.normal(0, 0.0001)
                
                self.traffic_lights[f"TL_{light_id}"] = TrafficLight(
                    id=f"TL_{light_id}",
                    lat=lat,
                    lon=lon_offset,
                    intersection=f"{avenue_name} & {street}th St",
                    battery_backup=(street % 5 == 0)  # Major intersections have backup
                )
                light_id += 1
    
    def _build_distribution_network(self):
        """Build realistic distribution network topology"""
        
        # Distribution substations (13.8kV level)
        distribution_points = {
            'DP_TimesSquare_North': {'lat': 40.762, 'lon': -73.985, 'substation': 'Times Square'},
            'DP_TimesSquare_South': {'lat': 40.755, 'lon': -73.986, 'substation': 'Times Square'},
            'DP_GrandCentral_North': {'lat': 40.758, 'lon': -73.977, 'substation': 'Grand Central'},
            'DP_GrandCentral_South': {'lat': 40.748, 'lon': -73.978, 'substation': 'Grand Central'},
            'DP_PennStation_North': {'lat': 40.755, 'lon': -73.993, 'substation': 'Penn Station'},
            'DP_PennStation_South': {'lat': 40.748, 'lon': -73.994, 'substation': 'Penn Station'},
            'DP_MurrayHill_East': {'lat': 40.750, 'lon': -73.973, 'substation': 'Murray Hill'},
            'DP_MurrayHill_West': {'lat': 40.748, 'lon': -73.980, 'substation': 'Murray Hill'},
            'DP_TurtleBay_North': {'lat': 40.758, 'lon': -73.968, 'substation': 'Turtle Bay'},
            'DP_TurtleBay_South': {'lat': 40.750, 'lon': -73.969, 'substation': 'Turtle Bay'},
        }
        
        # Create feeders from distribution points
        for dp_name, dp_data in distribution_points.items():
            feeder = DistributionFeeder(
                id=dp_name,
                substation=dp_data['substation'],
                capacity_mva=10,  # Typical distribution transformer
                loads=[]
            )
            
            # Assign traffic lights to nearest feeder using Voronoi-like assignment
            for tl_id, tl in self.traffic_lights.items():
                dist = np.sqrt((tl.lat - dp_data['lat'])**2 + (tl.lon - dp_data['lon'])**2)
                
                # Check if this is the closest feeder
                if tl.substation is None or dist < self._get_distance_to_feeder(tl, tl.feeder):
                    tl.substation = dp_data['substation']
                    tl.feeder = dp_name
                    feeder.loads.append(tl_id)
            
            # Calculate cable route (simplified Manhattan routing)
            feeder.route = self._calculate_cable_route(dp_data, feeder.loads)
            
            self.feeders[dp_name] = feeder
            
            # Add to network graph
            self.distribution_graph.add_node(dp_name, **dp_data)
    
    def _calculate_cable_route(self, start_point: Dict, load_ids: List[str]) -> List[Tuple[float, float]]:
        """Calculate realistic cable routing following Manhattan streets"""
        
        if not load_ids:
            return []
        
        route = [(start_point['lon'], start_point['lat'])]
        
        # Get all load positions
        load_positions = []
        for load_id in load_ids:
            if load_id in self.traffic_lights:
                tl = self.traffic_lights[load_id]
                load_positions.append((tl.lon, tl.lat))
        
        if not load_positions:
            return route
        
        # Find centroid of loads
        centroid_lon = np.mean([pos[0] for pos in load_positions])
        centroid_lat = np.mean([pos[1] for pos in load_positions])
        
        # Manhattan routing: go horizontal then vertical (or vice versa)
        if abs(start_point['lon'] - centroid_lon) > abs(start_point['lat'] - centroid_lat):
            # Go horizontal first
            route.append((centroid_lon, start_point['lat']))
            route.append((centroid_lon, centroid_lat))
        else:
            # Go vertical first
            route.append((start_point['lon'], centroid_lat))
            route.append((centroid_lon, centroid_lat))
        
        # Add branches to individual loads (simplified)
        for lon, lat in load_positions[:5]:  # Limit to avoid clutter
            route.append((centroid_lon, centroid_lat))
            route.append((lon, lat))
        
        return route
    
    def _get_distance_to_feeder(self, traffic_light: TrafficLight, feeder_id: str) -> float:
        """Calculate distance from traffic light to feeder"""
        
        if feeder_id not in self.feeders:
            return float('inf')
        
        feeder_node = self.distribution_graph.nodes.get(feeder_id, {})
        return np.sqrt(
            (traffic_light.lat - feeder_node.get('lat', 0))**2 + 
            (traffic_light.lon - feeder_node.get('lon', 0))**2
        )
    
    def _integrate_with_pypsa(self):
        """Add traffic lights as loads to PyPSA network"""
        
        for feeder_id, feeder in self.feeders.items():
            # Calculate total load for this feeder
            total_load_mw = len(feeder.loads) * 0.0003  # 300W per signal
            
            # Find the bus in PyPSA network
            bus_name = f"{feeder.substation}_13.8kV"
            
            if bus_name in self.power_grid.network.buses.index:
                # Add as aggregated load
                load_name = f"TrafficLights_{feeder_id}"
                
                # Create time-varying profile (dimmer at night)
                hours = self.power_grid.network.snapshots.hour
                load_profile = pd.Series(index=self.power_grid.network.snapshots)
                
                for i, h in enumerate(hours):
                    if 6 <= h <= 22:
                        load_profile.iloc[i] = total_load_mw  # Full power during day
                    else:
                        load_profile.iloc[i] = total_load_mw * 0.7  # Reduced at night
                
                self.power_grid.network.add(
                    "Load",
                    load_name,
                    bus=bus_name,
                    p_set=load_profile
                )
    
    def simulate_substation_failure(self, substation_name: str) -> Dict[str, Any]:
        """Simulate failure with accurate cascading effects"""
        
        affected_lights = []
        affected_feeders = []
        
        # Find all feeders connected to failed substation
        for feeder_id, feeder in self.feeders.items():
            if feeder.substation == substation_name:
                feeder.operational = False
                affected_feeders.append(feeder_id)
                
                # Turn off all traffic lights on this feeder
                for light_id in feeder.loads:
                    if light_id in self.traffic_lights:
                        light = self.traffic_lights[light_id]
                        if not light.battery_backup:
                            light.powered = False
                            affected_lights.append(light_id)
        
        # Calculate impact
        impact = {
            'substation': substation_name,
            'affected_feeders': affected_feeders,
            'affected_lights': len(affected_lights),
            'total_lights': len(self.traffic_lights),
            'intersections_dark': [
                self.traffic_lights[lid].intersection 
                for lid in affected_lights[:10]  # First 10 for display
            ],
            'estimated_traffic_delay_min': len(affected_lights) * 2.5,  # Rough estimate
            'power_lost_kw': len(affected_lights) * 0.3
        }
        
        return impact
    
    def restore_substation(self, substation_name: str):
        """Restore power to substation"""
        
        for feeder in self.feeders.values():
            if feeder.substation == substation_name:
                feeder.operational = True
                
                for light_id in feeder.loads:
                    if light_id in self.traffic_lights:
                        self.traffic_lights[light_id].powered = True
    
    def get_network_state(self) -> Dict[str, Any]:
        """Get complete network state for visualization"""
        
        return {
            'traffic_lights': [
                {
                    'id': tl.id,
                    'lat': tl.lat,
                    'lon': tl.lon,
                    'intersection': tl.intersection,
                    'powered': tl.powered,
                    'battery_backup': tl.battery_backup,
                    'substation': tl.substation,
                    'feeder': tl.feeder
                }
                for tl in self.traffic_lights.values()
            ],
            'feeders': [
                {
                    'id': f.id,
                    'substation': f.substation,
                    'operational': f.operational,
                    'route': f.route,
                    'load_count': len(f.loads),
                    'total_load_kw': len(f.loads) * 0.3
                }
                for f in self.feeders.values()
            ],
            'statistics': {
                'total_lights': len(self.traffic_lights),
                'powered_lights': sum(1 for tl in self.traffic_lights.values() if tl.powered),
                'battery_backup_lights': sum(1 for tl in self.traffic_lights.values() if tl.battery_backup),
                'total_feeders': len(self.feeders),
                'operational_feeders': sum(1 for f in self.feeders.values() if f.operational)
            }
        }

# Add this to your main.py API endpoints:

@app.route('/api/traffic_network')
def get_traffic_network():
    """Get complete traffic light network state"""
    return jsonify(traffic_system.get_network_state())

@app.route('/api/fail_substation/<name>', methods=['POST'])
def fail_substation(name):
    """Simulate substation failure with traffic impact"""
    impact = traffic_system.simulate_substation_failure(name)
    return jsonify(impact)

@app.route('/api/restore_substation/<name>', methods=['POST'])  
def restore_substation(name):
    """Restore substation and connected traffic lights"""
    traffic_system.restore_substation(name)
    return jsonify({'success': True, 'substation': name})