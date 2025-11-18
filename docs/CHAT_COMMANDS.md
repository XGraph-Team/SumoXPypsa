# 💬 Chatbot Scenario Commands - Quick Reference

## 🎬 SCENARIO COMMANDS (SIMULATION MODE)

### **V2G Emergency Rescue Scenario**

These commands trigger the **SIMULATION** scenario (not real V2G activation):

```
run v2g scenario
trigger v2g scenario
v2g rescue scenario
show v2g scenario
demonstrate v2g
execute v2g scenario
start v2g scenario
```

**What happens:**
1. AI analyzes system and shows preparation details
2. You type `confirm` to start
3. Camera zooms to Times Square
4. Dramatic substation failure simulation
5. EVs rush to provide emergency power
6. Live progress tracking
7. Automatic restoration and celebration

**Duration:** ~60 seconds

---

### **Citywide Blackout Scenario**

These commands trigger the **SIMULATION** blackout:

```
trigger blackout scenario
blackout scenario
run blackout scenario
citywide blackout scenario
execute blackout scenario
simulate blackout
start blackout scenario
```

**What happens:**
1. AI shows preparation with warnings
2. You type `confirm` to start
3. Camera shows Manhattan overview
4. Substations fail dramatically one by one
5. Traffic lights go dark
6. Emergency status displayed
7. Awaits your restoration command

**Duration:** Until manual restoration

---

## 📋 INFORMATION COMMANDS

### **List Available Scenarios**
```
show scenarios
what scenarios
list scenarios
available scenarios
scenario options
```

Shows all available scenarios with descriptions and commands.

---

### **Get Help**
```
help
what can you do
show capabilities
```

Shows all chatbot capabilities including scenarios.

---

## ✅ CONFIRMATION COMMANDS

When AI asks for confirmation, use:

```
confirm
yes
proceed
go ahead
do it
```

---

## ❌ CANCELLATION COMMANDS

To cancel a scenario before it starts:

```
cancel
no
abort
stop
nevermind
```

---

## 🎯 COMPLETE WORKFLOW EXAMPLE

### **Example 1: Quick V2G Test**

```
User: run v2g scenario

AI: [Shows detailed preparation overview]
    📊 Current System State:
    • Total vehicles: 35
    • High-SOC EVs (70%+): 12

    💡 Preparation Needed:
    I'll spawn 50 EVs with 70-95% battery...

    Type "confirm" to prepare and start

User: confirm

AI: 🚗 Preparing scenario environment...
    ⚡ Spawning 50 high-SOC electric vehicles...
    ✅ Vehicle preparation complete!
    🎬 V2G EMERGENCY RESCUE SCENARIO STARTING
    🎥 Positioning camera at Times Square...
    🚨 EMERGENCY ALERT
    ⚠️ Times Square Substation - CRITICAL FAILURE
    [... scenario executes with live updates ...]
    🎉 V2G RESCUE COMPLETE!
    📊 Scenario Results: [stats shown]
```

---

### **Example 2: Exploring Options**

```
User: what scenarios can I run?

AI: [Shows scenario list with descriptions]

User: trigger blackout scenario

AI: [Shows blackout preparation details with warning]

User: confirm

AI: [Executes dramatic blackout scenario]
```

---

### **Example 3: Cancelling**

```
User: run v2g scenario

AI: [Shows preparation details]

User: cancel

AI: ✅ Scenario cancelled. Let me know if you'd like to try something else!
```

---

## 🎨 VISUAL EFFECTS YOU'LL SEE

### **V2G Scenario:**
- ✅ Smooth camera zoom to Times Square
- ✅ Red flash on substation failure
- ✅ Pulsing red circle on failed substation
- ✅ Camera tilts and rotates dramatically (45°-60°)
- ✅ EVs moving on map towards location
- ✅ Green flash on successful restoration
- ✅ Camera zooms back out smoothly

### **Blackout Scenario:**
- ✅ Camera zooms out to show all Manhattan
- ✅ Orange flash for cascade failure warning
- ✅ Red flashes with each substation failure
- ✅ Traffic lights turn black across the map
- ✅ Camera tilts and rotates showing impact
- ✅ Dramatic visualization of darkened grid

---

## 💡 PRO TIPS

### **Tip 1: Pre-spawn Vehicles**
For faster scenarios, manually start SUMO first:
1. Go to "Vehicles" tab
2. Click "▶️ Start Vehicles"
3. Let 50-100 vehicles spawn
4. Then run scenario (AI will detect and skip preparation)

### **Tip 2: Best Viewing**
- Keep chatbot window open to see live narration
- Watch the map for camera choreography
- Full screen recommended for best experience

### **Tip 3: Multiple Scenarios**
Run them in sequence:
```
1. run v2g scenario → confirm → wait for completion
2. restore all (to reset)
3. trigger blackout → confirm
4. restore all (to reset)
5. Repeat!
```

### **Tip 4: Skip Preparation**
If you already have lots of vehicles:
- V2G scenario will auto-detect 30+ high-SOC EVs
- Blackout will auto-detect 50+ total vehicles
- AI will skip spawning and go straight to scenario

---

## 🚨 IMPORTANT NOTES

### **Scenarios vs Real Commands:**

**❌ DON'T CONFUSE:**
- `activate v2g` = Real V2G activation (requires actual substation failure)
- `run v2g scenario` = **SIMULATION** (creates test scenario)

**✅ FOR TESTING, ALWAYS USE:**
- `run v2g scenario`
- `trigger blackout scenario`

These are **SIMULATIONS** - safe, repeatable, cinematic demonstrations!

---

### **System Requirements:**

**For V2G Scenario:**
- SUMO must be running (or AI will start it)
- Needs 30+ EVs with high battery (or AI will spawn them)

**For Blackout Scenario:**
- SUMO must be running (or AI will start it)
- Needs 50+ vehicles (or AI will spawn them)

---

## 🎊 EXPECTED CHAT EXPERIENCE

### **Perfect Run Output:**

```
User: run v2g scenario

Ultra-AI:
🎬 V2G EMERGENCY RESCUE SCENARIO

📋 Overview:
   Times Square substation fails, EVs provide emergency power

📊 Current System State:
   • Total vehicles: 23
   • Electric vehicles: 15
   • High-SOC EVs (70%+): 8

💡 Preparation Needed:
To run this scenario optimally, I'll spawn additional vehicles:
   • 42 EVs
   • Battery SOC: 70-95%
   • Reason: Need high-SOC EVs for V2G emergency response

🎥 What You'll See:
   1. Camera zooms to Times Square
   2. Substation fails (red alert!)
   3. EVs rush to provide emergency power
   4. Live progress tracking
   5. Automatic restoration when complete
   6. Success celebration and statistics

⏱️ Duration: ~60 seconds

Type "confirm" to prepare and start the scenario
Type "cancel" to abort

---

User: confirm

Ultra-AI: ✅ Confirmed! Starting V2G Rescue scenario...

[Live Narration:]
🚗 Preparing scenario environment...
⚡ Spawning 42 high-SOC electric vehicles...
✅ Vehicle preparation complete!
🎬 V2G EMERGENCY RESCUE SCENARIO STARTING
🎥 Positioning camera at Times Square...
[Camera smoothly zooms to Times Square]
🚨 EMERGENCY ALERT
⚠️ Times Square Substation - CRITICAL FAILURE
👥 18 people trapped in elevators
🎥 Zooming to action area...
[Camera zooms closer with tilt]
📢 Sending V2G recruitment notification...
⚡ V2G system activated - recruiting vehicles...
🎯 Target energy needed: 50 kWh
🎥 Dramatic close-up view...
[Camera zooms very close, tilted 60°, rotating]
🚗 5 vehicles active | ⚡ 12 / 50 kWh (24%)
🚗 8 vehicles active | ⚡ 28 / 50 kWh (56%)
🚗 12 vehicles active | ⚡ 45 / 50 kWh (90%)
🚗 12 vehicles active | ⚡ 52 / 50 kWh (104%)
✅ TARGET REACHED! Restoring substation...
🎥 Zooming out for final view...
[Camera zooms back out, levels off]
🔧 Times Square substation restored
💡 Traffic lights coming back online
🏢 Elevator systems operational

🎉 V2G RESCUE COMPLETE!

📊 Scenario Results:
   • Energy delivered: 52 kWh
   • Revenue generated: $156
   • Response time: Excellent
   • Mission: SUCCESS ✅
```

---

## 🔥 READY TO TEST!

Just type in the chatbot:

```
run v2g scenario
```

Then watch the world-class experience unfold! 🎬✨🚀

---

## 📞 Need Help?

- Type `help` in chatbot for capabilities
- Type `show scenarios` for scenario list
- Check console (F12) for technical details
- See `SCENARIO_TESTING_GUIDE.md` for troubleshooting
