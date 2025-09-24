"""
Professional Integrated Power-Traffic System
Real traffic lights, real positions, real logic
"""

import json
import numpy as np
from typing import Dict, List, Tuple
import os

class IntegratedBackend:
    """
    Integrates:
    1. Real traffic light positions from OSM
    2. Power distribution network
    3. Traffic simulation ready for SUMO
    """
    
    def __init__(self, power_grid):
        self.power_grid = power_grid
        self.traffic_lights = {}
        self.distribution_feeders = {}
        self.cables = []
        
        # Load real traffic lights
        self._load_traffic_lights()
        
        # Build distribution network
        self._build_distribution_network()
        
        # Integrate with PyPSA
        self._integrate_with_power_grid()
        
    def _load_traffic_lights(self):
        """Load real traffic light positions"""
        
        if not os.path.exists('data/manhattan_traffic_lights.json'):
            print("Traffic light data not found. Run get_traffic_lights_osm.py first")
            return
        
        with open('data/manhattan_traffic_lights.json', 'r') as f:
            lights = json.load(f)
        
        for light in lights:
            self.traffic_lights[light['id']] = {
                'id': light['id'],
                'lat': light['lat'],
                'lon': light['lon'],
                'powered': True,
                'substation': None,
                'feeder': None,
                'cable_path': []
            }
        
        print(f"Loaded {len(self.traffic_lights)} traffic lights")
    
    def _build_distribution_network(self):
        """Build realistic power distribution network"""
        
        # Define distribution transformers (where 13.8kV becomes 480V for traffic lights)
        distribution_points = {
            # Times Square area
            'DP_TS_42_7th': {'lat': 40.7560, 'lon': -73.9855, 'substation': 'Times Square'},
            'DP_TS_47_Broadway': {'lat': 40.7595, 'lon': -73.9845, 'substation': 'Times Square'},
            
            # Grand Central area  
            'DP_GC_42_Lex': {'lat': 40.7519, 'lon': -73.9763, 'substation': 'Grand Central'},
            'DP_GC_45_Park': {'lat': 40.7541, 'lon': -73.9750, 'substation': 'Grand Central'},
            
            # Penn Station area
            'DP_PS_34_8th': {'lat': 40.7505, 'lon': -73.9910, 'substation': 'Penn Station'},
            'DP_PS_38_7th': {'lat': 40.7530, 'lon': -73.9895, 'substation': 'Penn Station'},
            
            # Murray Hill area
            'DP_MH_36_Mad': {'lat': 40.7495, 'lon': -73.9820, 'substation': 'Murray Hill'},
            'DP_MH_40_3rd': {'lat': 40.7515, 'lon': -73.9750, 'substation': 'Murray Hill'},
        }
        
        # Assign each traffic light to nearest distribution point
        for tl_id, tl in self.traffic_lights.items():
            min_dist = float('inf')
            nearest_dp = None
            nearest_sub = None
            
            for dp_name, dp in distribution_points.items():
                dist = self._calculate_distance(tl['lat'], tl['lon'], dp['lat'], dp['lon'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_dp = dp_name
                    nearest_sub = dp['substation']
            
            tl['feeder'] = nearest_dp
            tl['substation'] = nearest_sub
            
            # Create cable path (Manhattan grid routing)
            if nearest_dp:
                dp = distribution_points[nearest_dp]
                tl['cable_path'] = self._manhattan_routing(
                    dp['lat'], dp['lon'],
                    tl['lat'], tl['lon']
                )
        
        # Create feeder objects
        for dp_name, dp in distribution_points.items():
            connected_lights = [
                tl_id for tl_id, tl in self.traffic_lights.items()
                if tl['feeder'] == dp_name
            ]
            
            self.distribution_feeders[dp_name] = {
                'id': dp_name,
                'lat': dp['lat'],
                'lon': dp['lon'],
                'substation': dp['substation'],
                'connected_lights': connected_lights,
                'capacity_kva': 500,
                'load_kw': len(connected_lights) * 0.3,  # 300W per light
                'operational': True
            }
        
        print(f"Created {len(self.distribution_feeders)} distribution feeders")
    
    def _manhattan_routing(self, lat1, lon1, lat2, lon2):
        """Create cable path following Manhattan street grid"""
        path = []
        
        # Start point
        path.append([lon1, lat1])
        
        # Manhattan routing: go east/west first, then north/south
        # This follows the actual street grid
        path.append([lon2, lat1])  # Horizontal segment
        path.append([lon2, lat2])  # Vertical segment
        
        return path
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate Manhattan distance (not Euclidean)"""
        # Manhattan distance is more realistic for street grid
        return abs(lat1 - lat2) + abs(lon1 - lon2)
    
    def _integrate_with_power_grid(self):
        """Add traffic light loads to PyPSA"""
        
        # Group loads by substation
        loads_by_substation = {}
        for feeder in self.distribution_feeders.values():
            sub = feeder['substation']
            if sub not in loads_by_substation:
                loads_by_substation[sub] = 0
            loads_by_substation[sub] += feeder['load_kw']
        
        # Add to PyPSA network
        for substation, load_kw in loads_by_substation.items():
            bus_name = f"{substation}_13.8kV"
            
            if bus_name in self.power_grid.network.buses.index:
                self.power_grid.network.add(
                    "Load",
                    f"TrafficLights_{substation}",
                    bus=bus_name,
                    p_set=load_kw / 1000  # Convert to MW
                )
                print(f"Added {load_kw}kW traffic light load to {substation}")
    
    def fail_substation(self, substation_name):
        """Simulate substation failure"""
        
        affected_feeders = []
        affected_lights = []
        
        # Find affected feeders
        for feeder_id, feeder in self.distribution_feeders.items():
            if feeder['substation'] == substation_name:
                feeder['operational'] = False
                affected_feeders.append(feeder_id)
                
                # Turn off connected lights
                for light_id in feeder['connected_lights']:
                    self.traffic_lights[light_id]['powered'] = False
                    affected_lights.append(light_id)
        
        return {
            'substation': substation_name,
            'affected_feeders': len(affected_feeders),
            'affected_lights': len(affected_lights),
            'total_lights': len(self.traffic_lights)
        }
    
    def restore_substation(self, substation_name):
        """Restore substation"""
        
        for feeder in self.distribution_feeders.values():
            if feeder['substation'] == substation_name:
                feeder['operational'] = True
                
                for light_id in feeder['connected_lights']:
                    self.traffic_lights[light_id]['powered'] = True
    
    def get_network_state(self):
        """Get complete network state for frontend"""
        
        # Build cable list
        cables = []
        
        # Main distribution cables (substation to feeder)
        for feeder_id, feeder in self.distribution_feeders.items():
            substation = feeder['substation']
            sub_coords = self._get_substation_coords(substation)
            
            cables.append({
                'id': f"main_{feeder_id}",
                'type': 'distribution',
                'path': [
                    [sub_coords[1], sub_coords[0]],
                    [feeder['lon'], feeder['lat']]
                ],
                'operational': feeder['operational'],
                'voltage': '13.8kV'
            })
            
            # Individual cables to traffic lights
            for light_id in feeder['connected_lights'][:10]:  # Limit for performance
                light = self.traffic_lights[light_id]
                if light['cable_path']:
                    cables.append({
                        'id': f"tl_{light_id}",
                        'type': 'service',
                        'path': light['cable_path'],
                        'operational': light['powered'],
                        'voltage': '480V'
                    })
        
        return {
            'traffic_lights': list(self.traffic_lights.values()),
            'feeders': list(self.distribution_feeders.values()),
            'cables': cables,
            'statistics': {
                'total_lights': len(self.traffic_lights),
                'powered_lights': sum(1 for tl in self.traffic_lights.values() if tl['powered']),
                'total_feeders': len(self.distribution_feeders),
                'operational_feeders': sum(1 for f in self.distribution_feeders.values() if f['operational'])
            }
        }
    
    def _get_substation_coords(self, name):
        """Get substation coordinates"""
        coords = {
            'Times Square': (40.7589, -73.9851),
            'Grand Central': (40.7527, -73.9772),
            'Penn Station': (40.7505, -73.9934),
            'Murray Hill': (40.7489, -73.9765)
        }
        return coords.get(name, (40.755, -73.98))