"""
Realistic EV Battery Model for Manhattan Simulation
"""

class EVBatteryModel:
    """Professional EV battery simulation with realistic physics"""
    
    # Consumption factors (kWh/km)
# SIMULATION SPEED: 5x faster consumption for visible testing
# TESTING MODE: 10x faster consumption to force charging quickly
    CONSUMPTION_RATES = {
        'ev_sedan': {
            'city': 2.0,      # Extreme consumption for testing
            'highway': 2.5,   
            'congested': 3.0
        },
        'ev_suv': {
            'city': 3.0,
            'highway': 3.5,
            'congested': 4.0
        },
        'ev_bus': {
            'city': 10.0,
            'highway': 8.0,
            'congested': 12.0
        }
    }
    
    # Auxiliary consumption (kW) - AC, heating, etc.
    AUXILIARY_POWER = {
        'ev_sedan': 1.5,
        'ev_suv': 2.0,
        'ev_bus': 5.0
    }
    
    @staticmethod
    def calculate_consumption(vehicle_type, speed_mps, acceleration_mps2, 
                            is_congested=False, ambient_temp=20):
        """
        Calculate realistic energy consumption
        
        Args:
            vehicle_type: Type of EV
            speed_mps: Current speed in m/s
            acceleration_mps2: Current acceleration in m/s²
            is_congested: Whether in traffic
            ambient_temp: Ambient temperature (affects HVAC)
        
        Returns:
            Energy consumption in kWh for this timestep
        """
        
        # Base consumption based on driving conditions
        speed_kmh = speed_mps * 3.6
        
        if speed_kmh < 30:
            driving_mode = 'congested' if is_congested else 'city'
        elif speed_kmh < 60:
            driving_mode = 'city'
        else:
            driving_mode = 'highway'
        
        # Get base consumption rate
        base_rate = EVBatteryModel.CONSUMPTION_RATES.get(
            vehicle_type, 
            EVBatteryModel.CONSUMPTION_RATES['ev_sedan']
        )[driving_mode]
        
        # Adjust for acceleration (regenerative braking or acceleration penalty)
        if acceleration_mps2 < -1:
            # Regenerative braking
            regen_factor = 0.7  # Recover 30% energy
        elif acceleration_mps2 > 1:
            # Hard acceleration
            regen_factor = 1.3  # 30% more consumption
        else:
            regen_factor = 1.0
        
        # Temperature adjustment (HVAC usage)
        temp_factor = 1.0
        if ambient_temp < 0:
            temp_factor = 1.4  # Heating in winter
        elif ambient_temp > 30:
            temp_factor = 1.2  # AC in summer
        
        # Calculate consumption for this timestep (0.1 seconds)
        distance_km = (speed_mps * 0.1) / 1000
        energy_consumed = base_rate * distance_km * regen_factor * temp_factor
        
        # Add auxiliary power (converted to kWh for 0.1 second)
        aux_power = EVBatteryModel.AUXILIARY_POWER.get(vehicle_type, 1.5)
        energy_consumed += (aux_power * 0.1) / 3600
        
        return energy_consumed