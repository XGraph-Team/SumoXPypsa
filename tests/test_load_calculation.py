"""
Test realistic load calculation to see what's happening
"""

import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from core.power_system import ManhattanPowerGrid
from integrated_backend import ManhattanIntegratedSystem
from realistic_load_model import RealisticLoadModel

print("=" * 70)
print("TESTING REALISTIC LOAD CALCULATION")
print("=" * 70)

# Create dependencies
power_grid = ManhattanPowerGrid()
integrated_system = ManhattanIntegratedSystem(power_grid)
load_model = RealisticLoadModel(integrated_system)

print(f"\nBuildings generated: {len(load_model.buildings)}")

# Test 1: Normal conditions (12 PM, 72°F)
print("\n" + "=" * 70)
print("TEST 1: Normal Day (12 PM, 72°F)")
print("=" * 70)

load_model.set_time_of_day(12)
load_model.set_temperature(72)
loads = load_model.calculate_total_load()

print(f"\nSubstation loads:")
for name, load_mw in sorted(loads.items()):
    capacity = {
        "Hell's Kitchen": 750,
        "Times Square": 800,
        "Penn Station": 700,
        "Grand Central": 850,
        "Murray Hill": 650,
        "Turtle Bay": 600,
        "Chelsea": 700,
        "Midtown East": 750
    }[name]
    utilization = (load_mw / capacity) * 100
    print(f"  {name:20s}: {load_mw:6.1f} MW / {capacity} MVA = {utilization:5.1f}%")

total_load = sum(loads.values())
total_capacity = 6000  # Sum of all capacities
print(f"\nTotal load: {total_load:.1f} MW")
print(f"Average utilization: {(total_load / total_capacity) * 100:.1f}%")

# Test 2: Heatwave Crisis (3 PM, 98°F)
print("\n" + "=" * 70)
print("TEST 2: Heatwave Crisis (3 PM, 98°F)")
print("=" * 70)

load_model.set_time_of_day(15)  # 3 PM
load_model.set_temperature(98)
loads = load_model.calculate_total_load()

print(f"\nSubstation loads:")
for name, load_mw in sorted(loads.items()):
    capacity = {
        "Hell's Kitchen": 750,
        "Times Square": 800,
        "Penn Station": 700,
        "Grand Central": 850,
        "Murray Hill": 650,
        "Turtle Bay": 600,
        "Chelsea": 700,
        "Midtown East": 750
    }[name]
    utilization = (load_mw / capacity) * 100
    status = "NORMAL"
    if utilization >= 105:
        status = "OVERLOAD"
    elif utilization >= 95:
        status = "CRITICAL"
    elif utilization >= 85:
        status = "WARNING"

    print(f"  {name:20s}: {load_mw:6.1f} MW / {capacity} MVA = {utilization:5.1f}% [{status}]")

total_load = sum(loads.values())
print(f"\nTotal load: {total_load:.1f} MW")
print(f"Average utilization: {(total_load / total_capacity) * 100:.1f}%")

# Test 3: Evening Rush Hour (6 PM, 80°F)
print("\n" + "=" * 70)
print("TEST 3: Evening Rush (6 PM, 80°F)")
print("=" * 70)

load_model.set_time_of_day(18)  # 6 PM
load_model.set_temperature(80)
loads = load_model.calculate_total_load()

print(f"\nSubstation loads:")
for name, load_mw in sorted(loads.items()):
    capacity = {
        "Hell's Kitchen": 750,
        "Times Square": 800,
        "Penn Station": 700,
        "Grand Central": 850,
        "Murray Hill": 650,
        "Turtle Bay": 600,
        "Chelsea": 700,
        "Midtown East": 750
    }[name]
    utilization = (load_mw / capacity) * 100
    status = "NORMAL"
    if utilization >= 105:
        status = "OVERLOAD"
    elif utilization >= 95:
        status = "CRITICAL"
    elif utilization >= 85:
        status = "WARNING"

    print(f"  {name:20s}: {load_mw:6.1f} MW / {capacity} MVA = {utilization:5.1f}% [{status}]")

total_load = sum(loads.values())
print(f"\nTotal load: {total_load:.1f} MW")
print(f"Average utilization: {(total_load / total_capacity) * 100:.1f}%")

# Test 4: With EV load added
print("\n" + "=" * 70)
print("TEST 4: Heatwave + 90 EVs charging (simulated)")
print("=" * 70)

load_model.set_time_of_day(15)
load_model.set_temperature(98)

# Simulate 90 EVs at 50 kW each = 4.5 MW
# Distributed across 8 substations = ~0.56 MW per substation
ev_load_per_substation = 4.5 / 8

loads = load_model.calculate_total_load()

print(f"\nSubstation loads (with EV charging):")
for name, load_mw in sorted(loads.items()):
    total_with_ev = load_mw + ev_load_per_substation
    capacity = {
        "Hell's Kitchen": 750,
        "Times Square": 800,
        "Penn Station": 700,
        "Grand Central": 850,
        "Murray Hill": 650,
        "Turtle Bay": 600,
        "Chelsea": 700,
        "Midtown East": 750
    }[name]
    utilization = (total_with_ev / capacity) * 100
    status = "NORMAL"
    if utilization >= 105:
        status = "OVERLOAD"
    elif utilization >= 95:
        status = "CRITICAL"
    elif utilization >= 85:
        status = "WARNING"

    print(f"  {name:20s}: {total_with_ev:6.1f} MW / {capacity} MVA = {utilization:5.1f}% [{status}]")

print("\n" + "=" * 70)
print("ANALYSIS:")
print("=" * 70)
print(f"If loads are too low (< 50% even in heatwave), we need to:")
print(f"  1. Increase building count per substation")
print(f"  2. Increase base W/sqft for building types")
print(f"  3. Increase temperature impact multiplier")
print(f"  4. Add more realistic occupancy factors")
