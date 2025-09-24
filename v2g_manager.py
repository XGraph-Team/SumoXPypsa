# v2g_manager.py
"""
Manhattan V2G System - WORLD CLASS Vehicle-to-Grid Implementation
ULTRA PREMIUM VERSION - Realistic power delivery with accelerated simulation
"""

import json
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

@dataclass
class V2GContract:
    """Smart contract for V2G energy trading"""
    vehicle_id: str
    substation_id: str
    power_provided_kw: float
    start_time: datetime
    duration_seconds: float
    price_per_kwh: float  # Premium rate (10x normal charging cost)
    total_earnings: float = 0
    status: str = "active"  # active, completed, cancelled
    
@dataclass 
class V2GSession:
    """Individual V2G discharge session with realistic metrics"""
    session_id: str
    vehicle_id: str
    station_id: str
    substation_id: str
    initial_soc: float
    current_soc: float
    power_delivered_kwh: float = 0
    earnings: float = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    locked_at_station: bool = True
    min_energy_required: float = 0  # No minimum requirement
    target_discharge_duration: float = 0  # No duration requirement
    actual_power_kw: float = 0  # Track actual discharge rate
    peak_power_kw: float = 0  # Track peak discharge

class V2GManager:
    """WORLD CLASS Professional V2G orchestration - ULTRA REALISTIC VERSION"""
    
    # ==========================================
    # PREMIUM PRICING MODEL
    # ==========================================
    CHARGING_COST = 0.15  # Normal charging cost ($/kWh)
    V2G_RATE_MULTIPLIER = 50.0  # PREMIUM 50x for V2G service (reduced from 100x)
    EMERGENCY_MULTIPLIER = 150.0  # ULTRA PREMIUM 150x during critical events
    
    # ==========================================
    # REALISTIC POWER SPECIFICATIONS
    # ==========================================
    MIN_SOC_FOR_V2G = 0.60  # 60% minimum to participate
    MAX_DISCHARGE_SOC = 0.30  # Don't discharge below 30%
    
    # Realistic V2G discharge rates (kW)
    DISCHARGE_RATE_LEVEL_1 = 7.2   # Level 1 V2G (home outlet equivalent)
    DISCHARGE_RATE_LEVEL_2 = 50    # Level 2 V2G (commercial grade)
    DISCHARGE_RATE_DC_FAST = 150   # DC Fast V2G (premium stations)
    
    # Default discharge rate
    DISCHARGE_RATE_KW = DISCHARGE_RATE_LEVEL_2  # 50kW standard
    
    # ==========================================
    # SIMULATION ACCELERATION
    # ==========================================
    SIMULATION_TIME_MULTIPLIER = 20  # 20x faster for visible testing
    # Each 0.1s simulation step = 2 seconds of real discharge
    
    # ==========================================
    # OPERATIONAL PARAMETERS
    # ==========================================
    MIN_DISCHARGE_DURATION_SECONDS = 0  # No minimum duration
    MIN_ENERGY_PER_VEHICLE_KWH = 0  # No minimum energy requirement
    RESTORATION_ENERGY_THRESHOLD_KWH = 25  # Need 25 kWh total for restoration (slower recovery)
    MAX_V2G_VEHICLES = 10  # Maximum 10 vehicles simultaneously
    
    def __init__(self, integrated_system, sumo_manager):
        """Initialize WORLD CLASS V2G Manager"""
        
        self.integrated_system = integrated_system
        self.sumo_manager = sumo_manager
        
        # ==========================================
        # STATE MANAGEMENT WITH CONFLICT PREVENTION
        # ==========================================
        self.v2g_enabled_substations = set()
        self.active_sessions = {}  # vehicle_id -> V2GSession
        self.v2g_locked_vehicles = set()  # Vehicles locked in V2G mode
        self.pending_v2g_vehicles = {}  # Vehicles en route to V2G
        self.contracts = []  # Smart contracts
        
        # Power and energy tracking
        self.substation_power_needs = {}  # kW needed
        self.substation_energy_delivered = {}  # kWh delivered
        self.substation_energy_required = {}  # kWh required for restoration
        self.vehicles_providing_v2g = {}  # Active V2G providers
        
        # Restoration tracking
        self.restored_substations = set()
        self.restoration_in_progress = set()
        # Track recent restorations for UX (persist across refresh briefly)
        self.recently_restored: Dict[str, datetime] = {}
        
        # ==========================================
        # STATISTICS & ANALYTICS
        # ==========================================
        self.stats = {
            'total_kwh_provided': 0,
            'total_earnings': 0,
            'vehicles_participated': set(),
            'substations_restored': 0,
            'active_v2g_vehicles': 0,
            'peak_power_provided_kw': 0,
            'total_revenue_generated': 0,
            'average_discharge_rate_kw': 0,
            'total_discharge_time_minutes': 0
        }
        
        # Market dynamics
        self.market_price = self.CHARGING_COST * self.V2G_RATE_MULTIPLIER
        self.emergency_zones = set()
        
        # ==========================================
        # INITIALIZATION MESSAGE
        # ==========================================
        print("\n" + "="*60)
        print("⚡ V2G MANAGER INITIALIZED - ULTRA PREMIUM VERSION")
        print("="*60)
        print(f"💰 PRICING:")
        print(f"   Base rate: ${self.CHARGING_COST}/kWh")
        print(f"   V2G rate: ${self.market_price:.2f}/kWh (50x premium)")
        print(f"   Emergency rate: ${self.CHARGING_COST * self.EMERGENCY_MULTIPLIER:.2f}/kWh")
        print(f"\n⚡ DISCHARGE SPECIFICATIONS:")
        print(f"   Standard rate: {self.DISCHARGE_RATE_KW} kW")
        print(f"   Simulation acceleration: {self.SIMULATION_TIME_MULTIPLIER}x")
        print(f"   Real discharge time (60→30%): ~36 minutes")
        print(f"   Simulated time: ~{36/self.SIMULATION_TIME_MULTIPLIER:.1f} minutes")
        print(f"\n🚗 OPERATIONAL LIMITS:")
        print(f"   Max vehicles: {self.MAX_V2G_VEHICLES}")
        print(f"   Min SOC to join: {self.MIN_SOC_FOR_V2G:.0%}")
        print(f"   Discharge until: {self.MAX_DISCHARGE_SOC:.0%}")
        print(f"   Energy requirement: NONE - discharge freely")
        print("="*60 + "\n")
    
    def enable_v2g_for_substation(self, substation_name: str) -> bool:
        """Enable V2G support for failed substation - PREMIUM MODE"""
        
        if substation_name not in self.integrated_system.substations:
            return False
        
        # Check if already restored
        if substation_name in self.restored_substations:
            print(f"✅ {substation_name} already restored - V2G not needed")
            return False
        
        substation = self.integrated_system.substations[substation_name]
        
        # Only enable for failed substations
        if substation['operational']:
            print(f"⚠️ {substation_name} is operational - V2G not needed")
            return False
        
        self.v2g_enabled_substations.add(substation_name)
        self.restored_substations.discard(substation_name)
        
        # Calculate power requirements
        power_deficit_mw = substation['load_mw']
        self.substation_power_needs[substation_name] = power_deficit_mw * 1000  # kW
        
        # Set restoration energy threshold
        energy_needed_kwh = self.RESTORATION_ENERGY_THRESHOLD_KWH
        self.substation_energy_required[substation_name] = energy_needed_kwh
        self.substation_energy_delivered[substation_name] = 0
        
        # Mark as emergency zone for premium pricing
        if power_deficit_mw > 50:
            self.emergency_zones.add(substation_name)
        
        # Calculate potential revenue
        rate = self.get_current_rate(substation_name)
        max_revenue = energy_needed_kwh * rate * 10  # If 10 vehicles participate
        
        print("\n" + "="*60)
        print(f"⚡💰 V2G ACTIVATED - {substation_name}")
        print("="*60)
        print(f"📊 POWER DEFICIT: {power_deficit_mw:.1f} MW")
        print(f"⚡ ENERGY TARGET: {energy_needed_kwh:.1f} kWh for restoration")
        print(f"\n💵 PREMIUM PRICING:")
        print(f"   Rate: ${rate:.2f}/kWh ({int(rate/self.CHARGING_COST)}x normal)")
        print(f"   Max pool revenue: ${max_revenue:.0f}")
        print(f"   Per vehicle potential: ${max_revenue/10:.0f}")
        print(f"\n🚗 VEHICLE REQUIREMENTS:")
        print(f"   Vehicles needed: Up to {self.MAX_V2G_VEHICLES}")
        print(f"   Min SOC: {self.MIN_SOC_FOR_V2G:.0%}")
        print(f"   Discharge to: {self.MAX_DISCHARGE_SOC:.0%}")
        print(f"\n⏱️ ESTIMATED TIMELINE:")
        print(f"   With {self.MAX_V2G_VEHICLES} vehicles @ {self.DISCHARGE_RATE_KW}kW each")
        print(f"   Total power: {self.MAX_V2G_VEHICLES * self.DISCHARGE_RATE_KW}kW")
        print(f"   Time to restore: ~{energy_needed_kwh/(self.MAX_V2G_VEHICLES * self.DISCHARGE_RATE_KW)*60:.1f} minutes")
        print("="*60 + "\n")
        
        # Broadcast opportunity
        self._broadcast_v2g_opportunity(substation_name)
        
        return True
    
    def disable_v2g_for_substation(self, substation_name: str):
        """Disable V2G and release all vehicles"""
        
        if substation_name in self.v2g_enabled_substations:
            self.v2g_enabled_substations.remove(substation_name)
        
        self.restored_substations.add(substation_name)
        
        # End all sessions for this substation
        sessions_to_end = []
        for vehicle_id, session in self.active_sessions.items():
            if session.substation_id == substation_name:
                sessions_to_end.append(vehicle_id)
        
        for vehicle_id in sessions_to_end:
            self._force_end_v2g_session(vehicle_id, reason="substation_manually_restored")
        
        # Clear pending vehicles
        pending_to_clear = []
        for vid, sub in self.pending_v2g_vehicles.items():
            if sub == substation_name:
                pending_to_clear.append(vid)
        
        for vid in pending_to_clear:
            del self.pending_v2g_vehicles[vid]
            if vid in self.sumo_manager.vehicles:
                vehicle = self.sumo_manager.vehicles[vid]
                if hasattr(vehicle, 'v2g_target_substation'):
                    delattr(vehicle, 'v2g_target_substation')
        
        print(f"🔌 V2G DISABLED for {substation_name} - All vehicles released")
    
    def get_current_rate(self, substation_name: str) -> float:
        """Calculate dynamic V2G rate with time-of-day pricing"""
        
        # Base premium rate
        base_rate = self.CHARGING_COST * self.V2G_RATE_MULTIPLIER
        
        # Emergency premium
        if substation_name in self.emergency_zones:
            base_rate = self.CHARGING_COST * self.EMERGENCY_MULTIPLIER
        
        # Time-of-day multiplier
        hour = datetime.now().hour
        if 17 <= hour <= 21:  # Peak hours
            base_rate *= 1.5
        elif 0 <= hour <= 6:  # Off-peak
            base_rate *= 1.2
        
        return base_rate
    
    def _broadcast_v2g_opportunity(self, substation_name: str):
        """Intelligently recruit EVs for V2G service"""
        
        if not self.sumo_manager or not self.sumo_manager.running:
            return
        
        if substation_name in self.restored_substations:
            return
        
        import traci
        
        eligible_vehicles = []
        
        # Find high-SOC EVs
        for vehicle in self.sumo_manager.vehicles.values():
            if not vehicle.config.is_ev:
                continue
            
            # Check SOC requirement
            if vehicle.config.current_soc < self.MIN_SOC_FOR_V2G:
                continue
            
            # Skip if already occupied
            if (vehicle.id in self.v2g_locked_vehicles or
                vehicle.id in self.active_sessions or
                vehicle.id in self.pending_v2g_vehicles or
                (hasattr(vehicle, 'is_charging') and vehicle.is_charging) or
                (hasattr(vehicle, 'assigned_ev_station') and vehicle.assigned_ev_station)):
                continue
            
            if vehicle.id in traci.vehicle.getIDList():
                eligible_vehicles.append(vehicle)
        
        if eligible_vehicles:
            # Sort by SOC (highest first)
            eligible_vehicles.sort(key=lambda v: v.config.current_soc, reverse=True)
            
            # Use up to MAX_V2G_VEHICLES
            vehicles_to_use = min(self.MAX_V2G_VEHICLES, len(eligible_vehicles))
            
            rate = self.get_current_rate(substation_name)
            
            print(f"\n📢 V2G RECRUITMENT - {substation_name}")
            print(f"   Found: {len(eligible_vehicles)} eligible EVs")
            print(f"   Recruiting: {vehicles_to_use} vehicles")
            print(f"   💰 Rate: ${rate:.2f}/kWh")
            
            # Route vehicles to V2G
            for i, vehicle in enumerate(eligible_vehicles[:vehicles_to_use]):
                potential_energy = (vehicle.config.current_soc - self.MAX_DISCHARGE_SOC) * vehicle.config.battery_capacity_kwh
                potential_earnings = potential_energy * rate
                
                print(f"   🚗 {vehicle.id}: SOC={vehicle.config.current_soc:.0%} "
                      f"→ Potential: {potential_energy:.1f}kWh = ${potential_earnings:.0f}")
                
                self._route_to_v2g_station(vehicle, substation_name)
    
    def _route_to_v2g_station(self, vehicle, substation_name: str):
        """Route vehicle to V2G station with visual feedback"""
        
        import traci
        
        # Prevent double assignment
        if vehicle.id in self.v2g_locked_vehicles or vehicle.id in self.pending_v2g_vehicles:
            return
        
        # Find best station
        best_station = None
        min_distance = float('inf')
        
        for ev_id, ev_station in self.integrated_system.ev_stations.items():
            if ev_station['substation'] == substation_name:
                try:
                    x, y = traci.vehicle.getPosition(vehicle.id)
                    veh_lon, veh_lat = traci.simulation.convertGeo(x, y)
                    
                    dist = ((veh_lat - ev_station['lat'])**2 + 
                           (veh_lon - ev_station['lon'])**2)**0.5
                    
                    if dist < min_distance:
                        min_distance = dist
                        best_station = ev_id
                except:
                    continue
        
        if best_station and self.sumo_manager.station_manager:
            station = self.sumo_manager.station_manager.stations.get(best_station)
            if station:
                try:
                    current_edge = traci.vehicle.getRoadID(vehicle.id)
                    route = traci.simulation.findRoute(current_edge, station['edge'])
                    
                    if route and route.edges:
                        # Lock for V2G
                        self.pending_v2g_vehicles[vehicle.id] = substation_name
                        
                        # Clear charging assignments
                        vehicle.assigned_ev_station = None
                        vehicle.is_charging = False
                        if hasattr(vehicle, 'charging_at_station'):
                            vehicle.charging_at_station = None
                        
                        # Set V2G assignment
                        vehicle.v2g_station = best_station
                        vehicle.v2g_target_substation = substation_name
                        
                        # Route to station
                        traci.vehicle.setRoute(vehicle.id, route.edges)
                        
                        # Purple for V2G mode
                        traci.vehicle.setColor(vehicle.id, (128, 0, 255, 255))
                        
                        station_name = self.integrated_system.ev_stations[best_station]['name']
                        print(f"      → Routing to {station_name}")
                        
                except Exception as e:
                    print(f"Error routing to V2G: {e}")
    
    def start_v2g_session(self, vehicle_id: str, station_id: str, substation_id: str) -> bool:
        """Initialize V2G discharge session with realistic parameters"""
        
        # Check if substation restored
        if substation_id in self.restored_substations:
            return False
        
        if vehicle_id in self.active_sessions:
            return False
        
        vehicle = self.sumo_manager.vehicles.get(vehicle_id)
        if not vehicle or not vehicle.config.is_ev:
            return False
        
        # SOC check
        if vehicle.config.current_soc < self.MIN_SOC_FOR_V2G:
            print(f"❌ {vehicle_id} SOC too low ({vehicle.config.current_soc:.0%})")
            return False
        
        # Calculate discharge potential
        max_discharge_kwh = (vehicle.config.current_soc - self.MAX_DISCHARGE_SOC) * vehicle.config.battery_capacity_kwh
        
        # Create session
        session = V2GSession(
            session_id=f"v2g_{vehicle_id}_{int(time.time())}",
            vehicle_id=vehicle_id,
            station_id=station_id,
            substation_id=substation_id,
            initial_soc=vehicle.config.current_soc,
            current_soc=vehicle.config.current_soc,
            locked_at_station=True,
            min_energy_required=0,
            target_discharge_duration=0,
            actual_power_kw=self.DISCHARGE_RATE_KW
        )
        
        # Lock vehicle
        self.active_sessions[vehicle_id] = session
        self.v2g_locked_vehicles.add(vehicle_id)
        self.vehicles_providing_v2g[vehicle_id] = substation_id
        
        # Remove from pending
        if vehicle_id in self.pending_v2g_vehicles:
            del self.pending_v2g_vehicles[vehicle_id]
        
        # Update vehicle state
        vehicle.in_v2g_session = True
        vehicle.is_charging = False
        
        # Statistics
        self.stats['vehicles_participated'].add(vehicle_id)
        self.stats['active_v2g_vehicles'] = len(self.active_sessions)
        
        # Lock at station
        import traci
        if vehicle_id in traci.vehicle.getIDList():
            traci.vehicle.setSpeed(vehicle_id, 0)
            current_edge = traci.vehicle.getRoadID(vehicle_id)
            traci.vehicle.setRoute(vehicle_id, [current_edge])
            traci.vehicle.setColor(vehicle_id, (0, 255, 255, 255))
        
        station_name = self.integrated_system.ev_stations[station_id]['name']
        rate = self.get_current_rate(substation_id)
        
        print(f"\n⚡ V2G SESSION INITIATED")
        print(f"   Vehicle: {vehicle_id}")
        print(f"   Battery: {vehicle.config.battery_capacity_kwh}kWh @ {vehicle.config.current_soc:.0%}")
        print(f"   Station: {station_name}")
        print(f"   💰 Rate: ${rate:.2f}/kWh")
        print(f"   ⚡ Power: {self.DISCHARGE_RATE_KW}kW")
        print(f"   📊 Potential: {max_discharge_kwh:.1f}kWh = ${max_discharge_kwh * rate:.0f}")
        
        return True
    
    def update_v2g_sessions(self):
        """Update V2G sessions with REALISTIC FAST DISCHARGE"""
        
        import traci
        
        sessions_to_end = []
        total_power_provided = 0
        
        for vehicle_id, session in list(self.active_sessions.items()):
            # Check if substation restored
            if session.substation_id in self.restored_substations:
                sessions_to_end.append(vehicle_id)
                continue
            
            vehicle = self.sumo_manager.vehicles.get(vehicle_id)
            if not vehicle:
                sessions_to_end.append(vehicle_id)
                continue
            
            # Visual feedback
            if vehicle_id in traci.vehicle.getIDList():
                traci.vehicle.setSpeed(vehicle_id, 0)
                current_edge = traci.vehicle.getRoadID(vehicle_id)
                traci.vehicle.setRoute(vehicle_id, [current_edge])
                
                # Pulsing cyan
                pulse = int(time.time() * 4) % 4
                colors = [(0, 255, 255, 255), (50, 255, 255, 255), 
                        (0, 200, 255, 255), (100, 255, 255, 255)]
                traci.vehicle.setColor(vehicle_id, colors[pulse])
            
            # ==========================================
            # REALISTIC DISCHARGE CALCULATION
            # ==========================================
            # Each 0.1s step with acceleration multiplier
            time_per_step = 0.1 * self.SIMULATION_TIME_MULTIPLIER  # 2 seconds per step
            
            # Energy discharged (kWh)
            discharge_rate_kwh = (self.DISCHARGE_RATE_KW * time_per_step) / 3600
            
            # SOC decrease
            battery_capacity = vehicle.config.battery_capacity_kwh
            soc_decrease = discharge_rate_kwh / battery_capacity
            
            # Update SOC
            old_soc = vehicle.config.current_soc
            vehicle.config.current_soc -= soc_decrease
            vehicle.config.current_soc = max(self.MAX_DISCHARGE_SOC, vehicle.config.current_soc)
            
            # Update metrics
            actual_soc_decrease = old_soc - vehicle.config.current_soc
            actual_energy = actual_soc_decrease * battery_capacity
            
            session.current_soc = vehicle.config.current_soc
            session.power_delivered_kwh += actual_energy
            session.actual_power_kw = self.DISCHARGE_RATE_KW
            
            # Calculate earnings
            rate = self.get_current_rate(session.substation_id)
            earnings_this_step = actual_energy * rate
            session.earnings += earnings_this_step
            
            # Update substation tracking
            if session.substation_id in self.substation_energy_delivered:
                self.substation_energy_delivered[session.substation_id] += actual_energy
                total_power_provided += self.DISCHARGE_RATE_KW
            
            # Progress indicator every 1% SOC
            if int(old_soc * 100) != int(vehicle.config.current_soc * 100):
                energy_delivered = self.substation_energy_delivered.get(session.substation_id, 0)
                energy_required = self.substation_energy_required.get(session.substation_id, 100)
                progress = min(100, (energy_delivered / energy_required) * 100)
                
                # Time calculations
                session_duration = (datetime.now() - session.start_time).total_seconds()
                effective_minutes = (session.power_delivered_kwh / self.DISCHARGE_RATE_KW) * 60
                
                print(f"⚡ {vehicle_id}: {vehicle.config.current_soc:.0%}% | "
                      f"${session.earnings:.2f} | "
                      f"{session.power_delivered_kwh:.2f}kWh | "
                      f"{effective_minutes:.1f}min | "
                      f"Grid: {progress:.0f}%")
            
            # Check completion
            if vehicle.config.current_soc <= self.MAX_DISCHARGE_SOC:
                sessions_to_end.append(vehicle_id)
                
                # Final stats
                total_soc = session.initial_soc - session.current_soc
                discharge_minutes = (session.power_delivered_kwh / self.DISCHARGE_RATE_KW) * 60
                
                print(f"\n🔋 {vehicle_id} DISCHARGE COMPLETE")
                print(f"   SOC: {session.initial_soc:.0%} → {session.current_soc:.0%}")
                print(f"   Energy: {session.power_delivered_kwh:.2f}kWh")
                print(f"   Time: {discharge_minutes:.1f} minutes")
                print(f"   💵 Earned: ${session.earnings:.2f}")
                print(f"   Rate: ${session.earnings/session.power_delivered_kwh:.2f}/kWh")
            
            # Check restoration
            if session.substation_id in self.substation_energy_delivered:
                energy_delivered = self.substation_energy_delivered[session.substation_id]
                energy_required = self.substation_energy_required.get(session.substation_id, 100)
                
                if energy_delivered >= energy_required:
                    self.restoration_in_progress.add(session.substation_id)
        
        # Process restorations
        for substation_name in list(self.restoration_in_progress):
            self._complete_substation_restoration(substation_name)
            self.restoration_in_progress.discard(substation_name)
        
        # End sessions
        for vehicle_id in sessions_to_end:
            self._force_end_v2g_session(vehicle_id, reason="completed")
        
        # Update peak power
        if total_power_provided > self.stats['peak_power_provided_kw']:
            self.stats['peak_power_provided_kw'] = total_power_provided
        
        # Update average discharge rate
        if self.active_sessions:
            total_rate = sum(s.actual_power_kw for s in self.active_sessions.values())
            self.stats['average_discharge_rate_kw'] = total_rate / len(self.active_sessions)
    
    def _force_end_v2g_session(self, vehicle_id: str, reason: str = "normal"):
        """Complete V2G session with full analytics"""
        
        if vehicle_id not in self.active_sessions:
            return
        
        session = self.active_sessions[vehicle_id]
        session.end_time = datetime.now()
        session.status = "completed"
        
        # Update statistics
        self.stats['total_kwh_provided'] += session.power_delivered_kwh
        self.stats['total_earnings'] += session.earnings
        self.stats['total_revenue_generated'] += session.earnings
        
        # Calculate metrics
        duration_seconds = (session.end_time - session.start_time).total_seconds()
        duration_minutes = duration_seconds / 60
        self.stats['total_discharge_time_minutes'] += duration_minutes
        
        # Summary
        print(f"\n💰 V2G SESSION COMPLETE - {reason.upper()}")
        print(f"   Vehicle: {vehicle_id}")
        print(f"   Duration: {duration_minutes:.1f} minutes")
        print(f"   Energy: {session.power_delivered_kwh:.2f} kWh")
        print(f"   💵 EARNINGS: ${session.earnings:.2f}")
        if session.power_delivered_kwh > 0:
            print(f"   Effective rate: ${session.earnings/session.power_delivered_kwh:.2f}/kWh")
        print(f"   SOC: {session.initial_soc:.0%} → {session.current_soc:.0%}")
        
        # Release vehicle
        vehicle = self.sumo_manager.vehicles.get(vehicle_id)
        if vehicle:
            # Clear flags
            vehicle.assigned_ev_station = None
            vehicle.in_v2g_session = False
            vehicle.is_charging = False
            
            if hasattr(vehicle, 'v2g_target_substation'):
                delattr(vehicle, 'v2g_target_substation')
            if hasattr(vehicle, 'v2g_station'):
                delattr(vehicle, 'v2g_station')
            if hasattr(vehicle, 'charging_at_station'):
                vehicle.charging_at_station = None
            
            # Resume driving
            import traci
            if vehicle_id in traci.vehicle.getIDList():
                traci.vehicle.setColor(vehicle_id, (0, 255, 0, 255))
                traci.vehicle.setSpeed(vehicle_id, -1)
                traci.vehicle.setMaxSpeed(vehicle_id, 200)
                
                # New route
                current_edge = traci.vehicle.getRoadID(vehicle_id)
                all_edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
                
                if len(all_edges) > 10:
                    import random
                    destination = random.choice(all_edges[5:])
                    
                    try:
                        route = traci.simulation.findRoute(current_edge, destination)
                        if route and route.edges:
                            traci.vehicle.setRoute(vehicle_id, route.edges)
                    except:
                        if all_edges:
                            traci.vehicle.setRoute(vehicle_id, [current_edge, all_edges[0]])
        
        # Cleanup
        del self.active_sessions[vehicle_id]
        self.v2g_locked_vehicles.discard(vehicle_id)
        
        if vehicle_id in self.vehicles_providing_v2g:
            del self.vehicles_providing_v2g[vehicle_id]
        if vehicle_id in self.pending_v2g_vehicles:
            del self.pending_v2g_vehicles[vehicle_id]
        
        self.stats['active_v2g_vehicles'] = len(self.active_sessions)
    
    def _complete_substation_restoration(self, substation_name: str):
        """Complete restoration with celebration"""
        
        energy_delivered = self.substation_energy_delivered.get(substation_name, 0)
        energy_required = self.substation_energy_required.get(substation_name, 0)
        
        print("\n" + "="*60)
        print(f"🎉 SUBSTATION {substation_name} RESTORED!")
        print("="*60)
        print(f"⚡ Energy delivered: {energy_delivered:.1f} kWh")
        print(f"📊 Target achieved: {(energy_delivered/max(energy_required, 1))*100:.0f}%")
        
        # Calculate totals
        total_revenue = 0
        contributing_vehicles = []
        for vehicle_id, session in self.active_sessions.items():
            if session.substation_id == substation_name:
                contributing_vehicles.append((vehicle_id, session.earnings))
                total_revenue += session.earnings
        
        if contributing_vehicles:
            print(f"\n💰 REVENUE DISTRIBUTION:")
            for vid, earnings in contributing_vehicles:
                print(f"   {vid}: ${earnings:.2f}")
            print(f"   TOTAL: ${total_revenue:.2f}")
        
        print("="*60 + "\n")
        
        # Mark restored
        self.restored_substations.add(substation_name)
        # Record recent restoration timestamp
        self.recently_restored[substation_name] = datetime.now()
        
        # Restore in system
        if not self.integrated_system.substations[substation_name]['operational']:
            self.integrated_system.restore_substation(substation_name)
        
        # Cleanup
        self.v2g_enabled_substations.discard(substation_name)
        
        if substation_name in self.substation_power_needs:
            del self.substation_power_needs[substation_name]
        if substation_name in self.substation_energy_delivered:
            del self.substation_energy_delivered[substation_name]
        if substation_name in self.substation_energy_required:
            del self.substation_energy_required[substation_name]
        
        # End sessions
        sessions_to_end = []
        for vehicle_id, session in self.active_sessions.items():
            if session.substation_id == substation_name:
                sessions_to_end.append(vehicle_id)
        
        for vehicle_id in sessions_to_end:
            self._force_end_v2g_session(vehicle_id, reason="substation_restored")
        
        # Clear pending
        pending_to_clear = []
        for vid, sub in self.pending_v2g_vehicles.items():
            if sub == substation_name:
                pending_to_clear.append(vid)
        
        for vid in pending_to_clear:
            del self.pending_v2g_vehicles[vid]
        
        self.stats['substations_restored'] += 1
    
    def get_v2g_dashboard_data(self) -> Dict:
        """Provide real-time V2G analytics"""
        
        # Calculate active power
        active_power = len(self.active_sessions) * self.DISCHARGE_RATE_KW
        
        # Real-time earnings rate
        earnings_rate = 0
        if self.active_sessions:
            for session in self.active_sessions.values():
                rate = self.get_current_rate(session.substation_id)
                earnings_rate += (self.DISCHARGE_RATE_KW / 3600) * rate
        
        # Compute recently restored list within 90 seconds window
        now = datetime.now()
        recent_restored_names: List[str] = []
        to_delete: List[str] = []
        for name, ts in list(self.recently_restored.items()):
            # Keep for 90 seconds
            if (now - ts).total_seconds() <= 90:
                recent_restored_names.append(name)
            else:
                to_delete.append(name)
        # Cleanup expired
        for name in to_delete:
            del self.recently_restored[name]

        return {
            'enabled_substations': list(self.v2g_enabled_substations),
            'restored_substations': list(self.restored_substations),
            'recently_restored_substations': recent_restored_names,
            'active_sessions': len(self.active_sessions),
            'locked_vehicles': len(self.v2g_locked_vehicles),
            'pending_vehicles': len(self.pending_v2g_vehicles),
            'total_power_kw': active_power,
            'discharge_rate_kw': self.DISCHARGE_RATE_KW,
            'simulation_multiplier': self.SIMULATION_TIME_MULTIPLIER,
            'total_earnings': self.stats['total_earnings'],
            'earnings_rate_per_hour': earnings_rate * 3600,
            'total_kwh_provided': self.stats['total_kwh_provided'],
            'vehicles_participated': len(self.stats['vehicles_participated']),
            'substations_restored': self.stats['substations_restored'],
            'current_rate': self.market_price,
            'premium_multiplier': self.V2G_RATE_MULTIPLIER,
            'max_vehicles': self.MAX_V2G_VEHICLES,
            'power_needs': self.substation_power_needs,
            'energy_delivered': self.substation_energy_delivered,
            'energy_required': self.substation_energy_required,
            'average_discharge_rate': self.stats.get('average_discharge_rate_kw', 0),
            'peak_power': self.stats['peak_power_provided_kw'],
            'total_discharge_minutes': self.stats.get('total_discharge_time_minutes', 0),
            'active_vehicles': [
                {
                    'vehicle_id': v_id,
                    'soc': self.sumo_manager.vehicles[v_id].config.current_soc * 100,
                    'earnings': session.earnings,
                    'power_delivered': session.power_delivered_kwh,
                    'substation': session.substation_id,
                    'rate_per_kwh': self.get_current_rate(session.substation_id),
                    'status': 'discharging',
                    'duration': (datetime.now() - session.start_time).seconds,
                    'discharge_rate_kw': session.actual_power_kw,
                    'remaining_energy': (self.sumo_manager.vehicles[v_id].config.current_soc - self.MAX_DISCHARGE_SOC) * 
                                       self.sumo_manager.vehicles[v_id].config.battery_capacity_kwh
                }
                for v_id, session in self.active_sessions.items()
                if v_id in self.sumo_manager.vehicles
            ]
        }