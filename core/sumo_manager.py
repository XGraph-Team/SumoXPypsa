"""
core/sumo_manager.py - Complete SUMO Integration Module
Place this in your core/ directory
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

# Import the enhanced manager
from manhattan_sumo_manager import (
    ManhattanSUMOManager as BaseSUMOManager,
    VehicleType,
    SimulationScenario,
    VehicleConfig,
    Vehicle
)

# Re-export for compatibility
__all__ = ['ManhattanSUMOManager', 'VehicleType', 'SimulationScenario', 'VehicleConfig', 'Vehicle']

# Extend the base manager with any project-specific additions
class ManhattanSUMOManager(BaseSUMOManager):
    """Extended SUMO manager with project-specific features"""
    
    def __init__(self, integrated_system):
        super().__init__(integrated_system)
        
        # Additional project-specific initialization
        self.setup_manhattan_network()
    
    def setup_manhattan_network(self):
        """Ensure Manhattan network is properly configured"""
        
        # Check if network files exist
        required_files = [
            'data/sumo/manhattan.net.xml',
            'data/manhattan_traffic_lights.json'
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print("WARNING: Missing required files:")
            for f in missing_files:
                print(f"  - {f}")
            
            if 'data/sumo/manhattan.net.xml' in missing_files:
                print("\nINFO To fix: Run 'python get_manhattan_sumo_network.py'")
            if 'data/manhattan_traffic_lights.json' in missing_files:
                print("\nINFO To fix: Run 'python get_real_traffic_lights.py'")
            
            return False
        
        # Load connected network data if available
        connected_network_file = 'data/manhattan_connected_network.json'
        if os.path.exists(connected_network_file):
            with open(connected_network_file, 'r') as f:
                network_data = json.load(f)
                
                # Use connected edges for better routing
                if 'spawn_edges' in network_data:
                    self.spawn_edges = network_data['spawn_edges']
                    print(f"Loaded {len(self.spawn_edges)} spawn points")
                
                # Update charging station locations
                if 'charging_stations' in network_data:
                    for name, edge_id in network_data['charging_stations'].items():
                        # Map to your EV stations
                        for ev_id, ev_station in self.integrated_system.ev_stations.items():
                            if name.lower() in ev_station['name'].lower():
                                self.ev_stations_sumo[ev_id] = {
                                    'edge': edge_id,
                                    'capacity': ev_station['chargers'],
                                    'available': ev_station['chargers'],
                                    'charging': []
                                }
        
        return True
    
    def spawn_manhattan_traffic(self, scenario: SimulationScenario = None):
        """Spawn traffic appropriate for Manhattan scenario"""
        
        if scenario:
            self.current_scenario = scenario
        
        # Spawn patterns based on scenario
        if self.current_scenario == SimulationScenario.MORNING_RUSH:
            # Heavy traffic from residential to business areas
            self.spawn_vehicles(30, ev_percentage=0.3)  # More gas vehicles in rush hour
            print("Morning Morning rush: Heavy traffic spawned")
            
        elif self.current_scenario == SimulationScenario.EVENING_RUSH:
            # Heavy traffic from business to residential/entertainment
            self.spawn_vehicles(35, ev_percentage=0.4)  # EVs need charging after work
            print("Evening Evening rush: Maximum traffic spawned")
            
        elif self.current_scenario == SimulationScenario.MIDDAY:
            # Moderate traffic, mixed purposes
            self.spawn_vehicles(15, ev_percentage=0.5)
            print("Midday Midday: Moderate traffic spawned")
            
        elif self.current_scenario == SimulationScenario.NIGHT:
            # Light traffic, mostly taxis and deliveries
            self.spawn_vehicles(8, ev_percentage=0.7)  # More EVs at night
            print("Night Night: Light traffic spawned")
            
        elif self.current_scenario == SimulationScenario.WEEKEND:
            # Shopping and entertainment traffic
            self.spawn_vehicles(20, ev_percentage=0.6)
            print("Weekend Weekend: Shopping/entertainment traffic spawned")
            
        elif self.current_scenario == SimulationScenario.EMERGENCY:
            # Reduced traffic, emergency vehicles
            self.spawn_vehicles(5, ev_percentage=0.2)
            print("Emergency Emergency: Minimal traffic spawned")
    
    def simulate_power_outage_impact(self, affected_substations: List[str]):
        """Simulate how power outage affects traffic"""
        
        print(f"\nPOWER POWER OUTAGE AFFECTING TRAFFIC")
        print(f"Affected substations: {', '.join(affected_substations)}")
        
        if not self.running:
            print("WARNING SUMO not running")
            return
        
        # Update traffic lights
        self.update_traffic_lights()
        
        # Count affected traffic lights
        affected_tls = 0
        for power_tl_id, sumo_tl_id in self.tl_power_to_sumo.items():
            if power_tl_id in self.integrated_system.traffic_lights:
                power_tl = self.integrated_system.traffic_lights[power_tl_id]
                if not power_tl['powered']:
                    affected_tls += 1
        
        print(f"Traffic lights {affected_tls} traffic lights without power (showing as all red)")
        
        # Check EV stations
        affected_ev_stations = 0
        for ev_id, ev_station in self.integrated_system.ev_stations.items():
            if ev_station['substation'] in affected_substations:
                affected_ev_stations += 1
                
                # Update SUMO EV station availability
                if ev_id in self.ev_stations_sumo:
                    self.ev_stations_sumo[ev_id]['available'] = 0
                    
                    # Reroute vehicles that were heading there
                    for vehicle in self.vehicles.values():
                        if vehicle.assigned_ev_station == ev_id:
                            vehicle.assigned_ev_station = None
                            vehicle.is_charging = False
                            # Find alternative station
                            self._route_to_charging_station(vehicle)
        
        print(f"POWER {affected_ev_stations} EV charging stations offline")
        
        # Estimate traffic impact
        try:
            import traci
            if self.running:
                # Get current traffic metrics
                vehicle_ids = traci.vehicle.getIDList()
                if vehicle_ids:
                    avg_speed_before = sum(traci.vehicle.getSpeed(v) for v in vehicle_ids) / len(vehicle_ids)
                    total_waiting = sum(traci.vehicle.getWaitingTime(v) for v in vehicle_ids)
                    
                    print(f"\nStats TRAFFIC IMPACT:")
                    print(f"  - Average speed: {avg_speed_before * 3.6:.1f} km/h")
                    print(f"  - Total waiting time: {total_waiting:.0f} seconds")
                    print(f"  - Vehicles affected: {len(vehicle_ids)}")
                    
                    if affected_tls > 10:
                        print("  WARNING SEVERE: Major traffic disruption expected")
                    elif affected_tls > 5:
                        print("  WARNING MODERATE: Significant delays expected")
                    else:
                        print("  WARNING MINOR: Local delays expected")
        except:
            pass
    
    def get_vehicle_positions_for_visualization(self) -> List[Dict]:
        """Get vehicle data formatted for web visualization"""
        
        if not self.running:
            return []
        
        try:
            import traci
            vehicles_data = []
            
            for vehicle in self.vehicles.values():
                try:
                    if vehicle.id in traci.vehicle.getIDList():
                        # Get position
                        x, y = traci.vehicle.getPosition(vehicle.id)
                        lon, lat = traci.simulation.convertGeo(x, y)
                        
                        # Ensure within Manhattan bounds
                        if (self.bounds['south'] <= lat <= self.bounds['north'] and
                            self.bounds['west'] <= lon <= self.bounds['east']):
                            
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
                                'color': self._get_vehicle_color(vehicle)
                            })
                except:
                    pass
            
            return vehicles_data
        
        except:
            return []
    
    def _get_vehicle_color(self, vehicle: Vehicle) -> str:
        """Get vehicle color for visualization"""
        
        if vehicle.is_charging:
            return '#ffa500'  # Orange for charging
        elif vehicle.config.is_ev:
            if vehicle.config.current_soc < 0.2:
                return '#ff6b6b'  # Red for low battery
            else:
                return '#00ff00'  # Green for EV
        elif vehicle.config.vtype == VehicleType.TAXI:
            return '#ffff00'  # Yellow for taxi
        elif vehicle.config.vtype == VehicleType.BUS:
            return '#4169e1'  # Blue for bus
        else:
            return '#6464ff'  # Light blue for gas vehicles (consistent with frontend)