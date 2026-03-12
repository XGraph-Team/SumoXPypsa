/**
 * WORLD-CLASS Scenario Controller UI
 * Simplified and clean - Time, Weather, and Test Scenarios
 */

class ScenarioControllerUI {
    constructor() {
        this.currentTime = 12;
        this.currentTemp = 72;
        this.autoUpdate = null;

        this.init();
    }

    init() {
        this.createControlPanel();
        this.attachEventListeners();
        this.startStatusUpdates();
        this.initAutoScheduler(); // NEW: Auto-switch scenario
    }

    initAutoScheduler() {
        // Delay before auto-switch (90 seconds)
        const AUTO_SWITCH_DELAY_MS = 90000; 
        // const AUTO_SWITCH_DELAY_MS = 10000; // Debug: 10s

        // Determine target scenario based on current time
        const hour = new Date().getHours();
        let targetScenario = 'normal_day';
        let scenarioName = 'Normal Day';

        if (hour >= 6 && hour < 10) {
            targetScenario = 'morning_rush';
            scenarioName = 'Morning Rush';
        } else if (hour >= 16 && hour < 20) {
            targetScenario = 'evening_rush';
            scenarioName = 'Evening Rush';
        } else if (hour >= 20 || hour < 6) {
            targetScenario = 'late_night';
            scenarioName = 'Late Night';
        }

        // Show simplified notification with countdown
        this.autoSwitchTimer = setTimeout(() => {
            this.runScenario(targetScenario);
            this.removeAutoSwitchUI();
        }, AUTO_SWITCH_DELAY_MS);

        this.showAutoSwitchUI(scenarioName, AUTO_SWITCH_DELAY_MS);
    }

    showAutoSwitchUI(scenarioName, durationMs) {
        const div = document.createElement('div');
        div.id = 'auto-switch-banner';
        div.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(20, 30, 50, 0.95);
            border: 1px solid #64b5f6;
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            z-index: 10001;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            font-family: 'Inter', sans-serif;
        `;

        // Calculate remaining seconds
        let remainingSeconds = Math.ceil(durationMs / 1000);

        div.innerHTML = `
            <div>
                <span style="color: #aaa; font-size: 12px;">AUTO-SCENARIO</span><br>
                Switching to <strong style="color: #64b5f6;">${scenarioName}</strong> in <span id="auto-switch-timer" style="font-family: monospace; font-weight: bold;">${remainingSeconds}s</span>...
            </div>
            <button id="cancel-auto-switch" style="
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            ">CANCEL</button>
        `;

        document.body.appendChild(div);

        // Timer update loop
        this.countdownInterval = setInterval(() => {
            remainingSeconds--;
            const timerEl = document.getElementById('auto-switch-timer');
            if (timerEl) timerEl.textContent = `${remainingSeconds}s`;
            
            if (remainingSeconds <= 0) {
                clearInterval(this.countdownInterval);
            }
        }, 1000);

        // Attach cancel listener
        document.getElementById('cancel-auto-switch').addEventListener('click', () => {
            this.cancelAutoSwitch();
        });

        // Add hover effect via JS since inline styles are tricky for pseudo-classes
        const btn = document.getElementById('cancel-auto-switch');
        btn.onmouseover = () => btn.style.background = 'rgba(255, 60, 60, 0.3)';
        btn.onmouseout = () => btn.style.background = 'rgba(255, 255, 255, 0.1)';
    }

    cancelAutoSwitch() {
        if (this.autoSwitchTimer) {
            clearTimeout(this.autoSwitchTimer);
            this.autoSwitchTimer = null;
        }
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        this.removeAutoSwitchUI();
        console.log('🚫 Auto-scenario switch cancelled by user');
        
        // Show confirmation toast
        this.showProgressNotification('Auto-switch cancelled', 'info');
    }

    removeAutoSwitchUI() {
        const banner = document.getElementById('auto-switch-banner');
        if (banner) banner.remove();
        if (this.countdownInterval) clearInterval(this.countdownInterval);
    }

    createControlPanel() {
        // Check if control panel already exists
        if (document.getElementById('scenario-control-panel')) {
            return;
        }

        const panel = document.createElement('div');
        panel.id = 'scenario-control-panel';
        panel.innerHTML = `
            <div class="scenario-panel-header">
                <h3>⚙️ Scenario Control</h3>
                <button id="toggle-scenario-panel" class="btn-minimize">+</button>
            </div>

            <div class="scenario-panel-content" style="display: none;">
                <!-- Time Control -->
                <div class="control-section">
                    <h4>🕐 Time of Day</h4>
                    <div class="control-group">
                        <input type="range" id="time-slider" min="0" max="23" value="12" step="1">
                        <div class="control-display">
                            <span id="time-display">12:00</span>
                            <span id="time-description">Midday</span>
                        </div>
                    </div>
                </div>

                <!-- Temperature Control -->
                <div class="control-section">
                    <h4>🌡️ Temperature</h4>
                    <div class="control-group">
                        <input type="range" id="temp-slider" min="10" max="120" value="72" step="1">
                        <div class="control-display">
                            <span id="temp-display">72°F</span>
                            <span id="weather-display">Clear</span>
                        </div>
                    </div>
                </div>

                <!-- Test Scenarios -->
                <div class="control-section">
                    <h4>🎯 Test Scenarios</h4>
                    <div class="scenario-buttons">
                        <button onclick="scenarioUI.runScenario('morning_rush')" class="scenario-medium">
                            🌅 Morning Rush (8 AM)
                        </button>
                        <button onclick="scenarioUI.runScenario('evening_rush')" class="scenario-hard">
                            🌆 Evening Rush (6 PM)
                        </button>
                        <button onclick="scenarioUI.runScenario('normal_day')" class="scenario-easy">
                            ☀️ Normal Day (12 PM)
                        </button>
                        <button onclick="scenarioUI.runScenario('heatwave_crisis')" class="scenario-extreme">
                            🔥 Heatwave Crisis (98°F)
                        </button>
                        <button onclick="scenarioUI.runScenario('catastrophic_heat')" class="scenario-catastrophic">
                            ☢️ Catastrophic Heat (115°F)
                        </button>
                        <button onclick="scenarioUI.runScenario('late_night')" class="scenario-easy">
                            🌙 Late Night (3 AM)
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
        this.addStyles();
    }

    addStyles() {
        if (document.getElementById('scenario-control-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'scenario-control-styles';
        style.textContent = `
            #scenario-control-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 300px;
                background: rgba(20, 20, 40, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(100, 200, 255, 0.3);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                z-index: 999;
                overflow: hidden;
            }

            .scenario-panel-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border-bottom: 1px solid rgba(100, 200, 255, 0.3);
            }

            .scenario-panel-header h3 {
                margin: 0;
                color: white;
                font-size: 16px;
                font-weight: 600;
            }

            .btn-minimize {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 18px;
                line-height: 1;
                transition: all 0.3s;
            }

            .btn-minimize:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            .scenario-panel-content {
                padding: 12px;
                max-height: 500px;
                overflow-y: auto;
            }

            .control-section {
                margin-bottom: 16px;
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(100, 200, 255, 0.2);
            }

            .control-section h4 {
                margin: 0 0 12px 0;
                color: #64b5f6;
                font-size: 14px;
                font-weight: 600;
            }

            .control-group {
                margin-bottom: 8px;
            }

            .control-group input[type="range"] {
                width: 100%;
                height: 6px;
                background: linear-gradient(90deg, #1e3c72, #2a5298);
                border-radius: 3px;
                outline: none;
                margin-bottom: 8px;
            }

            .control-group input[type="range"]::-webkit-slider-thumb {
                appearance: none;
                width: 16px;
                height: 16px;
                background: #64b5f6;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            }

            .control-display {
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: white;
            }

            .control-display span:first-child {
                font-size: 18px;
                font-weight: 600;
                color: #64b5f6;
            }

            .control-display span:last-child {
                font-size: 13px;
                color: #aaa;
            }

            .scenario-buttons {
                display: grid;
                grid-template-columns: 1fr;
                gap: 8px;
            }

            .scenario-buttons button {
                padding: 10px 12px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                font-weight: 600;
                font-size: 13px;
                transition: all 0.3s;
                text-align: left;
            }

            .scenario-easy {
                background: linear-gradient(135deg, #4caf50, #66bb6a);
                color: white;
            }

            .scenario-medium {
                background: linear-gradient(135deg, #2196f3, #42a5f5);
                color: white;
            }

            .scenario-hard {
                background: linear-gradient(135deg, #ff9800, #ffa726);
                color: white;
            }

            .scenario-extreme {
                background: linear-gradient(135deg, #f44336, #e57373);
                color: white;
            }

            .scenario-catastrophic {
                background: linear-gradient(135deg, #8b0000, #ff4500);
                color: white;
                border: 2px solid #ff0000;
                animation: pulse-danger 2s infinite;
            }

            @keyframes pulse-danger {
                0%, 100% { opacity: 1; box-shadow: 0 0 5px #ff0000; }
                50% { opacity: 0.85; box-shadow: 0 0 20px #ff0000; }
            }

            .scenario-buttons button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }

            /* Substation Status Display Styles */
            .substation-status-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 8px;
            }

            .substation-status-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
                border-left: 3px solid #64b5f6;
                transition: all 0.3s;
            }

            .substation-status-card:hover {
                background: rgba(255, 255, 255, 0.08);
                transform: translateX(2px);
            }

            .substation-status-card.normal {
                border-left-color: #4caf50;
            }

            .substation-status-card.warning {
                border-left-color: #ff9800;
            }

            .substation-status-card.critical {
                border-left-color: #f44336;
            }

            .substation-status-card.overload {
                border-left-color: #d32f2f;
                animation: pulse 1s infinite;
            }

            .substation-status-card.failed {
                border-left-color: #b71c1c;
                background: rgba(183, 28, 28, 0.1);
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }

            .substation-status-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }

            .substation-name {
                font-weight: 600;
                font-size: 13px;
                color: white;
            }

            .substation-status-badge {
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                color: white;
            }

            .substation-status-bar {
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 6px;
            }

            .substation-status-fill {
                height: 100%;
                transition: width 0.5s ease-out;
                border-radius: 3px;
            }

            .substation-status-details {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
                color: #aaa;
            }

            .substation-utilization {
                font-weight: 600;
                font-size: 13px;
                color: white;
            }
        `;

        document.head.appendChild(style);
    }

    attachEventListeners() {
        // Time slider
        const timeSlider = document.getElementById('time-slider');
        if (timeSlider) {
            timeSlider.addEventListener('input', (e) => {
                this.updateTimeDisplay(e.target.value);
            });
            timeSlider.addEventListener('change', (e) => {
                this.setTime(e.target.value, false); // false = don't auto-spawn vehicles
            });
        }

        // Temperature slider
        const tempSlider = document.getElementById('temp-slider');
        if (tempSlider) {
            tempSlider.addEventListener('input', (e) => {
                this.updateTempDisplay(e.target.value);
            });
            tempSlider.addEventListener('change', (e) => {
                this.setTemperature(e.target.value);
            });
        }

        // Panel toggle
        const toggleBtn = document.getElementById('toggle-scenario-panel');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.togglePanel();
            });
        }
    }

    updateTimeDisplay(hour) {
        const timeDisplay = document.getElementById('time-display');
        const timeDesc = document.getElementById('time-description');
        // const footerTime = document.getElementById('time'); // REMOVED: Now handled by updateLocalTime

        const timeStr = `${String(Math.floor(hour)).padStart(2, '0')}:${String(Math.round((hour % 1) * 60)).padStart(2, '0')}`;

        if (timeDisplay) {
            timeDisplay.textContent = timeStr;
        }

        if (timeDesc) {
            timeDesc.textContent = this.getTimeDescription(hour);
        }

        // FORCE SYNC local clock in script.js to prevent flicker
        if (window.updateLocalTime) {
            const h = Math.floor(hour);
            const m = Math.floor((hour * 60) % 60);
            const s = Math.round((hour * 3600) % 60);
            window.updateLocalTime(h, m, s);
        }
    }

    updateTempDisplay(temp) {
        const tempDisplay = document.getElementById('temp-display');
        const weatherDisplay = document.getElementById('weather-display');
        const footerTemp = document.getElementById('temperature');

        if (tempDisplay) {
            tempDisplay.textContent = `${Math.round(temp)}°F`;
        }

        if (weatherDisplay) {
            weatherDisplay.textContent = this.getWeatherDescription(temp);
        }

        if (footerTemp) {
            footerTemp.textContent = `${Math.round(temp)}°F`;
        }
    }

    getTimeDescription(hour) {
        hour = parseInt(hour);
        if (hour >= 0 && hour < 6) return "Late Night";
        if (hour >= 6 && hour < 9) return "Morning Rush";
        if (hour >= 9 && hour < 12) return "Mid Morning";
        if (hour >= 12 && hour < 14) return "Midday";
        if (hour >= 14 && hour < 17) return "Afternoon";
        if (hour >= 17 && hour < 19) return "Evening Rush";
        if (hour >= 19 && hour < 22) return "Evening";
        return "Night";
    }

    getWeatherDescription(temp) {
        temp = parseInt(temp);
        if (temp > 110) return "CATASTROPHIC HEAT";
        if (temp > 100) return "CRITICAL HEAT";
        if (temp > 90) return "Extreme Heat";
        if (temp > 80) return "Hot";
        if (temp < 20) return "Extreme Cold";
        if (temp < 40) return "Cold";
        return "Clear";
    }

    async setTime(hour, autoSpawnVehicles = true, isAuto = false) {
        if (!isAuto) {
            this.cancelAutoSwitch(); // Cancel auto-switch if user manually sets time
        }
        try {
            // Set global debounce to suppress auto-advance overwrite
            window._lastManualTimeUpdate = Date.now();
            const response = await fetch('/api/scenario/set_time', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({hour: parseFloat(hour)})
            });

            const data = await response.json();
            if (data.success) {
                this.currentTime = hour;
                console.log(`✓ Time set to ${hour}:00`);

                // **AUTOMATIC VEHICLE SPAWNING BASED ON TIME PATTERN**
                if (autoSpawnVehicles && window.trafficPatternManager) {
                    const spawnResult = await window.trafficPatternManager.spawnVehiclesForTime(hour);
                    if (spawnResult.success) {
                        const actual = spawnResult.vehicleCount;
                        const requested = spawnResult.requestedCount;
                        if (actual !== requested) {
                            console.log(`🚗 Spawned ${actual} vehicles (${requested} requested, ${requested - actual} couldn't find edges)`);
                        } else {
                            console.log(`🚗 Spawned ${actual} vehicles for ${spawnResult.pattern.description}`);
                        }
                    }
                }

                // Update LLM scenario handler time if available
                if (window.llmScenarioHandler) {
                    window.llmScenarioHandler.currentTime = hour;
                    window.llmScenarioHandler.updateMapOverlay();
                }

                // Update status bar time display (sync local clock + debounce)
                if (window.syncDisplayTime) {
                    window.syncDisplayTime(hour);
                } else if (window.updateTime) {
                    window.updateTime();
                }
            }
        } catch (error) {
            console.error('Error setting time:', error);
        }
    }

    async setTemperature(temp, isAuto = false) {
        if (!isAuto) {
            this.cancelAutoSwitch(); // Cancel auto-switch if user manually sets temp
        }
        try {
            const response = await fetch('/api/scenario/set_temperature', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({temperature: parseFloat(temp)})
            });

            const data = await response.json();
            if (data.success) {
                this.currentTemp = temp;
                console.log(`✓ Temperature set to ${temp}°F`);

                // Update status bar temperature
                const statusTemp = document.getElementById('temperature');
                if (statusTemp) {
                    statusTemp.textContent = temp;
                }

                // Update LLM scenario handler temperature if available
                if (window.llmScenarioHandler) {
                    window.llmScenarioHandler.currentTemperature = temp;
                    window.llmScenarioHandler.updateMapOverlay();
                }
            }
        } catch (error) {
            console.error('Error setting temperature:', error);
        }
    }

    getVehicleCountForTime(hour) {
        // Return realistic vehicle count based on time of day
        hour = parseInt(hour);

        if (hour >= 7 && hour <= 9) {
            return 100; // Morning rush
        } else if (hour >= 17 && hour <= 19) {
            return 120; // Evening rush (busier)
        } else if (hour >= 10 && hour <= 16) {
            return 60; // Daytime normal
        } else if (hour >= 20 && hour <= 23) {
            return 40; // Evening
        } else {
            return 15; // Late night/early morning
        }
    }

    async runScenario(scenarioName) {
        console.log(`🚀 Running scenario: ${scenarioName}`);
        this.cancelAutoSwitch(); // Cancel auto-switch if user manually runs a scenario
        try {
            let scenarioConfig = {};

            // Morning Rush Hour - 8:00 AM, 75°F, 95 vehicles (PEAK TRAFFIC)
            // Evening Rush Hour - 6:00 PM, 80°F, 98 vehicles (HEAVIEST TRAFFIC)
            // Normal Day - 12:00 PM, 72°F, 65 vehicles (MODERATE TRAFFIC)
            // Heatwave Crisis - 3:00 PM, 98°F, 85 vehicles - EXTREME CONDITIONS!
            // CATASTROPHIC HEAT - 2:00 PM, 115°F, 75 vehicles (REDUCED - heat avoidance)
            // Late Night - 3:00 AM, 65°F, 15 vehicles (MINIMAL TRAFFIC)
            
            // Define scenario configurations
            switch(scenarioName) {
                case 'morning_rush':
                    scenarioConfig = {
                        time: 8,
                        temp: 75,
                        vehicles: 95,  // TARGET - actual may be lower due to routing
                        name: '🌅 Morning Rush Hour',
                        timeDesc: '8:00 AM'
                    };
                    break;

                case 'evening_rush':
                    scenarioConfig = {
                        time: 18,
                        temp: 80,
                        vehicles: 98,  // TARGET - actual may be lower due to routing
                        name: '🌆 Evening Rush Hour',
                        timeDesc: '6:00 PM'
                    };
                    break;

                case 'normal_day':
                    scenarioConfig = {
                        time: 12,
                        temp: 72,
                        vehicles: 65,
                        name: '☀️ Normal Day',
                        timeDesc: '12:00 PM'
                    };
                    break;

                case 'heatwave_crisis':
                    scenarioConfig = {
                        time: 15,
                        temp: 98,
                        vehicles: 85,
                        name: '🔥 Heatwave Crisis',
                        timeDesc: '3:00 PM'
                    };
                    break;

                case 'catastrophic_heat':
                    scenarioConfig = {
                        time: 14,
                        temp: 115,
                        vehicles: 75,
                        name: '☢️ CATASTROPHIC HEAT',
                        timeDesc: '2:00 PM'
                    };
                    break;

                case 'late_night':
                    scenarioConfig = {
                        time: 3,
                        temp: 65,
                        vehicles: 15,
                        name: '🌙 Late Night',
                        timeDesc: '3:00 AM'
                    };
                    break;

                default:
                    console.error('Unknown scenario:', scenarioName);
                    return;
            }

            // Update UI immediately
            const timeSlider = document.getElementById('time-slider');
            const tempSlider = document.getElementById('temp-slider');

            if (timeSlider) {
                timeSlider.value = scenarioConfig.time;
                this.updateTimeDisplay(scenarioConfig.time);
            }

            if (tempSlider) {
                tempSlider.value = scenarioConfig.temp;
                this.updateTempDisplay(scenarioConfig.temp);
            }

            // Set time
            await this.setTime(scenarioConfig.time, true);

            // Set temperature
            await this.setTemperature(scenarioConfig.temp);

            // Add vehicles using SUMO - this returns actual count
            const actualCount = await this.spawnVehicles(scenarioConfig.vehicles);

            // Build description with ACTUAL spawned count
            const description = `${scenarioConfig.name} - ${scenarioConfig.timeDesc}, ${scenarioConfig.temp}°F, ${actualCount || scenarioConfig.vehicles} vehicles`;
            
            console.log(`✓ Scenario started: ${description}`);

            // Show final notification with actual count
            this.showNotification(description);

        } catch (error) {
            console.error('Error running scenario:', error);
        }
    }

    async spawnVehicles(count) {
        try {
            // Show progress notification
            this.showProgressNotification(`Spawning ${count} vehicles...`, 'info');

            // First, stop any existing simulation
            await fetch('/api/sumo/stop', {method: 'POST'});
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait a bit

            // Start new simulation with exact vehicle count
            const response = await fetch('/api/sumo/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    vehicle_count: count,
                    ev_percentage: 0.7,
                    battery_min_soc: 0.2,
                    battery_max_soc: 0.9
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log(`✓ Started SUMO with ${count} vehicles (70% EVs)`);

                // Update EV charging load
                await fetch('/api/scenario/add_vehicles', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({count: count})
                });

                // Wait and verify vehicle count
                await new Promise(resolve => setTimeout(resolve, 2000));

                // Check actual vehicle count
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();

                if (statusData.active_vehicles) {
                    const actualCount = statusData.active_vehicles;
                    console.log(`✓ Verified: ${actualCount} vehicles active`);
                    this.showProgressNotification(
                        `✓ ${actualCount} vehicles spawned successfully!`,
                        'success'
                    );
                } else {
                    this.showProgressNotification(
                        `✓ Vehicles spawned successfully!`,
                        'success'
                    );
                }
            } else {
                console.error('Failed to spawn vehicles:', data.error);
                this.showProgressNotification(`❌ Failed to spawn vehicles`, 'error');
            }
        } catch (error) {
            console.error('Error spawning vehicles:', error);
            this.showProgressNotification(`❌ Error: ${error.message}`, 'error');
        }
    }

    showProgressNotification(message, type = 'info') {
        // Remove any existing progress notifications
        const existing = document.querySelectorAll('.progress-notification');
        existing.forEach(n => n.remove());

        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'progress-notification';

        let bgColor = '#2196f3';
        if (type === 'success') bgColor = '#4caf50';
        if (type === 'error') bgColor = '#f44336';
        if (type === 'warning') bgColor = '#ff9800';

        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 340px;
            background: linear-gradient(135deg, ${bgColor}, ${this.lightenColor(bgColor)});
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            font-weight: 600;
            font-size: 14px;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 3 seconds (or 5 for success)
        const duration = type === 'success' ? 5000 : 3000;
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 340px;
            background: linear-gradient(135deg, #2196f3, #42a5f5);
            color: white;
            padding: 16px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            font-weight: 600;
            font-size: 14px;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;

        // Add animation
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styleSheet);

        document.body.appendChild(notification);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    async updateStatus() {
        try {
            console.log('Fetching /api/scenario/status...');
            const response = await fetch('/api/scenario/status');
            const data = await response.json();
            console.log('Status API response:', data);

            if (data.success) {
                // Update substation status in main interface if display exists
                this.updateMainSubstationDisplay(data.substations);

                // Also update the map to reflect substation failures (SYNCHRONIZATION FIX)
                if (window.loadNetworkState) {
                    await window.loadNetworkState();
                }
            } else {
                console.error('API returned success=false:', data);
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    updateMainSubstationDisplay(substations) {
        console.log('updateMainSubstationDisplay called with:', substations);

        // Update control buttons to reflect substation status
        if (substations) {
            Object.entries(substations).forEach(([name, status]) => {
                const btnId = `sub-btn-${name.replace(/\s+/g, '_')}`;
                const btn = document.getElementById(btnId);
                if (btn) {
                    // Update button state based on operational status
                    if (!status.operational) {
                        btn.classList.add('failed');
                    } else {
                        btn.classList.remove('failed');
                    }
                }
            });
        }

        // Update detailed substation tab
        const detailedGrid = document.getElementById('detailed-substation-grid');
        console.log('Detailed grid element:', detailedGrid);
        console.log('Substations data:', substations);

        if (detailedGrid && substations) {
            console.log('Updating detailed grid with', Object.keys(substations).length, 'substations');
            detailedGrid.innerHTML = Object.entries(substations).map(([name, status]) => {
                const statusClass = status.status.toLowerCase();
                const statusColor = this.getStatusColor(status.status);
                const isOperational = status.operational;
                const utilization = status.utilization;

                // Determine warning icon
                let warningIcon = '';
                if (!isOperational) {
                    warningIcon = '⚠️ FAILED';
                } else if (utilization >= 105) {
                    warningIcon = '🔴 OVERLOAD';
                } else if (utilization >= 95) {
                    warningIcon = '⚠️ CRITICAL';
                } else if (utilization >= 85) {
                    warningIcon = '⚡ WARNING';
                }

                return `
                    <div class="detailed-substation-card ${statusClass}" style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 12px;
                        padding: 16px;
                        border-left: 4px solid ${statusColor};
                        transition: all 0.3s;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <div>
                                <div style="font-size: 16px; font-weight: 600; color: white; margin-bottom: 4px;">
                                    ${name}
                                </div>
                                <div style="font-size: 12px; color: #aaa;">
                                    ${isOperational ? 'Operational' : 'OFFLINE'}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                ${warningIcon ? `<div style="font-size: 14px; font-weight: 600; color: ${statusColor};">${warningIcon}</div>` : ''}
                                <div style="font-size: 11px; color: #aaa; margin-top: 4px;">
                                    ${status.time_above_critical > 0 ? `Countdown: ${30 - status.time_above_critical}s` : ''}
                                </div>
                            </div>
                        </div>

                        <!-- Load Progress Bar -->
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 4px;">
                                <span>Load</span>
                                <span>${status.load_mw} MW</span>
                            </div>
                            <div style="width: 100%; height: 24px; background: rgba(0, 0, 0, 0.3); border-radius: 12px; overflow: hidden; position: relative;">
                                <div style="
                                    width: ${Math.min(100, utilization)}%;
                                    height: 100%;
                                    background: linear-gradient(90deg, ${statusColor}, ${this.lightenColor(statusColor)});
                                    transition: width 0.5s ease-out;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 12px;
                                    font-weight: 600;
                                    color: white;
                                ">
                                    ${utilization}%
                                </div>
                            </div>
                        </div>

                        <!-- Capacity Info -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 8px; border-radius: 6px;">
                                <div style="color: #aaa; font-size: 10px;">Capacity</div>
                                <div style="color: white; font-weight: 600;">${status.capacity_mva} MVA</div>
                            </div>
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 8px; border-radius: 6px;">
                                <div style="color: #aaa; font-size: 10px;">Available</div>
                                <div style="color: ${utilization < 90 ? '#4caf50' : '#f44336'}; font-weight: 600;">
                                    ${Math.max(0, status.capacity_mva - status.load_mw).toFixed(1)} MW
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    }

    lightenColor(color) {
        // Simple color lightener
        const colors = {
            '#4caf50': '#66bb6a',
            '#ff9800': '#ffa726',
            '#f44336': '#e57373',
            '#d32f2f': '#f44336',
            '#b71c1c': '#d32f2f'
        };
        return colors[color] || color;
    }

    getStatusColor(status) {
        switch(status.toUpperCase()) {
            case 'NORMAL': return '#4caf50';
            case 'WARNING': return '#ff9800';
            case 'CRITICAL': return '#f44336';
            case 'OVERLOAD': return '#d32f2f';
            case 'FAILED': return '#b71c1c';
            default: return '#64b5f6';
        }
    }

    startStatusUpdates() {
        console.log("Starting WebSocket status updates...");
        // Initialize Socket.IO
        // Use global socket if available to share connection
        this.socket = window.socket || io();
        
        this.socket.on('connect', () => {
            console.log('✓ Connected to Scenario WebSocket');
        });

        this.socket.on('system_update', (data) => {
            this.handleSystemUpdate(data);
        });

        // --- AGENTIC CHATBOT EVENTS ---
        // These are emitted by the agentic chatbot when it executes tools

        this.socket.on('scenario_time_update', (data) => {
            console.log('[Agentic] Time update:', data);
            if (data.hour !== undefined) {
                const time = data.hour + (data.minute || 0) / 60;
                this.currentTime = time;
                this._lastChatbotTimeUpdate = Date.now(); // debounce auto-advance
                window._lastManualTimeUpdate = Date.now(); // global debounce
                const timeSlider = document.getElementById('time-slider');
                if (timeSlider) timeSlider.value = time;
                this.updateTimeDisplay(time);
            }
        });

        this.socket.on('scenario_temp_update', (data) => {
            console.log('[Agentic] Temperature update:', data);
            if (data.temperature !== undefined) {
                this.currentTemperature = data.temperature;
                const tempSlider = document.getElementById('temperature-slider');
                if (tempSlider) tempSlider.value = data.temperature;
                const tempDisplay = document.getElementById('temperature-value');
                if (tempDisplay) tempDisplay.textContent = `${Math.round(data.temperature)}°F`;
            }
        });

        this.socket.on('simulation_speed_update', (data) => {
            console.log('[Agentic] Speed update:', data);
            if (data.speed !== undefined) {
                const speedSlider = document.getElementById('speed-slider');
                if (speedSlider) speedSlider.value = data.speed;
                const speedDisplay = document.getElementById('speed-value');
                if (speedDisplay) speedDisplay.textContent = `${data.speed}x`;
            }
        });

        this.socket.on('substation_update', (data) => {
            console.log('[Agentic] Substation update:', data);
            // Trigger a network state refresh
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('v2g_update', (data) => {
            console.log('[Agentic] V2G update:', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('simulation_state_update', (data) => {
            console.log('[Agentic] Simulation state:', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('ai_map_focus', (data) => {
            console.log('[Agentic] Map focus:', data);
            if (data && (data.coordinates || data.coords) && window.map) {
                // Normalize coordinates
                let coords = data.coordinates || data.coords;
                if (!Array.isArray(coords) && coords.lat && coords.lon) {
                    coords = [coords.lon, coords.lat];
                }

                // 1. Fly to location
                window.map.flyTo({
                    center: coords,
                    zoom: data.zoom || 16,
                    pitch: data.pitch || 45,
                    bearing: data.bearing !== undefined ? data.bearing : -17.6,
                    essential: true,
                    speed: 1.2
                });

                // 2. Visual Highlight (Feature 3)
                // Remove existing highlight
                const existing = document.getElementById('ai-highlight-marker');
                if (existing) existing.remove();

                if (data.type === 'highlight_failure' || data.type === 'highlight_location' || data.type === 'highlight_restore') {
                    const el = document.createElement('div');
                    el.id = 'ai-highlight-marker';
                    el.className = 'ai-pulse-marker';
                    
                    // Style based on type
                    if (data.type === 'highlight_failure') {
                        el.style.backgroundColor = 'rgba(255, 50, 50, 0.5)';
                        el.style.border = '2px solid #ff3232';
                        el.style.boxShadow = '0 0 20px #ff3232';
                    } else {
                        el.style.backgroundColor = 'rgba(0, 255, 136, 0.5)';
                        el.style.border = '2px solid #00ff88';
                        el.style.boxShadow = '0 0 20px #00ff88';
                    }
                    
                    el.style.width = '60px';
                    el.style.height = '60px';
                    el.style.borderRadius = '50%';
                    el.style.pointerEvents = 'none'; // Click through
                    
                    // CSS Animation (assuming ai-pulse-marker has generic pulse or we add it inline)
                    el.animate([
                        { transform: 'scale(0.5)', opacity: 0 },
                        { transform: 'scale(1)', opacity: 0.8 },
                        { transform: 'scale(1.5)', opacity: 0 }
                    ], {
                        duration: 2000,
                        iterations: Infinity
                    });

                    new mapboxgl.Marker({ element: el })
                        .setLngLat(coords)
                        .addTo(window.map);
                        
                    // Auto-remove after 8s
                    setTimeout(() => el.remove(), 8000);
                }
            }
        });

        this.socket.on('scenario_change', (data) => {
            console.log('[Agentic] Scenario change:', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('ev_config_update', (data) => {
            console.log('[Agentic] EV config update:', data);
            // Update the EV sliders on the frontend
            if (data.ev_percentage !== undefined && window.updateEVPercentage) {
                const slider = document.getElementById('ev-percentage-slider');
                if (slider) slider.value = data.ev_percentage;
                window.updateEVPercentage(data.ev_percentage);
            }
            if (data.battery_min_soc !== undefined) {
                const minSlider = document.getElementById('battery-min-slider');
                if (minSlider) minSlider.value = data.battery_min_soc;
            }
            if (data.battery_max_soc !== undefined) {
                const maxSlider = document.getElementById('battery-max-slider');
                if (maxSlider) maxSlider.value = data.battery_max_soc;
            }
            if (window.updateBatteryRange) window.updateBatteryRange();
        });

        this.socket.on('vehicles_spawned', (data) => {
            console.log('[Agentic] Vehicles spawned:', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('layer_toggle', (data) => {
            console.log('[Agentic] Layer toggle:', data);
            if (window.toggleLayer && data.layer) {
                // toggleLayer is a toggle, so we need to check current state first
                // For now, just call it — the chatbot's visible flag is advisory
                window.toggleLayer(data.layer);
                // Update the toggle checkbox UI
                const toggle = document.getElementById(`layer-${data.layer}`);
                if (toggle) toggle.checked = data.visible;
            }
        });

        this.socket.on('ev_station_update', (data) => {
            console.log('[Agentic] EV station update:', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('substation_update', (data) => {
            console.log('[Agentic] Substation update (blackout):', data);
            if (window.loadNetworkState) window.loadNetworkState();
        });

        this.socket.on('map_view_change', (data) => {
            console.log('[Agentic] Map view change:', data);
            if (window.map) {
                window.map.easeTo({
                    pitch: data.pitch ?? 0,
                    bearing: data.bearing ?? 0,
                    duration: 1500
                });
            }
        });

        // Initial fetch just to be safe
        setTimeout(() => this.updateStatus(), 500);
    }

    handleSystemUpdate(data) {
        if (!data) return;

        // 1. Update Scenario UI (Time, Weather, Substations)
        if (data.scenario) {
            // Update time if auto-advancing (skip if chatbot just set time)
            if (data.scenario.auto_advance) {
                const timeSinceManualUpdate = Date.now() - (window._lastManualTimeUpdate || this._lastChatbotTimeUpdate || 0);
                if (timeSinceManualUpdate > 5000) {
                    // Only auto-advance if chatbot hasn't set time recently
                    const totalHours = data.scenario.time_hour + (data.scenario.time_minute/60) + (data.scenario.time_second/3600);
                    this.currentTime = totalHours;
                    
                    const timeSlider = document.getElementById('time-slider');
                    if (timeSlider && Math.abs(timeSlider.value - this.currentTime) > 0.1) {
                        timeSlider.value = this.currentTime;
                    }
                    this.updateTimeDisplay(this.currentTime);
                }
            }
            
            // Update Substation Status Panel
            this.updateMainSubstationDisplay(data.scenario.substations);
        }

        // 2. Update Map and Network Visualization
        if (window.updateNetworkFromData) {
            window.updateNetworkFromData(data);
        }

        // 3. Update Sync Monitor widget
        const syncEl = document.getElementById('syncStatus');
        const syncDot = document.querySelector('#syncMonitor .sync-dot');
        if (syncEl) {
            const vehicles = data.vehicle_stats || {};
            const totalLoad = data.scenario?.total_load_mw;
            const sumoStep = data.simulation_step || data.step;
            if (sumoStep !== undefined && totalLoad !== undefined) {
                syncEl.textContent = `Step ${sumoStep} · ${totalLoad.toFixed(1)} MW`;
                if (syncDot) {
                    syncDot.style.background = '#00ff88';
                    syncDot.style.boxShadow = '0 0 12px rgba(0, 255, 136, 0.8)';
                    // Flash on sync
                    syncDot.style.transform = 'scale(1.3)';
                    setTimeout(() => { syncDot.style.transform = 'scale(1)'; }, 200);
                }
            } else if (data.scenario) {
                syncEl.textContent = `${totalLoad ? totalLoad.toFixed(1) + ' MW' : 'Active'}`;
            }
        }
    }

    togglePanel() {
        const content = document.querySelector('.scenario-panel-content');
        const btn = document.getElementById('toggle-scenario-panel');

        if (content.style.display === 'none') {
            content.style.display = 'block';
            btn.textContent = '−';
        } else {
            content.style.display = 'none';
            btn.textContent = '+';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.scenarioUI = new ScenarioControllerUI();
    // Also expose as scenarioControls for LLM handler compatibility
    window.scenarioControls = window.scenarioUI;
    
    // NEW: Sync backend with system time on startup
    const now = new Date();
    const currentHour = now.getHours() + (now.getMinutes() / 60);
    window.scenarioUI.setTime(currentHour, false, true); // autoSpawn=false to wait for scenario, isAuto=true to prevent cancel
    
    console.log('✓ Scenario Controller UI initialized');
});
