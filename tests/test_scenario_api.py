"""
Quick test script to verify scenario API is working
"""

import requests
import json

print("Testing Scenario API...")
print("=" * 60)

try:
    response = requests.get('http://localhost:5000/api/scenario/status')
    data = response.json()

    print(f"Status Code: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"\nSubstations found: {len(data.get('substations', {}))}")
    print("\nSubstation Data:")
    print(json.dumps(data.get('substations', {}), indent=2))

except Exception as e:
    print(f"ERROR: {e}")
    print("\nMake sure the server is running:")
    print("  python main_complete_integration.py")
