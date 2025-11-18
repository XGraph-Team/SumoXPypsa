# Verify V2G revenue calculation accuracy

base_cost = 0.15  # $/kWh
emergency_multiplier = 150.0
v2g_multiplier = 50.0

emergency_rate = base_cost * emergency_multiplier
v2g_rate = base_cost * v2g_multiplier

print('=== REVENUE VERIFICATION ===')
print(f'Emergency rate: ${emergency_rate:.2f}/kWh')
print(f'V2G rate: ${v2g_rate:.2f}/kWh')
print()

print('Paper claims: "$75-100 revenue for 21 kWh discharge at $22.50/kWh emergency rate"')
print(f'Verification: 21 kWh × ${emergency_rate}/kWh = ${21 * emergency_rate:.2f}')
print('❌ MISMATCH! Paper says $75-100 but math gives $472.50')
print()

print('To earn $75-100 at emergency rate ($22.50/kWh):')
print(f'  $75 / ${emergency_rate} = {75/emergency_rate:.2f} kWh')
print(f'  $100 / ${emergency_rate} = {100/emergency_rate:.2f} kWh')
print('  → Should be 3.3-4.4 kWh, NOT 21 kWh')
print()

print('Alternative: If using regular V2G rate ($7.50/kWh):')
print(f'  10 kWh × ${v2g_rate} = ${10 * v2g_rate:.2f}')
print(f'  13 kWh × ${v2g_rate} = ${13 * v2g_rate:.2f}')
print('  → 10-13 kWh discharge would earn $75-98')
print()

print('=== RECOMMENDED CORRECTION ===')
print('Option 1: Fix discharge amount')
print('  "Each EV earns $75-100 revenue for 3-4 kWh discharge at $22.50/kWh"')
print()
print('Option 2: Fix revenue amount')
print('  "Each EV earns $450-500 revenue for 21 kWh discharge at $22.50/kWh"')
print()
print('Option 3: Remove specific numbers (safest)')
print('  "Each EV earns revenue based on kWh discharged at emergency rates"')
