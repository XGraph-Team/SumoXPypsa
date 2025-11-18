/**
 * TIME PROGRESSION & VEHICLE QUOTA MANAGEMENT
 * - Progressive time system (12:00 -> 12:01 -> 12:02...)
 * - Continuous vehicle spawning based on time-of-day quotas
 */

class TimeVehicleManager {
    constructor() {
        this.timeEnabled = false;
        this.currentHour = 12;
        this.currentMinute = 0;
        this.timeInterval = null;
        this.vehicleCheckInterval = null;

        // Time progression speed (ms per minute in simulation)
        this.timeSpeed = 1000; // 1 second real time = 1 minute simulation time

        console.log('✅ Time & Vehicle Manager initialized');
    }

    /**
     * Start progressive time system
     */
    startTimeProgression(startHour = 12, startMinute = 0) {
        this.currentHour = startHour;
        this.currentMinute = startMinute;
        this.timeEnabled = true;

        // Clear existing interval
        if (this.timeInterval) {
            clearInterval(this.timeInterval);
        }

        // Increment time every second (1 simulation minute)
        this.timeInterval = setInterval(() => {
            if (this.timeEnabled) {
                this.incrementTime();
                this.updateTimeDisplay();

                // Check if hour changed (for vehicle quota updates)
                if (this.currentMinute === 0) {
                    this.onHourChange();
                }
            }
        }, this.timeSpeed);

        // Start vehicle quota monitoring
        this.startVehicleQuotaMonitoring();

        console.log(`⏰ Time progression started at ${this.currentHour}:${String(this.currentMinute).padStart(2, '0')}`);
    }

    /**
     * Stop progressive time system
     */
    stopTimeProgression() {
        this.timeEnabled = false;

        if (this.timeInterval) {
            clearInterval(this.timeInterval);
            this.timeInterval = null;
        }

        if (this.vehicleCheckInterval) {
            clearInterval(this.vehicleCheckInterval);
            this.vehicleCheckInterval = null;
        }

        console.log('⏰ Time progression stopped');
    }

    /**
     * Increment time by 1 minute
     */
    incrementTime() {
        this.currentMinute++;

        if (this.currentMinute >= 60) {
            this.currentMinute = 0;
            this.currentHour++;

            if (this.currentHour >= 24) {
                this.currentHour = 0;
            }
        }
    }

    /**
     * Update time display in UI
     */
    updateTimeDisplay() {
        const timeEl = document.getElementById('time');
        if (timeEl) {
            const formattedTime = `${String(this.currentHour).padStart(2, '0')}:${String(this.currentMinute).padStart(2, '0')}`;
            timeEl.textContent = formattedTime;
        }

        // Update LLM scenario handler if available
        if (window.llmScenarioHandler) {
            window.llmScenarioHandler.currentTime = this.currentHour;
            window.llmScenarioHandler.updateMapOverlay();
        }
    }

    /**
     * Called when hour changes (for major updates)
     */
    onHourChange() {
        console.log(`🕐 Hour changed to ${this.currentHour}:00`);

        // Update scenario controls if available
        if (window.scenarioControls) {
            window.scenarioControls.currentTime = this.currentHour;
            const timeSlider = document.getElementById('time-slider');
            if (timeSlider) {
                timeSlider.value = this.currentHour;
                const timeLabel = document.getElementById('time-label');
                if (timeLabel) {
                    timeLabel.textContent = `${String(this.currentHour).padStart(2, '0')}:00`;
                }
            }
        }
    }

    /**
     * Start monitoring vehicle quotas and spawn as needed
     */
    startVehicleQuotaMonitoring() {
        // Clear existing interval
        if (this.vehicleCheckInterval) {
            clearInterval(this.vehicleCheckInterval);
        }

        // Check vehicle quota every 5 seconds
        this.vehicleCheckInterval = setInterval(async () => {
            if (this.timeEnabled) {
                await this.checkAndMaintainVehicleQuota();
            }
        }, 5000);

        console.log('🚗 Vehicle quota monitoring started');
    }

    /**
     * Check current vehicle count and spawn more if below quota
     */
    async checkAndMaintainVehicleQuota() {
        try {
            // Get traffic pattern for current hour
            if (!window.trafficPatternManager) {
                return;
            }

            const pattern = window.trafficPatternManager.getPatternForTime(this.currentHour);
            const [minVehicles, maxVehicles] = pattern.vehicleRange;

            // Get current vehicle count from network state
            const currentCount = (window.networkState && window.networkState.vehicles)
                ? window.networkState.vehicles.length
                : 0;

            // Target: maintain at least minimum for the time range
            const targetMin = minVehicles;

            // If below minimum, spawn vehicles to reach minimum
            if (currentCount < targetMin) {
                const neededVehicles = targetMin - currentCount;

                console.log(`🚗 Vehicle quota check: ${currentCount}/${targetMin} (spawning ${neededVehicles})`);

                await this.spawnAdditionalVehicles(neededVehicles, pattern.evPercentage);
            }
        } catch (error) {
            console.error('Error checking vehicle quota:', error);
        }
    }

    /**
     * Spawn additional vehicles to maintain quota
     */
    async spawnAdditionalVehicles(count, evPercentage) {
        try {
            const response = await fetch('/api/sumo/spawn', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    count: count,
                    ev_percentage: evPercentage,
                    battery_min_soc: 0.2,
                    battery_max_soc: 0.9
                })
            });

            const data = await response.json();

            if (data.success) {
                const actualSpawned = data.spawned || count;
                console.log(`✅ Spawned ${actualSpawned} additional vehicles (${count} requested, total: ${data.total_vehicles})`);

                // Update EV charging load
                await fetch('/api/scenario/add_vehicles', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({count: actualSpawned})
                });

                // Reload network state
                await new Promise(resolve => setTimeout(resolve, 300));
                if (window.loadNetworkState) {
                    await window.loadNetworkState();
                }
            }
        } catch (error) {
            console.error('Error spawning additional vehicles:', error);
        }
    }

    /**
     * Set time and start progression
     */
    async setTimeAndStart(hour, minute = 0) {
        // Update backend
        await fetch('/api/scenario/set_time', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({hour: hour})
        });

        // Start progression from this time
        this.startTimeProgression(hour, minute);

        // Initial vehicle spawn for this time
        if (window.trafficPatternManager) {
            const spawnResult = await window.trafficPatternManager.spawnVehiclesForTime(hour);
            console.log(`🚗 Initial spawn for time ${hour}: ${spawnResult.vehicleCount} vehicles`);
        }
    }

    /**
     * Pause time progression (keeps quota monitoring active)
     */
    pauseTime() {
        this.timeEnabled = false;
        console.log('⏸️ Time progression paused');
    }

    /**
     * Resume time progression
     */
    resumeTime() {
        this.timeEnabled = true;
        console.log('▶️ Time progression resumed');
    }

    /**
     * Set time speed (ms per simulation minute)
     */
    setTimeSpeed(ms) {
        this.timeSpeed = ms;

        // Restart interval with new speed if running
        if (this.timeInterval) {
            const wasEnabled = this.timeEnabled;
            this.stopTimeProgression();
            if (wasEnabled) {
                this.startTimeProgression(this.currentHour, this.currentMinute);
            }
        }

        console.log(`⏱️ Time speed set to ${ms}ms per simulation minute`);
    }

    /**
     * Get current time info
     */
    getCurrentTime() {
        return {
            hour: this.currentHour,
            minute: this.currentMinute,
            formatted: `${String(this.currentHour).padStart(2, '0')}:${String(this.currentMinute).padStart(2, '0')}`,
            enabled: this.timeEnabled
        };
    }
}

// Create global instance
window.timeVehicleManager = new TimeVehicleManager();

console.log('✅ Time & Vehicle Management System loaded');
