"""
WORLD-CLASS Scenario Controller
Manhattan Power Grid - Dynamic Simulation Control

Features:
- Time-of-day control (0-24 hours)
- Weather/temperature control
- Automatic load updates
- Automatic substation failure on overload
- V2G integration
- Real-time monitoring
"""

import threading
import time
from typing import Dict, List, Any
from datetime import datetime
import numpy as np


class SubstationMonitor:
    """Monitors substation loading and triggers automatic failures"""

    def __init__(self, substation_name: str, capacity_mva: float):
        self.substation_name = substation_name
        self.capacity_mva = capacity_mva
        self.current_load_mw = 0
        self.operational = True

        # Failure thresholds
        self.warning_threshold = 0.85    # 85% capacity
        self.critical_threshold = 0.95   # 95% capacity
        self.failure_threshold = 1.05    # 105% capacity (overload protection trips)

        # Status tracking
        self.status = "NORMAL"  # NORMAL, WARNING, CRITICAL, FAILED
        self.time_above_critical = 0    # Seconds
        self.failure_countdown = 30     # Fails after 30 seconds above 105%

    def update_load(self, load_mw: float) -> Dict[str, Any]:
        """Update load and check for threshold violations"""
        self.current_load_mw = load_mw
        utilization = load_mw / self.capacity_mva

        result = {
            'substation': self.substation_name,
            'load_mw': load_mw,
            'capacity_mva': self.capacity_mva,
            'utilization': utilization,
            'status': self.status,
            'operational': self.operational,
            'alert': None,
            'auto_failed': False
        }

        if not self.operational:
            result['status'] = "FAILED"
            return result

        # Check thresholds
        if utilization >= self.failure_threshold:
            self.time_above_critical += 1
            result['status'] = "OVERLOAD"
            result['alert'] = f"CRITICAL OVERLOAD: {utilization:.1%} - Failure imminent!"

            # Auto-fail after countdown
            if self.time_above_critical >= self.failure_countdown:
                self.operational = False
                self.status = "FAILED"
                result['auto_failed'] = True
                result['alert'] = f"AUTOMATIC FAILURE: Overload protection tripped at {utilization:.1%}"

        elif utilization >= self.critical_threshold:
            self.time_above_critical += 1
            result['status'] = "CRITICAL"
            result['alert'] = f"CRITICAL: {utilization:.1%} capacity - Approaching failure!"

        elif utilization >= self.warning_threshold:
            self.time_above_critical = 0
            result['status'] = "WARNING"
            result['alert'] = f"WARNING: {utilization:.1%} capacity"

        else:
            self.time_above_critical = 0
            result['status'] = "NORMAL"

        self.status = result['status']
        return result

    def reset(self):
        """Reset substation to operational state"""
        self.operational = True
        self.status = "NORMAL"
        self.time_above_critical = 0


class ScenarioController:
    """
    World-class scenario controller for testing Manhattan power grid
    """

    def __init__(self, integrated_system, load_model, power_grid, sumo_manager=None):
        self.integrated_system = integrated_system
        self.load_model = load_model
        self.power_grid = power_grid
        self.sumo_manager = sumo_manager

        # Scenario parameters - REALISTIC TIME SYSTEM
        self.current_time_seconds = 12 * 3600  # Time in seconds since midnight (0-86400)
        self.current_temperature = 72  # Fahrenheit
        self.time_speed = 60.0  # Simulation speed: 60x real-time (1 real second = 1 sim minute)
        self.auto_time_advance = True  # Auto-advance by default for realism
        self.last_update_time = time.time()  # Track real time for realistic progression

        # Substation monitors
        self.substation_monitors: Dict[str, SubstationMonitor] = {}
        self._initialize_monitors()

        # Event log
        self.event_log = []

        # Statistics
        self.stats = {
            'total_failures': 0,
            'total_warnings': 0,
            'peak_load_mw': 0,
            'v2g_activations': 0,
            'scenarios_run': 0
        }

        # Background monitor thread
        self.monitoring = False
        self.monitor_thread = None

        print("✓ Scenario Controller initialized")

    def _initialize_monitors(self):
        """Initialize monitors for all substations"""
        substations = {
            "Hell's Kitchen": 750,
            "Times Square": 800,
            "Penn Station": 700,
            "Grand Central": 850,
            "Murray Hill": 650,
            "Turtle Bay": 600,
            "Chelsea": 700,
            "Midtown East": 750
        }

        for name, capacity in substations.items():
            self.substation_monitors[name] = SubstationMonitor(name, capacity)

    def set_time(self, hour: float, minute: int = 0, second: int = 0):
        """Set simulation time with hours, minutes, and seconds"""
        # Convert to seconds since midnight
        total_seconds = (int(hour) * 3600 + int(minute) * 60 + int(second)) % 86400
        self.current_time_seconds = total_seconds
        self.last_update_time = time.time()  # Reset the update timer

        # Update load model with hour value
        hour_float = self.current_time_seconds / 3600.0
        self.load_model.set_time_of_day(hour_float)
        self._update_all_loads()

        time_str = self._format_time(self.current_time_seconds)
        self._log_event("TIME_CHANGE", f"Time set to {time_str}")

        return {
            'time_seconds': self.current_time_seconds,
            'time_string': time_str,
            'time_description': self._get_time_description()
        }

    def _format_time(self, seconds: int) -> str:
        """Format seconds since midnight as HH:MM:SS"""
        h = int(seconds // 3600) % 24
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_current_time(self) -> dict:
        """Get current time in various formats"""
        return {
            'seconds': self.current_time_seconds,
            'hours': self.current_time_seconds / 3600.0,
            'formatted': self._format_time(self.current_time_seconds),
            'hour': int(self.current_time_seconds // 3600) % 24,
            'minute': int((self.current_time_seconds % 3600) // 60),
            'second': int(self.current_time_seconds % 60)
        }

    def set_temperature(self, temp_f: float):
        """Set current temperature"""
        self.current_temperature = temp_f
        self.load_model.set_temperature(temp_f)
        self._update_all_loads()

        self._log_event("TEMPERATURE_CHANGE", f"Temperature set to {temp_f}°F")

        return {
            'temperature': temp_f,
            'weather': self.load_model.current_weather
        }

    def add_vehicles(self, count: int, ev_percentage: float = 0.7):
        """Add vehicles and update EV charging loads based on actual vehicle count"""

        # Calculate number of EVs
        num_evs = int(count * ev_percentage)

        # Calculate EV charging load per substation
        # Distribute EVs across substations (can be made more sophisticated based on location)
        ev_per_substation = num_evs / 8

        # Realistic EV charging: 30% charging at any time, 150kW average charging power
        charging_fraction = 0.3
        avg_charging_power_kw = 150
        ev_load_per_station = (ev_per_substation * charging_fraction * avg_charging_power_kw) / 1000  # MW

        # Update EV charging loads for all substations
        for substation in self.substation_monitors.keys():
            self.load_model.update_ev_charging_load(substation, ev_load_per_station)

            # Also update integrated_system's EV load (SYNCHRONIZATION FIX)
            if hasattr(self.integrated_system, 'substations') and substation in self.integrated_system.substations:
                self.integrated_system.substations[substation]['ev_load_mw'] = ev_load_per_station

        self._update_all_loads()

        total_ev_load = ev_load_per_station * 8
        self._log_event("VEHICLES_ADDED", f"Added {count} vehicles ({num_evs} EVs), EV charging load: {total_ev_load:.1f} MW")

        return {
            'vehicles': count,
            'num_evs': num_evs,
            'ev_load_per_station_mw': round(ev_load_per_station, 2),
            'total_ev_load_mw': round(total_ev_load, 2)
        }

    def _update_all_loads(self):
        """Update loads for all substations and check for failures"""

        # Calculate loads from model
        substation_loads = self.load_model.calculate_total_load()

        # Update PyPSA network
        for substation, load_mw in substation_loads.items():
            # Update commercial load
            commercial_load_name = f'Commercial_{substation.replace(" ", "_").replace("\'", "")}'
            if commercial_load_name in self.power_grid.network.loads.index:
                self.power_grid.network.loads.at[commercial_load_name, 'p_set'] = load_mw * 0.7

            # Update industrial load
            industrial_load_name = f'Industrial_{substation.replace(" ", "_").replace("\'", "")}'
            if industrial_load_name in self.power_grid.network.loads.index:
                self.power_grid.network.loads.at[industrial_load_name, 'p_set'] = load_mw * 0.3

            # Update integrated_system substations load (SYNCHRONIZATION FIX)
            if hasattr(self.integrated_system, 'substations') and substation in self.integrated_system.substations:
                self.integrated_system.substations[substation]['load_mw'] = load_mw

            # Update monitor and check for failures
            if substation in self.substation_monitors:
                monitor_result = self.substation_monitors[substation].update_load(load_mw)

                # Log alerts
                if monitor_result['alert']:
                    self._log_event("ALERT", monitor_result['alert'])

                # Auto-fail if overloaded
                if monitor_result['auto_failed']:
                    self._trigger_automatic_failure(substation)

                # Update stats
                if monitor_result['status'] in ['WARNING', 'CRITICAL', 'OVERLOAD']:
                    self.stats['total_warnings'] += 1

                if load_mw > self.stats['peak_load_mw']:
                    self.stats['peak_load_mw'] = load_mw

    def _trigger_automatic_failure(self, substation: str):
        """Trigger automatic substation failure due to overload"""

        self.stats['total_failures'] += 1

        # Fail substation in integrated system
        if hasattr(self.integrated_system, 'fail_substation'):
            self.integrated_system.fail_substation(substation)

        # Clear loads in load model (no power = no consumption)
        if hasattr(self.load_model, 'clear_substation_load'):
            self.load_model.clear_substation_load(substation)

        # Fail in power grid
        if hasattr(self.power_grid, 'trigger_failure'):
            self.power_grid.trigger_failure('substation', substation, cascading=True)

        # Handle EV station blackout - stop charging and reroute vehicles (CRITICAL FIX)
        if self.sumo_manager and hasattr(self.sumo_manager, 'station_manager'):
            if self.sumo_manager.station_manager:
                released_vehicles = self.sumo_manager.station_manager.handle_blackout(substation)
                if released_vehicles:
                    print(f"   ⚡ {len(released_vehicles)} EVs interrupted - rerouting to other stations")

        self._log_event("AUTOMATIC_FAILURE",
                       f"{substation} FAILED due to overload - Protection tripped!")

        print(f"⚠️  AUTOMATIC FAILURE: {substation} - Overload protection activated")

    def restore_substation(self, substation: str):
        """Manually restore a failed substation"""

        if substation in self.substation_monitors:
            self.substation_monitors[substation].reset()

        # Restore in power grid
        if hasattr(self.power_grid, 'restore_component'):
            self.power_grid.restore_component('substation', substation)

        # Restore in integrated system
        if hasattr(self.integrated_system, 'restore_substation'):
            self.integrated_system.restore_substation(substation)

        # Restore EV stations connected to this substation (CRITICAL FIX)
        if self.sumo_manager and hasattr(self.sumo_manager, 'station_manager'):
            if self.sumo_manager.station_manager:
                restored_stations = self.sumo_manager.station_manager.restore_power(substation)
                if restored_stations:
                    print(f"   ⚡ EV stations restored: {', '.join(restored_stations)}")

        self._log_event("RESTORATION", f"{substation} restored to service")

        return {'status': 'restored', 'substation': substation}

    def run_scenario(self, scenario_name: str, **params) -> Dict[str, Any]:
        """Run predefined test scenarios"""

        self.stats['scenarios_run'] += 1
        scenario_result = {
            'scenario': scenario_name,
            'start_time': datetime.now().isoformat(),
            'events': [],
            'final_status': {}
        }

        if scenario_name == "rush_hour_stress_test":
            # Morning rush hour + hot day + 100 EVs
            self.set_time(8.0)
            self.set_temperature(92)
            self.add_vehicles(100)
            scenario_result['events'].append("Set to 8:00 AM rush hour")
            scenario_result['events'].append("Set temperature to 92°F (extreme heat)")
            scenario_result['events'].append("Added 100 vehicles")

        elif scenario_name == "evening_peak_v2g":
            # Evening peak + normal weather + test V2G
            self.set_time(18.0)
            self.set_temperature(75)
            self.add_vehicles(80)
            scenario_result['events'].append("Set to 6:00 PM evening peak")
            scenario_result['events'].append("Optimal conditions for V2G testing")

        elif scenario_name == "winter_emergency":
            # Early morning + extreme cold + high load
            self.set_time(7.0)
            self.set_temperature(15)
            self.add_vehicles(60)
            scenario_result['events'].append("Set to 7:00 AM winter morning")
            scenario_result['events'].append("Set temperature to 15°F (extreme cold)")
            scenario_result['events'].append("High heating load expected")

        elif scenario_name == "summer_heatwave":
            # Afternoon + extreme heat + max AC load
            self.set_time(15.0)
            self.set_temperature(98)
            self.add_vehicles(90)
            scenario_result['events'].append("Set to 3:00 PM hottest time")
            scenario_result['events'].append("Set temperature to 98°F (heatwave)")
            scenario_result['events'].append("Maximum AC load")

        elif scenario_name == "heatwave_crisis":
            # Same as summer_heatwave but with consistent naming
            self.set_time(15.0)
            self.set_temperature(98)
            self.add_vehicles(90)
            scenario_result['events'].append("Set to 3:00 PM hottest time")
            scenario_result['events'].append("Set temperature to 98°F (heatwave)")
            scenario_result['events'].append("EXTREME CONDITIONS - Multiple failures expected")

        elif scenario_name == "catastrophic_heat":
            # CATASTROPHIC temperature + peak hour + heavy traffic
            self.set_time(14.0)
            self.set_temperature(115)
            self.add_vehicles(100)
            scenario_result['events'].append("Set to 2:00 PM peak solar heating")
            scenario_result['events'].append("Set temperature to 115°F (CATASTROPHIC)")
            scenario_result['events'].append("⚠️ MASS FAILURES IMMINENT - Grid near collapse!")

        elif scenario_name == "late_night_low_load":
            # Late night + mild weather + minimal vehicles
            self.set_time(3.0)
            self.set_temperature(65)
            self.add_vehicles(20)
            scenario_result['events'].append("Set to 3:00 AM late night")
            scenario_result['events'].append("Minimal load conditions")

        else:
            scenario_result['error'] = f"Unknown scenario: {scenario_name}"
            return scenario_result

        # Get final status
        scenario_result['final_status'] = self.get_system_status()

        self._log_event("SCENARIO_COMPLETE", f"Completed scenario: {scenario_name}")

        return scenario_result

    def start_auto_monitoring(self):
        """Start automatic monitoring in background"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("✓ Automatic monitoring started")

    def stop_auto_monitoring(self):
        """Stop automatic monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("✓ Automatic monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop with realistic time progression"""
        while self.monitoring:
            try:
                # Calculate elapsed real time
                current_real_time = time.time()
                elapsed_real_seconds = current_real_time - self.last_update_time
                self.last_update_time = current_real_time

                # Auto-advance time if enabled
                if self.auto_time_advance:
                    # Add simulated time based on speed multiplier
                    sim_seconds_to_add = elapsed_real_seconds * self.time_speed
                    self.current_time_seconds = int(self.current_time_seconds + sim_seconds_to_add) % 86400

                    # Update load model with current hour
                    hour_float = self.current_time_seconds / 3600.0
                    self.load_model.set_time_of_day(hour_float)

                self._update_all_loads()

                time.sleep(1)  # Update every real second

            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""

        substation_status = {}
        for name, monitor in self.substation_monitors.items():
            substation_status[name] = {
                'operational': monitor.operational,
                'status': monitor.status,
                'load_mw': round(monitor.current_load_mw, 2),
                'capacity_mva': monitor.capacity_mva,
                'utilization': round(monitor.current_load_mw / monitor.capacity_mva * 100, 1),
                'time_above_critical': monitor.time_above_critical
            }

        time_info = self.get_current_time()
        return {
            'time_seconds': self.current_time_seconds,
            'time_formatted': time_info['formatted'],
            'time_hour': time_info['hour'],
            'time_minute': time_info['minute'],
            'time_second': time_info['second'],
            'time_description': self._get_time_description(),
            'time_speed': self.time_speed,
            'auto_advance': self.auto_time_advance,
            'temperature_f': self.current_temperature,
            'weather': self.load_model.current_weather,
            'substations': substation_status,
            'statistics': self.stats,
            'recommendations': self.load_model.get_scenario_recommendations()
        }

    def get_load_forecast(self, hours_ahead: int = 6) -> List[Dict[str, Any]]:
        """Forecast loads for next N hours"""

        forecast = []
        current_temp = self.current_temperature
        current_hour = self.current_time_seconds / 3600.0

        for h in range(hours_ahead):
            future_time = (current_hour + h) % 24

            # Temporarily set time
            original_time = current_hour
            self.load_model.set_time_of_day(future_time)

            # Calculate loads
            loads = self.load_model.calculate_total_load()

            forecast.append({
                'hour': future_time,
                'time_description': self._get_time_description(future_time),
                'loads': loads,
                'total_load_mw': sum(loads.values()),
                'peak_substation': max(loads, key=loads.get),
                'peak_load_mw': max(loads.values())
            })

            # Restore time
            self.load_model.set_time_of_day(original_time)

        return forecast

    def _get_time_description(self, hour: float = None) -> str:
        """Get human-readable time description"""
        if hour is None:
            hour = self.current_time_seconds / 3600.0

        if 0 <= hour < 6:
            return "Late Night / Early Morning"
        elif 6 <= hour < 9:
            return "Morning Rush Hour"
        elif 9 <= hour < 12:
            return "Mid Morning"
        elif 12 <= hour < 14:
            return "Lunch Hour"
        elif 14 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 19:
            return "Evening Rush Hour"
        elif 19 <= hour < 22:
            return "Evening"
        else:
            return "Night"

    def _log_event(self, event_type: str, description: str):
        """Log system events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'description': description,
            'time': self.current_time,
            'temperature': self.current_temperature
        }
        self.event_log.append(event)

        # Keep last 1000 events
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]

    def get_event_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self.event_log[-limit:]

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data for dashboard display"""

        return {
            'status': self.get_system_status(),
            'recent_events': self.get_event_log(20),
            'load_forecast': self.get_load_forecast(6),
            'statistics': self.stats,
            'monitoring': self.monitoring
        }
