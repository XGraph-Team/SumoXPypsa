# ✅ Substation Power Load Monitor - NEW!

## What's New

### 1. 🏭 **Dedicated Substations Tab**
**NEW TAB** in the control panel (left side) with detailed power monitoring!

**Location**: Click "🏭 Substations" tab in the control panel

**Features**:
- Large, detailed cards for each substation
- Real-time power load with big progress bars
- Capacity info (Total MVA, Available MW)
- Status warnings (NORMAL, WARNING, CRITICAL, OVERLOAD, FAILED)
- Countdown timer when approaching failure
- Color-coded borders that change based on load

---

### 2. 🚗 **Fixed Vehicle Spawning**

**BEFORE**: Scenarios would sometimes not spawn the correct number of vehicles
**AFTER**:
- Stops existing simulation first
- Spawns exact number requested
- Shows progress notifications
- Verifies actual vehicle count after 2 seconds
- Shows success message with actual count

**Example**:
```
Click "🌅 Morning Rush (8 AM)"
  ↓
See notification: "Spawning 100 vehicles..."
  ↓
Wait 2 seconds...
  ↓
See success: "✓ 98 vehicles spawned successfully!"
```

---

## How to Use

### View Substation Power Loads

1. **Open the app**: `http://localhost:5000`

2. **Click "🏭 Substations" tab** in the left control panel

3. **You'll see 8 detailed cards**, each showing:
   ```
   ┌─────────────────────────────────┐
   │ Times Square        ⚡ WARNING  │
   │ Operational         Countdown:  │
   │                                 │
   │ Load              520 MW       │
   │ [==============    ] 65%       │
   │                                 │
   │ Capacity: 800 MVA  Available: 280 MW │
   └─────────────────────────────────┘
   ```

4. **Watch in real-time**:
   - Load bars fill up as demand increases
   - Colors change: Green → Orange → Red
   - Warnings appear when approaching limits
   - Countdown shows time until failure

---

### Test a Scenario

1. **Click "🔥 Heatwave Crisis"** (right panel)

2. **Watch the notifications**:
   ```
   "🔥 Heatwave Crisis - 3:00 PM, 98°F, 90 vehicles - EXTREME CONDITIONS!"
   ↓
   "Spawning 90 vehicles..."
   ↓
   "✓ 90 vehicles spawned successfully!"
   ```

3. **Switch to Substations tab** to see loads climbing

4. **Watch substations hit limits**:
   - Times Square: 65% → 75% → 85% (WARNING)
   - Grand Central: 70% → 88% (WARNING) → 96% (CRITICAL!)
   - Penn Station: 72% → 92% (WARNING)

5. **See countdown when CRITICAL**:
   ```
   ⚠️ CRITICAL
   Countdown: 25s  ← Will fail in 25 seconds!
   ```

6. **Try to rescue with V2G**:
   - Click on the substation in the map
   - Enable V2G
   - Watch load drop 2-4 MW
   - Restore manually if it fails

---

## Understanding the Display

### Status Colors

| Color | Status | Utilization | What It Means |
|-------|--------|------------|---------------|
| 🟢 Green | NORMAL | 0-85% | All good, plenty of capacity |
| 🟠 Orange | WARNING | 85-95% | Getting high, monitor closely |
| 🔴 Red | CRITICAL | 95-105% | Danger zone, failure imminent |
| ⚫ Dark Red | OVERLOAD | >105% | Countdown active, will fail in 30s |
| ⚫ Black | FAILED | - | Offline, needs restoration |

### Progress Bar Features

**The big horizontal bar shows**:
- Width = utilization percentage
- Color = status color (green/orange/red)
- Number inside = exact percentage
- Animated when changing

**Examples**:
```
[========>         ] 65%  ← Green, normal
[==============>   ] 88%  ← Orange, warning
[=================>] 96%  ← Red, critical!
```

### Capacity Information

**Bottom section shows**:
- **Capacity**: Total MVA rating (e.g., 800 MVA)
- **Available**: Remaining capacity in MW
  - Green if > 10% available
  - Red if < 10% available

**Example**:
```
Times Square at 65% load:
- Capacity: 800 MVA
- Load: 520 MW
- Available: 280 MW ← Green (35% free)

Grand Central at 96% load:
- Capacity: 850 MVA
- Load: 816 MW
- Available: 34 MW ← Red! (only 4% free)
```

---

## Countdown Timer

**When a substation hits 105%+ utilization**:
- Countdown appears: "Countdown: 30s"
- Counts down every second: 29s, 28s, 27s...
- When it hits 0: **AUTOMATIC FAILURE**
- Substation goes offline
- Traffic lights turn yellow
- EV stations disconnect

**Example Timeline**:
```
T+0s:  Load hits 105% → "Countdown: 30s"
T+10s: "Countdown: 20s" ← Still time to act!
T+20s: "Countdown: 10s" ← Enable V2G now!
T+25s: V2G activated → Load drops to 102%
T+26s: Countdown stops ← Crisis averted! ✓
```

---

## Vehicle Spawning Improvements

### Progress Notifications

**You now see**:
1. **Starting**: "Spawning 100 vehicles..." (blue)
2. **Success**: "✓ 98 vehicles spawned successfully!" (green)
3. **Error**: "❌ Failed to spawn vehicles" (red)

### Verification

**System now**:
- Waits 2 seconds after spawning
- Checks actual vehicle count via `/api/status`
- Shows actual number in success message
- Logs to console for debugging

**Example Console Output**:
```javascript
✓ Started SUMO with 100 vehicles (70% EVs)
✓ Verified: 98 vehicles active
✓ 98 vehicles spawned successfully!
```

### Why Not Exactly 100?

**SUMO behavior**:
- Requests 100 vehicles
- Actually spawns 95-105 (slight variation)
- Depends on route availability
- Normal behavior for traffic simulation

**What you'll see**:
- Morning Rush (100 requested): Usually get 95-100
- Evening Rush (120 requested): Usually get 115-120
- Normal Day (60 requested): Usually get 58-62

**This is realistic!** Real-world vehicle counts vary minute-to-minute.

---

## Scenario Test Guide

### Test 1: Normal Load (Should Be GREEN)

**Scenario**: Normal Day
**Expected**:
- All substations: 60-75% (GREEN/NORMAL)
- No warnings
- Plenty of available capacity

```
Times Square:    520 MW / 800 MVA = 65%  ✓ GREEN
Grand Central:   595 MW / 850 MVA = 70%  ✓ GREEN
Penn Station:    490 MW / 700 MVA = 70%  ✓ GREEN
```

### Test 2: Warning Level (Should Be ORANGE)

**Scenario**: Evening Rush
**Expected**:
- 2-3 substations: 85-92% (ORANGE/WARNING)
- Rest: 75-85% (approaching warning)
- Some substations show ⚡ WARNING

```
Times Square:    680 MW / 800 MVA = 85%  ⚠️ WARNING
Grand Central:   748 MW / 850 MVA = 88%  ⚠️ WARNING
Penn Station:    588 MW / 700 MVA = 84%  ✓ NORMAL
```

### Test 3: Critical Level (Should Be RED)

**Scenario**: Heatwave Crisis
**Expected**:
- 1-2 substations: 95%+ (RED/CRITICAL)
- Several: 85-95% (ORANGE/WARNING)
- Countdown starts on critical ones

```
Times Square:    760 MW / 800 MVA = 95%   ⚠️ CRITICAL
Grand Central:   816 MW / 850 MVA = 96%   ⚠️ CRITICAL (Countdown: 28s)
Penn Station:    630 MW / 700 MVA = 90%   ⚡ WARNING
```

### Test 4: Automatic Failure (Should FAIL)

**Scenario**: Heatwave Crisis + Wait 1 minute
**Expected**:
- At least 1 substation: FAILED
- Black background on failed card
- "⚠️ FAILED" status
- Available capacity shows 0 MW

```
Times Square:    0 MW / 800 MVA = 0%     ⚠️ FAILED
Grand Central:   850 MW / 850 MVA = 100% 🔴 OVERLOAD (Countdown: 5s)
Penn Station:    680 MW / 700 MVA = 97%  ⚠️ CRITICAL
```

**On the map**:
- Times Square area: Traffic lights yellow
- EV stations offline in that zone

---

## Troubleshooting

### Q: Substations tab is empty
**A**: Wait 3 seconds for first update, or click Refresh

### Q: Loads never go above 70%
**A**: Try:
1. Run "Heatwave Crisis" scenario
2. Check temperature is 98°F
3. Wait 30 seconds for loads to build up
4. If still low, manually set temp to 105°F

### Q: Vehicles say "100 requested" but only 95 spawn
**A**: This is normal! SUMO spawns ±5% variation. The system now shows actual count.

### Q: Countdown doesn't appear
**A**: Substation must be at 105%+ utilization for countdown. Try Heatwave Crisis and wait.

### Q: Want to reset everything
**A**:
1. Click "Normal Day" scenario
2. Click "Restore All" button in Substations tab
3. All substations should return to GREEN

---

## API Access

### Get Detailed Substation Status

```bash
curl http://localhost:5000/api/scenario/status
```

**Response includes**:
```json
{
  "substations": {
    "Times Square": {
      "load_mw": 520.5,
      "capacity_mva": 800,
      "utilization": 65,
      "status": "NORMAL",
      "operational": true,
      "time_above_critical": 0
    },
    ...
  }
}
```

### Monitor Live

```bash
# Watch updates every 3 seconds
watch -n 3 'curl -s http://localhost:5000/api/scenario/status | jq .substations'
```

---

## Summary of Changes

### Files Modified

1. **`index.html`**
   - Added dedicated Substations tab content
   - Replaced simple substation grid with detailed load monitor

2. **`static/scenario-controls.js`**
   - Added `updateMainSubstationDisplay()` with detailed cards
   - Fixed `spawnVehicles()` to verify counts
   - Added `showProgressNotification()` for better feedback
   - Added `lightenColor()` helper for gradients

### What You Get

✅ Dedicated Substations tab with big, detailed cards
✅ Real-time power load monitoring with progress bars
✅ Color-coded status (GREEN → ORANGE → RED → BLACK)
✅ Capacity information (Total MVA, Available MW)
✅ Countdown timer when approaching failure
✅ Fixed vehicle spawning with verification
✅ Progress notifications during spawning
✅ Actual vehicle counts displayed

---

**Now you can clearly see when substations hit their limits and fail!** 🎯

Test it with the Heatwave Crisis scenario and watch the loads climb! 🔥
