"""
World-Class EV Charging Station Manager - FIXED VERSION
Handles exactly 20 charging slots, no queue, vehicles circle if full
"""

import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

@dataclass
class ChargingPort:
    """Individual charging port at a station"""
    port_id: str
    power_kw: float
    occupied_by: Optional[str] = None
    charging_start: Optional[datetime] = None
    expected_finish: Optional[datetime] = None

class EVStationManager:
    """Manages all EV charging stations with strict 20-slot limit"""
    
    def __init__(self, integrated_system, sumo_net):
        self.integrated_system = integrated_system
        self.sumo_net = sumo_net
        self.stations = {}
        self.vehicle_reservations = {}  # vehicle_id -> station_id
        
        self._initialize_stations()
    
    def _initialize_stations(self):
        """Initialize stations with EXACTLY 20 ports each"""
        
        for ev_id, ev_station in self.integrated_system.ev_stations.items():
            # Find nearest valid edge
            edge = self._find_nearest_valid_edge(
                ev_station['lat'], 
                ev_station['lon']
            )
            
            if edge:
                # Create EXACTLY 20 charging ports per station
                ports = []
                for i in range(20):  # FIXED: Exactly 20 ports
                    # Mix of DC fast and Level 2
                    if i < 5:  # 25% fast chargers
                        power = 150  # DC fast charging
                    else:
                        power = 22   # Level 2
                    
                    ports.append(ChargingPort(
                        port_id=f"{ev_id}_port_{i}",
                        power_kw=power
                    ))
                
                self.stations[ev_id] = {
                    'id': ev_id,
                    'name': ev_station['name'],
                    'edge': edge,
                    'lat': ev_station['lat'],
                    'lon': ev_station['lon'],
                    'ports': ports,
                    'vehicles_charging': [],  # List of vehicle IDs currently charging
                    'operational': ev_station['operational'],
                    'substation': ev_station['substation'],
                    'total_power_kw': sum(p.power_kw for p in ports),
                    'current_load_kw': 0
                }
                
                print(f"Success Initialized {ev_station['name']} on edge {edge} with EXACTLY 20 ports")
    
    def _find_nearest_valid_edge(self, lat, lon):
        """Find nearest edge that can be routed to"""
        
        try:
            x, y = self.sumo_net.convertLonLat2XY(lon, lat)
            
            # Get edges that allow passenger vehicles
            valid_edges = [
                e for e in self.sumo_net.getEdges() 
                if e.allows("passenger") and not e.isSpecial()
            ]
            
            nearest_edge = None
            min_dist = float('inf')
            
            for edge in valid_edges:
                # Get edge center
                shape = edge.getShape()
                if shape:
                    edge_x = sum(p[0] for p in shape) / len(shape)
                    edge_y = sum(p[1] for p in shape) / len(shape)
                    
                    dist = np.sqrt((x - edge_x)**2 + (y - edge_y)**2)
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_edge = edge.getID()
            
            return nearest_edge
            
        except Exception as e:
            print(f"Error finding edge: {e}")
            return None
    
    def can_charge_at_station(self, station_id: str) -> Tuple[bool, int]:
        """Check if station has available charging slots
        Returns: (can_charge, num_available_slots)
        """
        
        if station_id not in self.stations:
            return False, 0
        
        station = self.stations[station_id]
        
        # Check if station has power
        if not station['operational']:
            return False, 0
        
        # Count occupied ports
        occupied = len([p for p in station['ports'] if p.occupied_by is not None])
        available = 20 - occupied  # FIXED: Always 20 total
        
        return available > 0, available
    
    def request_charging_simple(self, vehicle_id: str, station_id: str) -> bool:
        """Simple charging request - returns True if can charge, False if need to circle"""
        
        if station_id not in self.stations:
            return False
        
        station = self.stations[station_id]
        
        # Check if station is operational
        if not station['operational']:
            return False
        
        # Check if already charging
        if vehicle_id in station['vehicles_charging']:
            return True  # Already charging
        
        # Count current charging vehicles
        charging_count = len(station['vehicles_charging'])
        
        # STRICT LIMIT: Only allow if under 20
        if charging_count < 20:
            # Find available port
            for port in station['ports']:
                if port.occupied_by is None:
                    # Assign port
                    port.occupied_by = vehicle_id
                    port.charging_start = datetime.now()
                    
                    # Add to charging list
                    if vehicle_id not in station['vehicles_charging']:
                        station['vehicles_charging'].append(vehicle_id)
                    
                    # Update power load
                    station['current_load_kw'] += port.power_kw
                    
                    # Store reservation
                    self.vehicle_reservations[vehicle_id] = station_id
                    
                    print(f"Success {vehicle_id} -> Port at {station['name']} ({len(station['vehicles_charging'])}/20 occupied)")
                    return True
            
        # Station full - vehicle must circle
        print(f"❌ {station['name']} FULL (20/20) - {vehicle_id} must circle")
        return False

    def request_charging(self, vehicle_id: str, current_soc: float, current_edge: str,
                          vehicle_lonlat: Tuple[float, float], is_emergency: bool = False
                          ) -> Optional[Tuple[str, str, int, float]]:
        """Choose the nearest operational station with a free port.
        Does NOT reserve a port; reservation happens upon arrival.
        Returns tuple: (station_id, station_edge, estimated_wait_minutes, straight_line_distance_m)
        or None if no station available.
        """
        # Convert vehicle position to SUMO XY for distance calc
        try:
            veh_lon, veh_lat = vehicle_lonlat
            veh_x, veh_y = self.sumo_net.convertLonLat2XY(veh_lon, veh_lat)
        except Exception:
            return None

        best_station_id = None
        best_station_edge = None
        best_distance = float('inf')

        for station_id, station in self.stations.items():
            # Must be operational
            if not station['operational']:
                continue

            # Check available ports (strict 20 ports)
            occupied_ports = sum(1 for p in station['ports'] if p.occupied_by is not None)
            available_ports = 20 - occupied_ports
            if available_ports <= 0:
                continue

            # Compute straight-line distance in XY space using station edge center
            try:
                edge = self.sumo_net.getEdge(station['edge']) if station['edge'] else None
                if not edge:
                    continue
                shape = edge.getShape()
                if not shape:
                    continue
                edge_x = sum(p[0] for p in shape) / len(shape)
                edge_y = sum(p[1] for p in shape) / len(shape)
                dist = float(np.sqrt((veh_x - edge_x)**2 + (veh_y - edge_y)**2))
            except Exception:
                continue

            if dist < best_distance:
                best_distance = dist
                best_station_id = station_id
                best_station_edge = station['edge']

        if not best_station_id:
            return None

        # No reservation here. Vehicle will attempt to occupy a port on arrival.
        wait_minutes = 0
        return best_station_id, best_station_edge, wait_minutes, best_distance
    
    def update_charging(self, vehicle_id: str, current_soc: float) -> float:
        """Update charging progress - returns energy delivered"""
        
        for station_id, station in self.stations.items():
            for port in station['ports']:
                if port.occupied_by == vehicle_id:
                    # Calculate charge delivered (FAST for simulation)
                    if current_soc < 0.5:
                        # Fast charging below 50%
                        if port.power_kw >= 150:
                            energy_kwh = 1.5  # Super fast for simulation
                        else:
                            energy_kwh = 0.4
                    elif current_soc < 0.8:
                        # Medium speed 50-80%
                        if port.power_kw >= 150:
                            energy_kwh = 0.8
                        else:
                            energy_kwh = 0.3
                    else:
                        # Slow above 80%
                        energy_kwh = 0.2
                    
                    return energy_kwh
        
        return 0
    
    def finish_charging(self, vehicle_id: str) -> Optional[str]:
        """Finish charging and free up port
        Returns: station edge where vehicle was charging (for route continuation)
        """
        
        for station_id, station in self.stations.items():
            for port in station['ports']:
                if port.occupied_by == vehicle_id:
                    # Free the port
                    station['current_load_kw'] -= port.power_kw
                    port.occupied_by = None
                    port.charging_start = None
                    port.expected_finish = None
                    
                    # Remove from charging list
                    if vehicle_id in station['vehicles_charging']:
                        station['vehicles_charging'].remove(vehicle_id)
                    
                    # Clear reservation
                    if vehicle_id in self.vehicle_reservations:
                        del self.vehicle_reservations[vehicle_id]
                    
                    print(f"Battery {vehicle_id} finished charging at {station['name']} ({len(station['vehicles_charging'])}/20 now occupied)")
                    
                    # Return the edge where station is located
                    return station['edge']
        
        return None
    
    def handle_blackout(self, substation_name: str) -> List[str]:
        """Handle substation blackout - mark stations as offline"""
        
        affected_stations = []
        released_vehicles = []
        
        for station_id, station in self.stations.items():
            if station['substation'] == substation_name:
                station['operational'] = False
                affected_stations.append(station['name'])
                
                # Update in integrated system too
                if station_id in self.integrated_system.ev_stations:
                    self.integrated_system.ev_stations[station_id]['operational'] = False
                
                # Release all charging vehicles
                for port in station['ports']:
                    if port.occupied_by:
                        released_vehicles.append(port.occupied_by)
                        # Clear port
                        veh = port.occupied_by
                        port.occupied_by = None
                        port.charging_start = None
                        # Clear reservation mapping if any
                        if veh in self.vehicle_reservations:
                            del self.vehicle_reservations[veh]
                
                # Clear charging list
                station['vehicles_charging'].clear()
                station['current_load_kw'] = 0
        
        if affected_stations:
            print(f"POWER BLACKOUT: {', '.join(affected_stations)} offline! {len(released_vehicles)} vehicles interrupted")
        
        return released_vehicles
    
    def handle_station_failure(self, station_id: str) -> List[str]:
        """Handle individual station failure - release charging vehicles"""
        
        if station_id not in self.stations:
            return []
        
        station = self.stations[station_id]
        released_vehicles = []
        
        # Mark station as offline
        station['operational'] = False
        
        # Update in integrated system too
        if station_id in self.integrated_system.ev_stations:
            self.integrated_system.ev_stations[station_id]['operational'] = False
        
        # Release all charging vehicles
        for port in station['ports']:
            if port.occupied_by:
                released_vehicles.append(port.occupied_by)
                # Clear port
                veh = port.occupied_by
                port.occupied_by = None
                port.charging_start = None
                if veh in self.vehicle_reservations:
                    del self.vehicle_reservations[veh]
        
        # Clear charging list
        station['vehicles_charging'].clear()
        station['current_load_kw'] = 0
        
        if released_vehicles:
            print(f"[EMERGENCY] STATION FAILURE: {station['name']} offline! {len(released_vehicles)} vehicles interrupted")
        
        return released_vehicles
    
    def restore_power(self, substation_name: str) -> List[str]:
        """Restore power to stations"""
        
        restored_stations = []
        for station_id, station in self.stations.items():
            if station['substation'] == substation_name:
                station['operational'] = True
                restored_stations.append(station['name'])
                
                # Update in integrated system too
                if station_id in self.integrated_system.ev_stations:
                    self.integrated_system.ev_stations[station_id]['operational'] = True
        
        if restored_stations:
            print(f"Success POWER RESTORED: {', '.join(restored_stations)} back online!")
        
        return restored_stations
    
    def restore_station(self, station_id: str) -> bool:
        """Restore individual station"""
        
        if station_id not in self.stations:
            return False
        
        station = self.stations[station_id]
        station['operational'] = True
        
        # Update in integrated system too
        if station_id in self.integrated_system.ev_stations:
            self.integrated_system.ev_stations[station_id]['operational'] = True
        
        print(f"Success STATION RESTORED: {station['name']} back online")
        return True
    
    def get_station_status(self, station_id: str) -> Dict:
        """Get detailed station status"""
        
        if station_id not in self.stations:
            return None
        
        station = self.stations[station_id]
        
        occupied_ports = sum(1 for p in station['ports'] if p.occupied_by is not None)
        
        return {
            'operational': station['operational'],
            'total_ports': 20,  # Always 20
            'occupied_ports': occupied_ports,
            'available_ports': 20 - occupied_ports,
            'vehicles_charging': len(station['vehicles_charging']),
            'current_load_kw': station['current_load_kw'],
            'max_load_kw': station['total_power_kw'],
            'charging_vehicles': station['vehicles_charging'].copy()
        }
    
    def find_nearest_available_station(self, current_edge: str, current_soc: float) -> Optional[Tuple[str, str, int]]:
        """Find nearest station with available slots
        Returns: (station_id, station_edge, distance) or None
        """
        
        best_station = None
        min_distance = float('inf')
        
        for station_id, station in self.stations.items():
            # Skip non-operational stations
            if not station['operational']:
                continue
            
            # Check availability
            occupied = len(station['vehicles_charging'])
            if occupied >= 20:  # Station full
                continue
            
            # Simple distance estimate (you could use actual routing here)
            try:
                # For now, just return first available station
                return station_id, station['edge'], 1
            except:
                pass
        
        return None