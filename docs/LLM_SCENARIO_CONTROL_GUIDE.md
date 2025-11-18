# LLM-Based Scenario Control System
## Comprehensive Guide

This document describes the **World-Class LLM-Based Scenario Control System** that allows you to control all simulation aspects through natural language commands in the chatbot.

---

## Features

### 1. Automatic Realistic Traffic Patterns ⭐ NEW
**Vehicles spawn automatically based on time of day!**

When you set any time, the system automatically spawns realistic vehicle counts:
- **Late Night (0-5 AM)**: 10-20 vehicles
- **Morning Rush (7-9 AM)**: 85-100 vehicles
- **Midday (11 AM-2 PM)**: 70-90 vehicles
- **Evening Rush (5-7 PM)**: 90-100 vehicles
- **Night (9-11 PM)**: 40-60 vehicles

**No manual vehicle spawning needed!** See `TRAFFIC_PATTERNS_GUIDE.md` for full details.

### 2. Natural Language Command Processing
Control the simulation using natural, conversational commands:

#### Time Control
Set the time of day using various natural language patterns:
- `set time of day for 13` → Sets time to 13:00 (1:00 PM)
- `set time to 8` → Sets time to 8:00 AM
- `change time to 18` → Sets time to 18:00 (6:00 PM)
- `8 am` or `6 pm` → Sets time with AM/PM
- `time is 12` → Sets time to 12:00

#### Temperature Control
Set the temperature using natural commands:
- `set temperature for 115` → Sets temperature to 115°F
- `set temp to 75` → Sets temperature to 75°F
- `change temperature to 98` → Sets temperature to 98°F
- `make it 72 degrees` → Sets temperature to 72°F
- `temp is 85` → Sets temperature to 85°F

#### Test Scenarios
Run pre-defined test scenarios using keywords:
- **Morning Rush**: `morning rush`, `morning commute`, `8 am scenario`
- **Evening Rush**: `evening rush`, `evening commute`, `6 pm scenario`
- **Normal Day**: `normal day`, `regular day`, `typical day`, `midday`
- **Heatwave Crisis**: `heatwave`, `heat crisis`, `extreme heat`
- **Catastrophic Heat**: `catastrophic heat`, `critical heat`, `115 degrees`
- **Late Night**: `late night`, `night time`, `3 am`, `overnight`

#### Status Requests
Get current scenario status:
- `status` → Shows current time, temperature, and active scenarios
- `what is the current status` → Same as above
- `current settings` → Same as above

#### Suggestions
Get intelligent scenario recommendations:
- `suggest` → Get scenario suggestions based on current conditions
- `recommend` → Same as above
- `what should I run` → Same as above

---

## Intelligent Suggestions

The system provides **context-aware scenario suggestions** based on:

### Time-Based Suggestions
- **7:00-9:00 AM**: Morning Rush scenarios
- **5:00-7:00 PM**: Evening Rush scenarios
- **0:00-4:00 AM**: Late Night scenarios
- **Other times**: Normal Day scenarios

### Temperature-Based Suggestions
- **110°F+**: Catastrophic Heat scenarios
- **95°F+**: Heatwave Crisis scenarios
- **Normal temps**: Standard traffic scenarios

Suggestions are automatically shown when you set time or temperature!

---

## Conflict Detection

The system prevents overlapping scenarios:

### Protected Scenarios
- **Blackout Scenarios**: Citywide power failure (manually triggered)
- **V2G Emergency Scenarios**: Vehicle-to-Grid rescue operations

### How It Works
If you try to change time/temperature during an active blackout or V2G scenario, you'll get:
```
⚠️ Cannot change time: Active scenario in progress (v2g_rescue).
Please wait for scenario completion or cancel it first.
```

This ensures scenario integrity and prevents conflicts!

---

## Map Overlay

A **live status overlay** displays on the map showing:
- **Current Time**: 24-hour format (e.g., 13:00)
- **Temperature**: In Fahrenheit (e.g., 75°F)
- **Time Description**: "Morning Rush", "Evening", etc.

### Location
Top-left corner of the map, below the performance stats.

### Updates
Updates automatically when you change time or temperature via chat!

---

## Test Scenario Details

Each scenario sets specific conditions:

| Scenario | Time | Temp | Vehicles | Difficulty |
|----------|------|------|----------|------------|
| **Morning Rush** 🌅 | 8:00 AM | 75°F | 100 | Medium |
| **Evening Rush** 🌆 | 6:00 PM | 80°F | 120 | Hard |
| **Normal Day** ☀️ | 12:00 PM | 72°F | 60 | Easy |
| **Heatwave Crisis** 🔥 | 3:00 PM | 98°F | 90 | Extreme |
| **Catastrophic Heat** ☢️ | 2:00 PM | 115°F | 100 | Catastrophic |
| **Late Night** 🌙 | 3:00 AM | 65°F | 15 | Easy |

---

## Example Commands

### Simple Commands
```
User: set time for 13
AI: ✅ Time set to 13:00 (Midday)
    💡 Suggested test scenarios:
    • Normal Day
    • Heatwave Crisis

User: set temperature for 115
AI: ✅ Temperature set to 115°F (CATASTROPHIC HEAT)
    💡 Suggested test scenarios:
    • Catastrophic Heat
    • Heatwave Crisis

User: morning rush
AI: 🌅 Morning Rush Hour (8:00 AM, 75°F) scenario started!
    ⏰ Time: 8:00
    🌡️ Temperature: 75°F
    🚗 Vehicles: 100
    📊 Difficulty: MEDIUM
```

### Complex Workflow
```
User: status
AI: 📊 Current Scenario Status
    ⏰ Time: 12:00 (Midday)
    🌡️ Temperature: 72°F (Clear)
    🏭 Substations: 8/8 operational
    ✅ No active scenarios - Ready for commands

User: suggest
AI: 💡 Scenario Suggestions
    Based on current conditions (Midday, 72°F):
    1. ☀️ Normal Day (12:00 PM, 72°F)
       Reason: Regular daytime operations
    2. 🌅 Morning Rush (8:00 AM, 75°F)
       Reason: High demand scenario
    Say any scenario name to start it!

User: set temp to 115
AI: ✅ Temperature set to 115°F (CATASTROPHIC HEAT)
    💡 Suggested test scenarios:
    • Catastrophic Heat
    • Heatwave Crisis

User: catastrophic heat
AI: ☢️ Catastrophic Heat (2:00 PM, 115°F) scenario started!
    ⏰ Time: 14:00
    🌡️ Temperature: 115°F
    🚗 Vehicles: 100
    📊 Difficulty: CATASTROPHIC
```

---

## Technical Architecture

### Components

#### 1. **chatbot-scenario-llm.js**
- Natural language processing engine
- Pattern matching for commands
- Conflict detection
- Suggestion generation
- Map overlay management

#### 2. **Modified script.js**
- Integration with existing chatbot
- Dual-path processing (scenario vs AI chat)
- Response formatting
- Suggestion chip rendering

#### 3. **Backend APIs Used**
- `/api/scenario/set_time` - Set simulation time
- `/api/scenario/set_temperature` - Set temperature
- `/api/scenario/add_vehicles` - Update vehicle loads
- `/api/scenario/status` - Get current status
- `/api/sumo/start` - Start traffic simulation
- `/api/sumo/stop` - Stop traffic simulation

### Processing Flow
```
User Input
    ↓
LLM Scenario Handler (processCommand)
    ↓
Command Detection (time/temp/scenario/status)
    ↓
Conflict Check (blackout/V2G)
    ↓
API Call (backend updates)
    ↓
Map Overlay Update
    ↓
Intelligent Suggestions
    ↓
Response to User
```

---

## Error Handling

### Validation
- **Time**: Clamped to 0-23 hours
- **Temperature**: Clamped to 10-120°F
- **Conflicts**: Detected and prevented
- **API Errors**: Caught and displayed

### Error Messages
```
❌ Failed to set time: [error details]
❌ Error setting temperature: [error details]
⚠️ Cannot change time: Active scenario in progress
```

---

## UI Integration

### Scenario Control Panel
The existing scenario control panel (`scenario-controls.js`) remains available but is now **optional**. You can:
1. **Use chatbot only**: Control everything via natural language
2. **Use UI sliders**: Traditional manual control
3. **Use both**: Mix and match as preferred

### Recommended Approach
Use the **chatbot for everything** - it's faster, more intuitive, and provides intelligent suggestions!

---

## Best Practices

### 1. **Start with Status**
Always check current status before making changes:
```
User: status
```

### 2. **Use Suggestions**
Let the AI suggest appropriate scenarios:
```
User: suggest
```

### 3. **Clear Commands**
Be explicit but natural:
```
Good: "set time for 13"
Good: "morning rush"
Good: "set temperature to 98"

Also works: "13:00"
Also works: "make it morning"
Also works: "temp 98"
```

### 4. **Wait for Scenarios**
Don't change settings during blackout or V2G scenarios - let them complete naturally.

### 5. **Experiment**
Try different phrasings - the system is designed to understand variations!

---

## Troubleshooting

### Issue: Substations not visible initially
**Solution**: Fixed! Substations now show correctly on first load.

### Issue: Commands not recognized
**Solution**: Check spelling, try rephrasing. Examples:
- "time 13" instead of "13 time"
- "morning rush" instead of "rush morning"

### Issue: Conflict warning appearing
**Solution**: Wait for active scenario to complete, or manually restore substations if it's a blackout scenario.

### Issue: Suggestions not appearing
**Solution**: Suggestions only appear when you set time or temperature, or explicitly ask for them with "suggest".

---

## Future Enhancements

Possible future additions:
- Voice command support
- Scenario scheduling
- Custom scenario creation via chat
- Multi-scenario orchestration
- Predictive scenario suggestions
- Historical scenario replay

---

## Support

For issues or questions:
1. Type `status` to check system state
2. Type `suggest` to get recommendations
3. Check console for detailed error messages
4. Refer to this guide for command syntax

---

## Summary

**The LLM-Based Scenario Control System provides:**
- ✅ Natural language command processing
- ✅ Intelligent context-aware suggestions
- ✅ Conflict detection and prevention
- ✅ Live map status overlay
- ✅ Complete error handling
- ✅ Seamless integration with existing systems
- ✅ World-class user experience

**Everything is controlled through the chatbot - no manual UI needed!**

Enjoy your world-class scenario control system! 🎯
