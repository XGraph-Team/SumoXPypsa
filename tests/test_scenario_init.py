"""
Test script to diagnose scenario controller initialization issues
"""

import sys
import traceback

# Fix Windows console encoding issues
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

print("=" * 70)
print("TESTING SCENARIO CONTROLLER INITIALIZATION")
print("=" * 70)

# Step 1: Test imports
print("\n[1] Testing imports...")
try:
    from realistic_load_model import RealisticLoadModel
    print("    [OK] RealisticLoadModel imported successfully")
except Exception as e:
    print(f"    [FAIL] FAILED to import RealisticLoadModel: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from scenario_controller import ScenarioController
    print("    [OK] ScenarioController imported successfully")
except Exception as e:
    print(f"    [FAIL] FAILED to import ScenarioController: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from scenario_integration import integrate_scenario_controller
    print("    [OK] integrate_scenario_controller imported successfully")
except Exception as e:
    print(f"    [FAIL] FAILED to import integrate_scenario_controller: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test integrated system
print("\n[2] Testing integrated system dependency...")
try:
    from core.power_system import ManhattanPowerGrid
    from integrated_backend import ManhattanIntegratedSystem

    power_grid = ManhattanPowerGrid()
    print("    [OK] ManhattanPowerGrid created")

    integrated_system = ManhattanIntegratedSystem(power_grid)
    print("    [OK] ManhattanIntegratedSystem created")
except Exception as e:
    print(f"    [FAIL] FAILED to create dependencies: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test RealisticLoadModel initialization
print("\n[3] Testing RealisticLoadModel initialization...")
try:
    load_model = RealisticLoadModel(integrated_system)
    print("    [OK] RealisticLoadModel initialized successfully")
    print(f"    - Buildings generated: {len(load_model.buildings)}")
except Exception as e:
    print(f"    [FAIL] FAILED to initialize RealisticLoadModel: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test ScenarioController initialization
print("\n[4] Testing ScenarioController initialization...")
try:
    scenario_controller = ScenarioController(
        integrated_system=integrated_system,
        load_model=load_model,
        power_grid=power_grid,
        sumo_manager=None  # Optional
    )
    print("    [OK] ScenarioController initialized successfully")
    print(f"    - Monitors: {len(scenario_controller.substation_monitors)}")
except Exception as e:
    print(f"    [FAIL] FAILED to initialize ScenarioController: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test get_system_status
print("\n[5] Testing get_system_status()...")
try:
    status = scenario_controller.get_system_status()
    print("    [OK] get_system_status() works")
    print(f"    - Substations: {len(status.get('substations', {}))}")

    # Print substation data
    print("\n[6] Substation status:")
    for name, data in status.get('substations', {}).items():
        print(f"    - {name}: {data['load_mw']} MW / {data['capacity_mva']} MVA ({data['utilization']}%)")
except Exception as e:
    print(f"    [FAIL] FAILED to get system status: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 7: Test Flask integration (without running server)
print("\n[7] Testing Flask integration...")
try:
    from flask import Flask
    app = Flask(__name__)

    integrate_scenario_controller(app, scenario_controller, load_model)
    print("    [OK] Flask endpoints integrated")

    # List registered routes
    print("\n    Registered scenario routes:")
    for rule in app.url_map.iter_rules():
        if 'scenario' in rule.rule:
            print(f"      {rule.rule}")
except Exception as e:
    print(f"    [FAIL] FAILED Flask integration: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("[SUCCESS] ALL TESTS PASSED - Scenario controller should work!")
print("=" * 70)
print("\nIf the server still doesn't work, check main_complete_integration.py")
print("for errors during startup.")
