"""
WORLD-CLASS Realistic Load Modeling System
Manhattan Power Grid - Physics-Based Load Calculations

Features:
- Building types with realistic power consumption
- Time-of-day load curves
- Weather impact (temperature-based AC/heating)
- EV charging integration
- Zone-based distribution
- Automatic substation failure detection
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
import json


class BuildingType(Enum):
    """Manhattan building types"""
    OFFICE_TOWER = "office_tower"           # 40-60 floors
    COMMERCIAL = "commercial"                # Shops, restaurants
    RESIDENTIAL_HIGHRISE = "residential_highrise"  # Luxury apartments
    RESIDENTIAL_MIDRISE = "residential_midrise"    # 10-20 floors
    HOTEL = "hotel"                         # Hotels
    HOSPITAL = "hospital"                   # Medical facilities
    DATA_CENTER = "data_center"             # Data centers (high load)
    RETAIL = "retail"                       # Street-level retail
    ENTERTAINMENT = "entertainment"          # Theaters, venues
    TRANSPORTATION = "transportation"        # Stations, terminals


class ManhattanZone(Enum):
    """Manhattan zones with different characteristics"""
    MIDTOWN_CORE = "midtown_core"           # Times Square, Grand Central
    FINANCIAL = "financial"                  # Lower Manhattan
    RESIDENTIAL_UPPER = "residential_upper"  # Upper East/West Side
    MIXED_USE = "mixed_use"                 # Chelsea, Flatiron
    TRANSIT_HUB = "transit_hub"             # Penn Station, Port Authority


@dataclass
class BuildingLoad:
    """Represents a building's power consumption"""
    building_id: str
    building_type: BuildingType
    zone: ManhattanZone
    substation: str
    floor_count: int
    floor_area_sqft: float

    # Power consumption (kW)
    base_load_kw: float = 0
    hvac_load_kw: float = 0
    lighting_load_kw: float = 0
    equipment_load_kw: float = 0

    # Occupancy
    current_occupancy: float = 0.5  # 0-1
    max_occupancy: int = 1000

    # Coordinates
    lat: float = 40.755
    lon: float = -73.985


@dataclass
class ZoneCharacteristics:
    """Zone-specific characteristics"""
    zone: ManhattanZone
    office_density: float       # 0-1
    residential_density: float  # 0-1
    commercial_density: float   # 0-1
    peak_hour_multiplier: float
    base_load_mw: float


class RealisticLoadModel:
    """
    World-class load modeling system for Manhattan power grid
    Based on actual Con Edison data and DOE building energy models
    """

    def __init__(self, integrated_system):
        self.integrated_system = integrated_system

        # Current scenario parameters
        self.current_time_of_day = 12.0  # Hour (0-24)
        self.current_temperature_f = 72  # Fahrenheit
        self.current_weather = "clear"   # clear, hot, cold, extreme_heat, extreme_cold

        # Gradual load transition (for smooth, realistic changes)
        self.target_loads = {}  # Target loads we're transitioning to
        self.current_loads = {}  # Current actual loads (smoothly transitioning)
        self.transition_rate = 0.05  # 5% of delta per update (SLOW, realistic - 20-30 seconds to stabilize)

        # AC/Heating ramp-up state (buildings don't instantly hit max AC!)
        self.hvac_ramp_state = {}  # Track how much HVAC has ramped up (0.0 to 1.0)
        self.hvac_ramp_rate = 0.01  # 1% per second = 100 seconds (1.7 minutes) to full AC
        self.last_temperature = 72  # Track temperature changes to trigger ramp-up

        # Building database
        self.buildings: Dict[str, BuildingLoad] = {}

        # Zone definitions
        self.zones = self._define_manhattan_zones()

        # Power consumption standards (kW per sqft)
        self.building_standards = self._define_building_standards()

        # Time-of-day multipliers
        self.time_curves = self._define_time_curves()

        # Temperature response curves
        self.temperature_curves = self._define_temperature_curves()

        # EV charging loads
        self.ev_charging_loads = {}

        # Initialize Manhattan building stock
        self._generate_manhattan_buildings()

        print(f"✓ Realistic Load Model initialized with {len(self.buildings)} buildings")

    def _define_manhattan_zones(self) -> Dict[ManhattanZone, ZoneCharacteristics]:
        """Define Manhattan zones and their characteristics"""
        return {
            ManhattanZone.MIDTOWN_CORE: ZoneCharacteristics(
                zone=ManhattanZone.MIDTOWN_CORE,
                office_density=1.0,  # MAXIMUM DENSITY - Times Square, Grand Central, Midtown East
                residential_density=0.1,
                commercial_density=0.3,
                peak_hour_multiplier=2.2,  # Peak hours hit HARD
                base_load_mw=200  # Higher base load
            ),
            ManhattanZone.FINANCIAL: ZoneCharacteristics(
                zone=ManhattanZone.FINANCIAL,
                office_density=0.9,
                residential_density=0.05,
                commercial_density=0.2,
                peak_hour_multiplier=2.0,
                base_load_mw=150
            ),
            ManhattanZone.RESIDENTIAL_UPPER: ZoneCharacteristics(
                zone=ManhattanZone.RESIDENTIAL_UPPER,
                office_density=0.15,  # LOW office density
                residential_density=0.85,  # HIGH residential
                commercial_density=0.1,
                peak_hour_multiplier=1.2,  # Lower peak multiplier
                base_load_mw=60  # Lower base load
            ),
            ManhattanZone.MIXED_USE: ZoneCharacteristics(
                zone=ManhattanZone.MIXED_USE,
                office_density=0.5,
                residential_density=0.4,
                commercial_density=0.25,
                peak_hour_multiplier=1.6,
                base_load_mw=120
            ),
            ManhattanZone.TRANSIT_HUB: ZoneCharacteristics(
                zone=ManhattanZone.TRANSIT_HUB,
                office_density=0.4,
                residential_density=0.1,
                commercial_density=0.7,  # Lots of retail/shops
                peak_hour_multiplier=2.0,  # Rush hour spikes
                base_load_mw=110
            )
        }

    def _define_building_standards(self) -> Dict[BuildingType, Dict[str, float]]:
        """Define power consumption standards (based on DOE Commercial Building Energy Survey)"""
        return {
            BuildingType.OFFICE_TOWER: {
                'base_w_per_sqft': 3.5,      # Base load
                'hvac_w_per_sqft': 2.0,      # HVAC
                'lighting_w_per_sqft': 1.2,  # Lighting
                'equipment_w_per_sqft': 2.5, # Computers, elevators
                'occupancy_factor': 0.7      # Peak occupancy effect
            },
            BuildingType.COMMERCIAL: {
                'base_w_per_sqft': 2.5,
                'hvac_w_per_sqft': 1.5,
                'lighting_w_per_sqft': 2.0,
                'equipment_w_per_sqft': 1.0,
                'occupancy_factor': 0.8
            },
            BuildingType.RESIDENTIAL_HIGHRISE: {
                'base_w_per_sqft': 1.5,
                'hvac_w_per_sqft': 1.0,
                'lighting_w_per_sqft': 0.8,
                'equipment_w_per_sqft': 1.2,
                'occupancy_factor': 0.6
            },
            BuildingType.RESIDENTIAL_MIDRISE: {
                'base_w_per_sqft': 1.2,
                'hvac_w_per_sqft': 0.8,
                'lighting_w_per_sqft': 0.6,
                'equipment_w_per_sqft': 1.0,
                'occupancy_factor': 0.6
            },
            BuildingType.HOTEL: {
                'base_w_per_sqft': 3.0,
                'hvac_w_per_sqft': 2.5,
                'lighting_w_per_sqft': 1.5,
                'equipment_w_per_sqft': 1.5,
                'occupancy_factor': 0.7
            },
            BuildingType.HOSPITAL: {
                'base_w_per_sqft': 5.0,      # 24/7 operation
                'hvac_w_per_sqft': 3.0,
                'lighting_w_per_sqft': 2.0,
                'equipment_w_per_sqft': 4.0, # Medical equipment
                'occupancy_factor': 0.95     # Always high
            },
            BuildingType.DATA_CENTER: {
                'base_w_per_sqft': 50.0,     # Extremely high!
                'hvac_w_per_sqft': 25.0,     # Cooling critical
                'lighting_w_per_sqft': 1.0,
                'equipment_w_per_sqft': 75.0,# Servers
                'occupancy_factor': 0.98     # Constant
            },
            BuildingType.RETAIL: {
                'base_w_per_sqft': 2.0,
                'hvac_w_per_sqft': 1.5,
                'lighting_w_per_sqft': 2.5,  # Display lighting
                'equipment_w_per_sqft': 1.0,
                'occupancy_factor': 0.6
            },
            BuildingType.ENTERTAINMENT: {
                'base_w_per_sqft': 3.5,
                'hvac_w_per_sqft': 2.0,
                'lighting_w_per_sqft': 3.0,  # Stage lighting
                'equipment_w_per_sqft': 2.5, # Sound systems
                'occupancy_factor': 0.5      # Event-based
            },
            BuildingType.TRANSPORTATION: {
                'base_w_per_sqft': 4.0,
                'hvac_w_per_sqft': 2.5,
                'lighting_w_per_sqft': 2.0,
                'equipment_w_per_sqft': 3.0, # Escalators, displays
                'occupancy_factor': 0.8
            }
        }

    def _define_time_curves(self) -> Dict[BuildingType, List[float]]:
        """Define 24-hour load curves for each building type"""
        return {
            BuildingType.OFFICE_TOWER: [
                0.3, 0.3, 0.3, 0.3, 0.3, 0.4,  # 00:00-05:00 (night - minimal)
                0.6, 0.8, 0.9, 1.0, 1.0, 1.0,  # 06:00-11:00 (morning ramp-up to peak)
                1.0, 1.0, 0.9, 0.9, 0.8, 0.6,  # 12:00-17:00 (afternoon peak, evening ramp-down)
                0.5, 0.4, 0.4, 0.3, 0.3, 0.3   # 18:00-23:00 (evening - cleaning crews)
            ],
            BuildingType.COMMERCIAL: [
                0.2, 0.2, 0.2, 0.2, 0.2, 0.3,
                0.5, 0.7, 0.8, 0.9, 1.0, 1.0,
                1.0, 0.9, 0.9, 0.9, 0.8, 0.7,
                0.7, 0.6, 0.5, 0.4, 0.3, 0.2
            ],
            BuildingType.RESIDENTIAL_HIGHRISE: [
                0.5, 0.5, 0.5, 0.5, 0.5, 0.6,  # Night - people sleeping
                0.7, 0.8, 0.7, 0.5, 0.4, 0.4,  # Morning rush then empty
                0.4, 0.4, 0.5, 0.6, 0.7, 0.8,  # Afternoon - people return
                0.9, 1.0, 0.9, 0.8, 0.7, 0.6   # Evening peak - cooking, TV
            ],
            BuildingType.RESIDENTIAL_MIDRISE: [
                0.5, 0.5, 0.5, 0.5, 0.5, 0.6,
                0.7, 0.8, 0.7, 0.5, 0.4, 0.4,
                0.4, 0.4, 0.5, 0.6, 0.7, 0.8,
                0.9, 1.0, 0.9, 0.8, 0.7, 0.6
            ],
            BuildingType.HOTEL: [
                0.6, 0.5, 0.5, 0.5, 0.5, 0.6,
                0.7, 0.8, 0.8, 0.8, 0.8, 0.9,
                0.9, 0.9, 0.9, 0.9, 0.9, 1.0,
                1.0, 0.9, 0.8, 0.7, 0.7, 0.6
            ],
            BuildingType.HOSPITAL: [
                0.9, 0.9, 0.9, 0.9, 0.9, 0.9,  # 24/7 operation
                0.95, 1.0, 1.0, 1.0, 1.0, 1.0,
                1.0, 1.0, 1.0, 1.0, 0.95, 0.95,
                0.95, 0.95, 0.9, 0.9, 0.9, 0.9
            ],
            BuildingType.DATA_CENTER: [
                0.98, 0.98, 0.98, 0.98, 0.98, 0.98,  # Nearly constant
                0.98, 0.99, 1.0, 1.0, 1.0, 1.0,
                1.0, 1.0, 1.0, 1.0, 1.0, 0.99,
                0.99, 0.99, 0.98, 0.98, 0.98, 0.98
            ],
            BuildingType.RETAIL: [
                0.2, 0.2, 0.2, 0.2, 0.2, 0.3,
                0.4, 0.5, 0.6, 0.8, 1.0, 1.0,
                1.0, 1.0, 0.9, 0.9, 0.8, 0.8,
                0.7, 0.6, 0.5, 0.4, 0.3, 0.2
            ],
            BuildingType.ENTERTAINMENT: [
                0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                0.3, 0.3, 0.4, 0.5, 0.6, 0.7,
                0.8, 0.8, 0.9, 0.9, 0.9, 1.0,
                1.0, 1.0, 0.9, 0.7, 0.5, 0.3
            ],
            BuildingType.TRANSPORTATION: [
                0.4, 0.3, 0.3, 0.3, 0.4, 0.6,  # Early morning trains
                0.9, 1.0, 1.0, 0.9, 0.8, 0.8,  # Rush hour
                0.8, 0.8, 0.8, 0.9, 0.9, 1.0,  # Evening rush
                0.9, 0.8, 0.7, 0.6, 0.5, 0.4
            ]
        }

    def _define_temperature_curves(self) -> Dict[str, Any]:
        """
        Define how temperature affects load - PHYSICS-BASED HVAC MODELING
        Based on actual ASHRAE standards and Con Edison load studies
        Extended range: 10°F to 120°F for extreme scenario testing
        """
        return {
            # Comfort zone parameters
            'cooling_balance_f': 70,  # Temperature where AC starts (comfort threshold)
            'heating_balance_f': 65,  # Temperature where heating starts

            # Cooling load calculation (based on cooling degree days)
            # Formula: AC Load = Base_HVAC * (1 + CDD_factor * (T - balance)^1.3)
            # The exponent 1.3 models non-linear AC power consumption as compressor works harder
            'cooling_base_factor': 0.015,      # Moderate AC load increase per °F
            'cooling_curve_exponent': 1.25,    # Non-linear increase (physics-based)

            # Multi-tier extreme heat thresholds
            'extreme_heat_threshold': 90,      # Extreme heat starts (>90°F)
            'extreme_heat_cop_degradation': 0.25,  # 25% efficiency loss at 90°F

            'critical_heat_threshold': 100,    # Critical heat (>100°F)
            'critical_heat_cop_degradation': 0.45,  # 45% efficiency loss at 100°F

            'catastrophic_heat_threshold': 110,  # Catastrophic heat (>110°F)
            'catastrophic_heat_multiplier': 1.8,  # 80% additional load at 110°F+

            # At 120°F: Near-total grid failure expected
            # AC units struggle, buildings become heat sinks, infrastructure fails

            # Heating load calculation (similar but different curve)
            'heating_base_factor': 0.012,      # Heating is more efficient than cooling
            'heating_curve_exponent': 1.15,

            # Extreme cold effects
            'extreme_cold_threshold': 20,
            'extreme_cold_efficiency_loss': 0.20,  # 20% efficiency loss in extreme cold

            # Thermal mass and building envelope effects
            'thermal_lag_hours': 2,  # Buildings take time to heat up/cool down
            'envelope_efficiency': 0.85,  # NYC buildings ~85% as efficient as modern code

            # Peak diversity factor (not all ACs reach max at same time)
            'diversity_factor': 0.92  # 92% simultaneous peak
        }

    def _generate_manhattan_buildings(self):
        """Generate realistic Manhattan building stock"""

        # Map substations to zones
        substation_zones = {
            "Hell's Kitchen": ManhattanZone.MIXED_USE,
            "Times Square": ManhattanZone.MIDTOWN_CORE,
            "Penn Station": ManhattanZone.TRANSIT_HUB,
            "Grand Central": ManhattanZone.MIDTOWN_CORE,
            "Murray Hill": ManhattanZone.MIXED_USE,
            "Turtle Bay": ManhattanZone.RESIDENTIAL_UPPER,
            "Chelsea": ManhattanZone.MIXED_USE,
            "Midtown East": ManhattanZone.MIDTOWN_CORE
        }

        # Generate buildings for each substation
        # CALIBRATED: Normal conditions (72°F, 12PM) → 55-65% capacity
        #            Moderate heat (85°F) → 75-85% capacity
        #            Extreme heat (98°F) → 95-110% capacity (failures)
        building_id = 1
        for substation, zone in substation_zones.items():
            zone_char = self.zones[zone]

            # Office towers - CALIBRATED for realistic Manhattan density
            # Reduced from 42 to 35 to prevent normal-condition failures
            num_offices = int(35 * zone_char.office_density)
            for i in range(num_offices):
                self._create_building(
                    building_id, BuildingType.OFFICE_TOWER, zone,
                    substation, floors=np.random.randint(30, 60),
                    sqft_per_floor=38000  # Slightly reduced from 40k
                )
                building_id += 1

            # Commercial buildings - reduced density
            num_commercial = int(45 * zone_char.commercial_density)  # Reduced from 55
            for i in range(num_commercial):
                self._create_building(
                    building_id, BuildingType.COMMERCIAL, zone,
                    substation, floors=np.random.randint(2, 5),
                    sqft_per_floor=9000  # Slightly reduced
                )
                building_id += 1

            # Residential - balanced for evening peaks
            num_residential = int(40 * zone_char.residential_density)  # Reduced from 48
            for i in range(num_residential):
                btype = BuildingType.RESIDENTIAL_HIGHRISE if np.random.random() < 0.6 else BuildingType.RESIDENTIAL_MIDRISE
                self._create_building(
                    building_id, btype, zone,
                    substation, floors=np.random.randint(15, 40),
                    sqft_per_floor=18000  # Reduced from 20k
                )
                building_id += 1

            # Special buildings
            if zone == ManhattanZone.MIDTOWN_CORE:
                # Add hotels
                for i in range(3):
                    self._create_building(
                        building_id, BuildingType.HOTEL, zone,
                        substation, floors=40, sqft_per_floor=30000
                    )
                    building_id += 1

                # Add entertainment venues
                for i in range(2):
                    self._create_building(
                        building_id, BuildingType.ENTERTAINMENT, zone,
                        substation, floors=5, sqft_per_floor=50000
                    )
                    building_id += 1

            if zone == ManhattanZone.TRANSIT_HUB:
                # Add transportation hubs
                self._create_building(
                    building_id, BuildingType.TRANSPORTATION, zone,
                    substation, floors=3, sqft_per_floor=100000
                )
                building_id += 1

            # Add one data center per zone (high impact!)
            if np.random.random() < 0.3:
                self._create_building(
                    building_id, BuildingType.DATA_CENTER, zone,
                    substation, floors=5, sqft_per_floor=50000
                )
                building_id += 1

            # Add hospital if residential
            if zone_char.residential_density > 0.5:
                self._create_building(
                    building_id, BuildingType.HOSPITAL, zone,
                    substation, floors=15, sqft_per_floor=40000
                )
                building_id += 1

        print(f"  Generated {len(self.buildings)} buildings across 8 substations")

    def _create_building(self, building_id: int, btype: BuildingType, zone: ManhattanZone,
                        substation: str, floors: int, sqft_per_floor: float):
        """Create a building with calculated loads"""

        standards = self.building_standards[btype]
        total_sqft = floors * sqft_per_floor

        # Calculate base loads (convert W to kW)
        base_load = (standards['base_w_per_sqft'] * total_sqft) / 1000
        hvac_load = (standards['hvac_w_per_sqft'] * total_sqft) / 1000
        lighting_load = (standards['lighting_w_per_sqft'] * total_sqft) / 1000
        equipment_load = (standards['equipment_w_per_sqft'] * total_sqft) / 1000

        building = BuildingLoad(
            building_id=f"B{building_id}",
            building_type=btype,
            zone=zone,
            substation=substation,
            floor_count=floors,
            floor_area_sqft=total_sqft,
            base_load_kw=base_load,
            hvac_load_kw=hvac_load,
            lighting_load_kw=lighting_load,
            equipment_load_kw=equipment_load,
            current_occupancy=standards['occupancy_factor']
        )

        self.buildings[building.building_id] = building

    def calculate_total_load(self) -> Dict[str, float]:
        """
        Calculate total load for each substation with REALISTIC GRADUAL INCREASES
        - Time of day
        - Weather/temperature (AC RAMPS UP SLOWLY!)
        - Occupancy
        - EV charging
        - EVERYTHING increases gradually and visibly
        - CRITICAL: Failed substations have ZERO load (no power = no consumption)
        """

        # Update HVAC ramp state for each substation
        self._update_hvac_ramp_state()

        # Calculate TARGET loads (what we want to reach)
        target_substation_loads = {
            "Hell's Kitchen": 0,
            "Times Square": 0,
            "Penn Station": 0,
            "Grand Central": 0,
            "Murray Hill": 0,
            "Turtle Bay": 0,
            "Chelsea": 0,
            "Midtown East": 0
        }

        # Get time multiplier (0-23 hours)
        hour = int(self.current_time_of_day) % 24

        # Calculate TARGET load for each building
        for building in self.buildings.values():
            substation = building.substation

            # CRITICAL FIX: Check if substation is operational
            # If substation failed, NO POWER = NO LOAD
            is_operational = self._is_substation_operational(substation)

            if not is_operational:
                # Substation is failed - no load consumption
                # (Everything is off, no AC, no lights, no equipment)
                continue

            # Get time-of-day multiplier
            time_curve = self.time_curves[building.building_type]
            time_multiplier = time_curve[hour]

            # Get temperature multiplier (MAXIMUM potential)
            max_temp_multiplier = self._calculate_temperature_multiplier(
                building.building_type, building.floor_area_sqft
            )

            # Apply HVAC ramp state - AC doesn't go to max instantly!
            hvac_ramp = self.hvac_ramp_state.get(substation, 0.0)
            actual_temp_multiplier = 1.0 + ((max_temp_multiplier - 1.0) * hvac_ramp)

            # Calculate total building load with RAMPED HVAC
            total_load_kw = (
                building.base_load_kw +
                (building.hvac_load_kw * actual_temp_multiplier) +  # GRADUAL!
                (building.lighting_load_kw * time_multiplier) +
                (building.equipment_load_kw * time_multiplier * building.current_occupancy)
            )

            # Apply time multiplier to total
            total_load_kw *= time_multiplier

            # Add to TARGET substation (convert kW to MW)
            target_substation_loads[building.substation] += total_load_kw / 1000

        # Add EV charging loads to TARGET (only if substation operational)
        for substation, ev_load_mw in self.ev_charging_loads.items():
            if substation in target_substation_loads:
                # Check if substation is operational before adding EV load
                if self._is_substation_operational(substation):
                    target_substation_loads[substation] += ev_load_mw

        # GRADUAL TRANSITION - Smoothly move current loads toward target loads
        # This creates realistic, incremental changes over 20-30 seconds
        for substation in target_substation_loads.keys():
            target_load = target_substation_loads[substation]

            # Initialize current load if first time
            if substation not in self.current_loads:
                self.current_loads[substation] = target_load

            current_load = self.current_loads[substation]
            delta = target_load - current_load

            # Move 5% of the way toward target each update (every 1 second)
            # This creates smooth transitions over ~20-30 seconds
            self.current_loads[substation] = current_load + (delta * self.transition_rate)

        return self.current_loads.copy()

    def _is_substation_operational(self, substation_name: str) -> bool:
        """
        Check if a substation is operational
        Returns True if operational, False if failed
        """
        # Check in integrated_system if it exists
        if hasattr(self.integrated_system, 'substations'):
            if substation_name in self.integrated_system.substations:
                return self.integrated_system.substations[substation_name].get('operational', True)

        # Default to operational if we can't determine status
        return True

    def _update_hvac_ramp_state(self):
        """
        Update HVAC ramp-up state for each substation
        AC/Heating doesn't instantly go to max - it ramps up over 1-2 minutes
        """
        temp_params = self.temperature_curves
        cooling_balance = temp_params['cooling_balance_f']
        heating_balance = temp_params['heating_balance_f']
        current_temp = self.current_temperature_f

        # Determine if HVAC is needed (outside comfort zone)
        hvac_needed = (current_temp > cooling_balance) or (current_temp < heating_balance)

        # Update ramp state for each substation
        for substation in ["Hell's Kitchen", "Times Square", "Penn Station", "Grand Central",
                          "Murray Hill", "Turtle Bay", "Chelsea", "Midtown East"]:

            if substation not in self.hvac_ramp_state:
                self.hvac_ramp_state[substation] = 0.0

            current_ramp = self.hvac_ramp_state[substation]

            if hvac_needed:
                # Ramp UP - increase by 1% per second
                # Takes 100 seconds (1.7 minutes) to reach full capacity
                new_ramp = min(1.0, current_ramp + self.hvac_ramp_rate)
            else:
                # Ramp DOWN - decrease when not needed
                new_ramp = max(0.0, current_ramp - (self.hvac_ramp_rate * 2))  # Ramp down 2x faster

            self.hvac_ramp_state[substation] = new_ramp

    def _calculate_temperature_multiplier(self, building_type: BuildingType, sqft: float) -> float:
        """
        Calculate temperature-based HVAC load multiplier using PHYSICS-BASED equations

        Based on:
        - Cooling/Heating Degree Days (CDD/HDD)
        - Non-linear compressor power consumption
        - COP (Coefficient of Performance) degradation in extreme temps
        - Building thermal characteristics
        """

        temp_params = self.temperature_curves
        current_temp = self.current_temperature_f
        cooling_balance = temp_params['cooling_balance_f']
        heating_balance = temp_params['heating_balance_f']

        multiplier = 1.0

        # COOLING MODE (Temperature above comfort zone)
        if current_temp > cooling_balance:
            # Calculate temperature delta from balance point
            delta_t = current_temp - cooling_balance

            # Non-linear cooling load increase (compressor power increases exponentially)
            # Formula: 1 + factor * (ΔT)^exponent
            # This models how AC compressors work harder (more power) at higher temps
            base_increase = temp_params['cooling_base_factor'] * (
                delta_t ** temp_params['cooling_curve_exponent']
            )

            multiplier = 1.0 + base_increase

            # MULTI-TIER EXTREME HEAT HANDLING
            # Each tier represents increasingly severe grid stress conditions

            # TIER 1: CATASTROPHIC HEAT (>110°F) - Near-total failure conditions
            if current_temp >= temp_params['catastrophic_heat_threshold']:
                catastrophic_delta = current_temp - temp_params['catastrophic_heat_threshold']

                # Massive COP degradation + infrastructure stress
                # At 120°F, expect 150-180% of normal peak load
                multiplier *= temp_params['catastrophic_heat_multiplier']

                # Additional penalties per degree above 110°F
                # Buildings become heat sinks, AC units fail, transformers overheat
                additional_penalty = catastrophic_delta * 0.04  # 4% per degree
                multiplier *= (1 + additional_penalty)

                # Envelope heat gain is severe
                envelope_load = temp_params['envelope_efficiency'] * (catastrophic_delta / 50)
                multiplier += envelope_load

                print(f"⚠️ CATASTROPHIC HEAT: {current_temp}°F - Grid failure imminent!")

            # TIER 2: CRITICAL HEAT (100-110°F) - Severe stress
            elif current_temp >= temp_params['critical_heat_threshold']:
                critical_delta = current_temp - temp_params['critical_heat_threshold']

                # 45% COP degradation at 100°F
                cop_penalty = temp_params['critical_heat_cop_degradation'] * (
                    1 + (critical_delta / 8)  # Gets worse for each 8°F
                )
                multiplier *= (1 + cop_penalty)

                # Envelope heat gain
                envelope_load = temp_params['envelope_efficiency'] * (critical_delta / 80)
                multiplier += envelope_load

            # TIER 3: EXTREME HEAT (90-100°F) - High stress
            elif current_temp >= temp_params['extreme_heat_threshold']:
                extreme_delta = current_temp - temp_params['extreme_heat_threshold']

                # 25% COP degradation at 90°F
                cop_penalty = temp_params['extreme_heat_cop_degradation'] * (
                    1 + (extreme_delta / 10)  # Gets worse for each 10°F
                )
                multiplier *= (1 + cop_penalty)

                # Building envelope heat gain
                envelope_load = temp_params['envelope_efficiency'] * (extreme_delta / 100)
                multiplier += envelope_load

        # HEATING MODE (Temperature below comfort zone)
        elif current_temp < heating_balance:
            # Calculate temperature delta from balance point
            delta_t = heating_balance - current_temp

            # Non-linear heating load increase (but less steep than cooling)
            base_increase = temp_params['heating_base_factor'] * (
                delta_t ** temp_params['heating_curve_exponent']
            )

            multiplier = 1.0 + base_increase

            # EXTREME COLD: Heat pump efficiency loss
            if current_temp < temp_params['extreme_cold_threshold']:
                extreme_delta = temp_params['extreme_cold_threshold'] - current_temp
                efficiency_penalty = temp_params['extreme_cold_efficiency_loss'] * (
                    1 + (extreme_delta / 15)
                )
                multiplier *= (1 + efficiency_penalty)

        # Apply diversity factor (not all HVAC units peak simultaneously)
        multiplier *= temp_params['diversity_factor']

        # Building type adjustments (some buildings have better/worse HVAC)
        if building_type == BuildingType.DATA_CENTER:
            # Data centers need constant precise cooling - less temperature variation
            multiplier = min(multiplier, 1.2)  # Cap at 20% increase
        elif building_type == BuildingType.HOSPITAL:
            # Hospitals maintain strict temperature control
            multiplier = min(multiplier, 1.3)
        elif building_type == BuildingType.RESIDENTIAL_HIGHRISE:
            # Residential buildings have more variation (people adjust thermostats)
            multiplier *= 1.15  # 15% higher due to less efficient control

        return multiplier

    def set_time_of_day(self, hour: float):
        """Set current simulation time (0-24)"""
        self.current_time_of_day = hour % 24
        print(f"Time set to: {int(hour):02d}:00")

    def set_temperature(self, temp_f: float):
        """Set current temperature in Fahrenheit (10-120°F range)"""
        self.current_temperature_f = temp_f

        # Categorize weather with extended heat tiers
        if temp_f >= 110:
            self.current_weather = "catastrophic_heat"
            warning = "⚠️ CATASTROPHIC - Mass failures expected!"
        elif temp_f >= 100:
            self.current_weather = "critical_heat"
            warning = "🔥 CRITICAL - Multiple failures likely"
        elif temp_f > 90:
            self.current_weather = "extreme_heat"
            warning = "⚡ EXTREME - High failure risk"
        elif temp_f > 80:
            self.current_weather = "hot"
            warning = "☀️ Hot - Monitor loads"
        elif temp_f < 20:
            self.current_weather = "extreme_cold"
            warning = "❄️ EXTREME COLD"
        elif temp_f < 40:
            self.current_weather = "cold"
            warning = "🌡️ Cold"
        else:
            self.current_weather = "clear"
            warning = "✓ Normal conditions"

        print(f"Temperature set to: {temp_f}°F - {warning}")

    def update_ev_charging_load(self, substation: str, load_mw: float):
        """Update EV charging load for a substation"""
        self.ev_charging_loads[substation] = load_mw

    def clear_substation_load(self, substation: str):
        """
        Clear all loads for a failed substation
        Called when substation loses power - no power = no consumption
        """
        # Clear EV charging load
        if substation in self.ev_charging_loads:
            self.ev_charging_loads[substation] = 0.0

        # Set current load to zero (will gradually drop via transition)
        if substation in self.current_loads:
            # Force immediate drop to zero for failed substations
            self.current_loads[substation] = 0.0

        # Reset HVAC ramp state (AC turns off when power is lost)
        if substation in self.hvac_ramp_state:
            self.hvac_ramp_state[substation] = 0.0

        print(f"  - Load model: {substation} load cleared (no power = 0 MW)")

    def get_load_breakdown(self, substation: str) -> Dict[str, Any]:
        """Get detailed load breakdown for a substation"""

        breakdown = {
            'substation': substation,
            'time': self.current_time_of_day,
            'temperature_f': self.current_temperature_f,
            'weather': self.current_weather,
            'building_loads': {},
            'ev_load_mw': self.ev_charging_loads.get(substation, 0),
            'total_mw': 0
        }

        # Get building loads by type
        for building in self.buildings.values():
            if building.substation == substation:
                btype = building.building_type.value
                if btype not in breakdown['building_loads']:
                    breakdown['building_loads'][btype] = 0

                # Calculate load for this building
                hour = int(self.current_time_of_day) % 24
                time_curve = self.time_curves[building.building_type]
                time_multiplier = time_curve[hour]
                temp_multiplier = self._calculate_temperature_multiplier(
                    building.building_type, building.floor_area_sqft
                )

                total_load_kw = (
                    building.base_load_kw +
                    (building.hvac_load_kw * temp_multiplier) +
                    (building.lighting_load_kw * time_multiplier) +
                    (building.equipment_load_kw * time_multiplier)
                ) * time_multiplier

                breakdown['building_loads'][btype] += total_load_kw / 1000  # MW

        # Calculate total
        breakdown['total_mw'] = sum(breakdown['building_loads'].values()) + breakdown['ev_load_mw']

        return breakdown

    def get_scenario_recommendations(self) -> List[str]:
        """Get recommendations for interesting test scenarios"""

        recommendations = []

        # Rush hour scenario
        if 8 <= self.current_time_of_day <= 9 or 17 <= self.current_time_of_day <= 18:
            recommendations.append("RUSH HOUR: Peak office + transportation load. Add 100 EVs to stress system.")

        # Hot day scenario
        if self.current_temperature_f > 85:
            recommendations.append("HOT DAY: High AC load. Substations may reach 90%+ capacity.")

        # Cold day scenario
        if self.current_temperature_f < 32:
            recommendations.append("COLD DAY: High heating load. Monitor residential areas.")

        # Evening peak
        if 18 <= self.current_time_of_day <= 20:
            recommendations.append("EVENING PEAK: Residential + entertainment peak. Good time for V2G testing.")

        # Late night
        if 0 <= self.current_time_of_day <= 5:
            recommendations.append("LATE NIGHT: Low load. Good time for maintenance and grid optimization.")

        return recommendations


def get_realistic_ev_load(num_evs: int, avg_charging_power_kw: float = 150) -> float:
    """Calculate realistic EV charging load"""
    # Assume 30% of EVs are charging at any given time
    charging_fraction = 0.3
    return (num_evs * charging_fraction * avg_charging_power_kw) / 1000  # MW
