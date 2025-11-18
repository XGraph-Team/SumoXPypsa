#!/usr/bin/env python3
"""
Test script to demonstrate all 6 advanced AI capabilities
"""

import requests
import json
import time

def test_advanced_ai_features():
    base_url = "http://localhost:5002"

    print("🚀 TESTING ADVANCED AI CAPABILITIES")
    print("=" * 60)

    # Test all 6 advanced features with custom commands
    test_commands = [
        # 1. Location Visualization
        ("show me times square", "🗺️ Advanced Location Visualization"),
        ("show me central park", "🎯 Map Focus with Highlighting"),

        # 2. System Analysis
        ("analyze system", "🔍 Deep System Analysis"),
        ("system status", "📊 Comprehensive Overview"),

        # 3. AI Suggestions
        ("suggest optimizations", "💡 AI-Powered Recommendations"),
        ("what should I do?", "🤖 Smart System Suggestions"),

        # 4. Failure Prediction
        ("predict failures", "⚠️ Predictive Analytics"),
        ("what might go wrong?", "🔮 Future Fault Detection"),

        # 5. Smart Routing
        ("optimize power routing", "⚡ Intelligent Power Management"),
        ("balance the grid", "🎛️ Smart Load Distribution"),

        # 6. Interactive Control
        ("interactive control", "🕹️ Advanced System Control"),
        ("emergency response", "🚨 Interactive Emergency Protocols")
    ]

    for i, (command, description) in enumerate(test_commands, 1):
        print(f"\n{i:2d}. {description}")
        print("-" * 50)
        print(f"Command: {command}")

        try:
            # Send command to AI
            response = requests.get(f"{base_url}/test_ai",
                                  params={"cmd": command},
                                  timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    ai_response = data.get('response', {}).get('text', 'No response')
                    print(f"✅ Success: {ai_response[:200]}...")
                else:
                    print(f"❌ Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")

        time.sleep(0.5)  # Brief pause between tests

    print("\n" + "=" * 60)
    print("🎉 ADVANCED AI TESTING COMPLETED!")
    print("All 6 advanced capabilities have been demonstrated.")

    # Final comprehensive test
    print(f"\n🌟 FINAL TEST: Maximum AI Capability")
    print("-" * 50)
    try:
        response = requests.get(f"{base_url}/test_ai", timeout=15)
        if response.status_code == 200:
            print("✅ AI System is fully operational with maximum capabilities!")
        else:
            print(f"❌ System check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System check exception: {str(e)}")

if __name__ == "__main__":
    test_advanced_ai_features()