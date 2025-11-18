# Realistic Traffic Pattern System
## Automatic Vehicle Spawning Based on Time of Day

---

## Overview

The system now **automatically spawns realistic vehicle counts** based on the time of day you set. Whether you use the chatbot or scenario control sliders, the simulation will intelligently adjust traffic to match Manhattan's real-world patterns.

**Maximum Capacity**: 100 vehicles (simulation limit)

---

## Traffic Patterns Throughout the Day

| Time Range | Icon | Vehicles | EV % | Description |
|------------|------|----------|------|-------------|
| **00:00 - 05:00** | 🌙 | 10-20 | 50% | Late Night - Minimal Traffic |
| **05:00 - 07:00** | 🌅 | 40-60 | 60% | Early Morning - Light Traffic |
| **07:00 - 09:00** | 🚗 | 85-100 | 70% | Morning Rush Hour - Heavy Traffic |
| **09:00 - 11:00** | ☀️ | 60-80 | 70% | Mid Morning - Moderate Traffic |
| **11:00 - 14:00** | 🌞 | 70-90 | 70% | Midday - Normal Traffic |
| **14:00 - 17:00** | 🌤️ | 75-95 | 70% | Afternoon - Building Traffic |
| **17:00 - 19:00** | 🌆 | 90-100 | 75% | Evening Rush Hour - Heavy Traffic |
| **19:00 - 21:00** | 🌃 | 70-85 | 70% | Evening - Moderate Traffic |
| **21:00 - 23:00** | 🌉 | 40-60 | 60% | Night - Light Traffic |
| **23:00 - 24:00** | 🌙 | 20-30 | 50% | Late Evening - Minimal Traffic |

---

## How It Works

### Automatic Spawning

When you set the time (via chatbot or slider), the system:

1. **Detects the time range** (e.g., 8:00 AM = Morning Rush)
2. **Calculates appropriate vehicle count** (e.g., 85-100 vehicles)
3. **Determines EV percentage** (e.g., 70% EVs)
4. **Stops existing simulation** (clears old vehicles)
5. **Spawns new vehicles** (with realistic distribution)
6. **Updates EV charging loads** (based on vehicle count)

### Safety Caps

- **Maximum vehicles**: 100 (hard limit)
- **Minimum vehicles**: 10 (even at night, some traffic exists)
- **Variance**: ±20% randomization for realism

### Actual Spawned vs Requested

**Important**: SUMO may not be able to spawn all requested vehicles if it can't find suitable road edges.

- **Requested Count**: Calculated by traffic pattern system
- **Actual Spawned**: What SUMO successfully placed on roads
- **Difference**: Shown in chatbot when they differ

The chatbot **always shows the actual spawned count**, ensuring accuracy!

---

## Examples

### Example 1: Setting Morning Rush (All Spawn Successfully)

```
User: set time for 8
AI: ✅ Time set to 08:00 (Morning Rush)
    🚗 Traffic: 92 vehicles
    🚗 Morning Rush Hour - Heavy Traffic

Result: 92 vehicles successfully spawned (70% EVs)
```

### Example 1b: Setting Afternoon (Some Can't Spawn)

```
User: set time for 15
AI: ✅ Time set to 15:00 (Afternoon)
    🚗 Traffic: 52 vehicles spawned (86 requested)
    🌤️ Afternoon - Building Traffic
    ⚠️ Note: 34 vehicles couldn't find suitable road edges

Result: 52 vehicles spawned (SUMO couldn't place 34 on roads)
Console: ✅ Requested: 86, Actually spawned: 52
```

### Example 2: Setting Late Night

```
User: set time for 3
AI: ✅ Time set to 03:00 (Late Night)
    🚗 Traffic: 15 vehicles
    🌙 Late Night - Minimal Traffic

Result: 15 vehicles spawned (50% EVs)
```

### Example 3: Using Slider

```
Action: Move time slider to 18:00
Result: 95 vehicles automatically spawned
Console: 🚗 Spawned 95 vehicles for Evening Rush Hour - Heavy Traffic
```

---

## EV Percentage by Time

The system varies EV percentage based on time:

- **Night (50%)**: Lower EV usage, mostly ICE vehicles
- **Early Morning (60%)**: EVs starting commutes
- **Rush Hours (70-75%)**: Peak EV usage, many commuters
- **Daytime (70%)**: Consistent EV presence
- **Evening Rush (75%)**: Highest EV percentage

This creates realistic charging demand patterns throughout the day!

---

## Integration Points

### 1. Chatbot Commands
All time-setting commands trigger automatic vehicle spawning:
```
"set time for 13"
"time is 8"
"8 am"
"change time to 18"
```

### 2. Scenario Control Slider
Moving the time slider automatically spawns vehicles for that time.

### 3. Test Scenarios
Pre-defined scenarios override automatic patterns with specific counts:
- Morning Rush: 100 vehicles
- Evening Rush: 120 vehicles (capped to 100)
- Normal Day: 60 vehicles
- Heatwave: 90 vehicles
- Late Night: 15 vehicles

---

## Technical Details

### Files Involved

**`traffic-patterns.js`**
- Pattern definitions
- Vehicle count calculation
- Spawning logic
- EV percentage management

**`chatbot-scenario-llm.js`**
- Integrates patterns with chatbot commands
- Displays traffic info in responses

**`scenario-controls.js`**
- Integrates patterns with UI sliders
- Auto-spawns on slider change

### API Endpoints Used

- `/api/sumo/stop` - Stops current simulation
- `/api/sumo/start` - Starts with new vehicle count
- `/api/scenario/set_time` - Sets simulation time
- `/api/scenario/add_vehicles` - Updates EV charging loads

### Pattern Selection Algorithm

```javascript
1. Parse hour (0-23)
2. Find matching time range in patterns
3. Get min/max vehicle range for that pattern
4. Calculate base count: (min + max) / 2
5. Add randomization: ±20% variance
6. Apply safety cap: max 100 vehicles
7. Return final count
```

---

## Benefits

### Realism
- Matches Manhattan's actual traffic patterns
- Rush hours have heavy traffic
- Night hours have minimal traffic
- Realistic EV adoption rates

### Convenience
- **Zero manual work** - Just set the time!
- Works with chatbot and UI
- Consistent across all methods
- Automatic synchronization

### Accuracy
- Proper EV charging loads
- Realistic grid stress
- Better testing scenarios
- Predictable patterns

---

## Testing Different Scenarios

### Light Load Testing
```
Set time: 3 AM (Late Night)
Vehicles: 10-20
Use case: Test minimal load conditions
```

### Normal Load Testing
```
Set time: 12 PM (Midday)
Vehicles: 70-90
Use case: Test standard operations
```

### Heavy Load Testing
```
Set time: 8 AM or 6 PM (Rush Hours)
Vehicles: 85-100
Use case: Test peak demand, potential failures
```

### Progressive Testing
```
Cycle through: 3 AM → 8 AM → 12 PM → 6 PM → 11 PM
Watch traffic build and decrease naturally
Test grid response to changing loads
```

---

## Customization

Want to modify patterns? Edit `traffic-patterns.js`:

```javascript
'morning_rush': {
    timeRange: [7, 9],        // Time range (hours)
    vehicleRange: [85, 100],  // Min-max vehicles
    evPercentage: 0.7,        // 70% EVs
    description: 'Morning Rush Hour - Heavy Traffic',
    icon: '🚗'
},
```

**Remember**: Keep max at or below 100 vehicles!

---

## Troubleshooting

### Issue: Too many/few vehicles
**Solution**: Adjust `vehicleRange` in `traffic-patterns.js`

### Issue: Vehicles not spawning
**Solution**: Check console for errors, ensure `/api/sumo/start` is working

### Issue: EV percentage seems wrong
**Solution**: Adjust `evPercentage` (0.0 to 1.0) in patterns

### Issue: Spawn lag
**Solution**: Normal - simulation stops old vehicles, then spawns new ones (~500ms delay)

---

## Advanced Features

### Pattern Querying
```javascript
// Get pattern for specific time
const pattern = trafficPatternManager.getPatternForTime(8);
console.log(pattern.description); // "Morning Rush Hour - Heavy Traffic"

// Get vehicle count
const count = trafficPatternManager.getVehicleCountForTime(8);
console.log(count); // 92 (randomized within 85-100)

// Get daily summary
const summary = trafficPatternManager.getDailySummary();
console.log(summary); // Full 24-hour pattern breakdown
```

### Manual Override
To spawn specific count (not recommended):
```javascript
// Disable auto-spawn, then manually spawn
await trafficPatternManager.spawnVehiclesForTime(8); // Uses pattern
// OR
fetch('/api/sumo/start', {
    method: 'POST',
    body: JSON.stringify({vehicle_count: 50, ev_percentage: 0.7})
});
```

---

## Summary

The **Realistic Traffic Pattern System** provides:

✅ **Automatic vehicle spawning** based on time
✅ **10 distinct traffic patterns** covering 24 hours
✅ **Realistic EV percentages** (50-75%)
✅ **Safety cap** at 100 vehicles maximum
✅ **±20% randomization** for natural variance
✅ **Works everywhere** - chatbot, sliders, scenarios
✅ **Zero configuration** needed
✅ **World-class realism** matching Manhattan patterns

**Just set the time - vehicles spawn automatically!** 🚀
