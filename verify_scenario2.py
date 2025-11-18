# Verify all numbers in Scenario 2 (V2G Emergency Mitigation)

print('=== SCENARIO 2 VERIFICATION ===\n')

# From v2g_manager.py
MIN_SOC_FOR_V2G = 0.60  # 60%
DISCHARGE_RATE_KW = 50  # kW per vehicle

print('1. SOC Threshold')
print(f'   Code: MIN_SOC_FOR_V2G = {MIN_SOC_FOR_V2G*100:.0f}%')
print(f'   Paper: "12 EVs with SOC > 70%"')
print(f'   Issue: Paper says 70%, code says 60%')
print(f'   ⚠️  Should say "SOC > 60%"')
print()

print('2. Total Potential Power (8 vehicles)')
total_power = 8 * DISCHARGE_RATE_KW
print(f'   Calculation: 8 EVs × {DISCHARGE_RATE_KW} kW = {total_power} kW')
print(f'   Paper: "total potential 480 kW"')
if total_power != 480:
    print(f'   ❌ ERROR! Should be {total_power} kW, not 480 kW')
else:
    print(f'   ✓ Correct')
print()

print('3. Initial Discharge (3 vehicles)')
initial_discharge = 3 * DISCHARGE_RATE_KW
print(f'   Calculation: 3 EVs × {DISCHARGE_RATE_KW} kW = {initial_discharge} kW')
print(f'   Paper: "First 3 EVs... 150 kW discharge"')
if initial_discharge == 150:
    print(f'   ✓ Correct')
else:
    print(f'   ❌ ERROR!')
print()

print('4. Full Deployment (8 vehicles)')
full_discharge = 8 * DISCHARGE_RATE_KW
print(f'   Calculation: 8 EVs × {DISCHARGE_RATE_KW} kW = {full_discharge} kW')
print(f'   Paper: "8 EVs provide 400 kW total"')
if full_discharge == 400:
    print(f'   ✓ Correct')
else:
    print(f'   ❌ ERROR!')
print()

print('5. Revenue Calculation')
emergency_rate = 0.15 * 150  # $22.50/kWh
discharge_kwh = 21
revenue = discharge_kwh * emergency_rate
print(f'   Paper: "$75-100 revenue for 21 kWh discharge at $22.50/kWh"')
print(f'   Calculation: {discharge_kwh} kWh × ${emergency_rate}/kWh = ${revenue:.2f}')
print(f'   ❌ MAJOR ERROR! Should be ${revenue:.2f}, not $75-100')
print()

print('=== CORRECTIONS NEEDED ===')
print('1. Change "SOC > 70%" to "SOC > 60%"')
print('2. Change "total potential 480 kW" to "total potential 400 kW"')
print('3. Fix revenue claim (see options in previous analysis)')
