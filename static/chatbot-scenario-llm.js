/**
 * WORLD-CLASS LLM-BASED SCENARIO COMMAND HANDLER
 * Natural language processing for comprehensive scenario control
 *
 * Features:
 * - Natural language time/temperature control
 * - Intelligent test scenario suggestions
 * - Conflict detection (blackout/V2G)
 * - Map overlay integration
 * - Complete error handling
 */

class LLMScenarioCommandHandler {
    constructor() {
        this.currentScenario = null;
        this.activeScenarios = new Set(); // Track active scenarios
        this.currentTime = 12;
        this.currentTemperature = 72;
        this.lastSuggestionContext = null;

        // Scenario patterns for natural language understanding
        this.patterns = {
            time: [
                /set\s+time\s+(?:of\s+day\s+)?(?:for\s+|to\s+)?(\d+)/i,
                /time\s+(?:is\s+|=\s+)?(\d+)/i,
                /change\s+time\s+to\s+(\d+)/i,
                /(\d+)\s+(?:o'clock|hours?|am|pm)/i
            ],
            temperature: [
                /set\s+temp(?:erature)?\s+(?:for\s+|to\s+)?(\d+)/i,
                /temp(?:erature)?\s+(?:is\s+|=\s+)?(\d+)/i,
                /change\s+temp(?:erature)?\s+to\s+(\d+)/i,
                /make\s+it\s+(\d+)\s+degrees/i
            ],
            scenarios: {
                'morning_rush': ['morning rush', 'morning commute', 'am rush', '8 am scenario'],
                'evening_rush': ['evening rush', 'evening commute', 'pm rush', '6 pm scenario'],
                'normal_day': ['normal day', 'regular day', 'typical day', 'midday'],
                'heatwave_crisis': ['heatwave crisis', 'heatwave', 'heat crisis', 'extreme heat', '98 degrees'],
                'catastrophic_heat': ['catastrophic heat', 'critical heat', 'extreme emergency', '115 degrees'],
                'late_night': ['late night', 'night time', '3 am', 'overnight']
            }
        };

        // Test scenario definitions
        this.testScenarios = {
            'morning_rush': {
                time: 8,
                temp: 75,
                description: 'Morning Rush Hour (8:00 AM, 75°F) - PEAK TRAFFIC',
                icon: '🌅',
                difficulty: 'medium',
                vehicles: 95  // PEAK RUSH - Heavy commuter traffic
            },
            'evening_rush': {
                time: 18,
                temp: 80,
                description: 'Evening Rush Hour (6:00 PM, 80°F) - HEAVIEST TRAFFIC',
                icon: '🌆',
                difficulty: 'hard',
                vehicles: 98  // HIGHEST TRAFFIC - Commute + errands + deliveries
            },
            'normal_day': {
                time: 12,
                temp: 72,
                description: 'Normal Day (12:00 PM, 72°F) - MODERATE TRAFFIC',
                icon: '☀️',
                difficulty: 'easy',
                vehicles: 65  // MODERATE - Lunch traffic, less than rush hour
            },
            'heatwave_crisis': {
                time: 15,
                temp: 98,
                description: 'Heatwave Crisis (3:00 PM, 98°F) - HIGH TRAFFIC',
                icon: '🔥',
                difficulty: 'extreme',
                vehicles: 85  // HIGH - Afternoon activity in extreme heat
            },
            'catastrophic_heat': {
                time: 14,
                temp: 115,
                description: 'Catastrophic Heat (2:00 PM, 115°F) - REDUCED TRAFFIC',
                icon: '☢️',
                difficulty: 'catastrophic',
                vehicles: 75  // REDUCED - Many avoid travel in catastrophic heat
            },
            'late_night': {
                time: 3,
                temp: 65,
                description: 'Late Night (3:00 AM, 65°F) - MINIMAL TRAFFIC',
                icon: '🌙',
                difficulty: 'easy',
                vehicles: 15  // MINIMAL - Only essential/night shift traffic
            }
        };

        console.log('✅ LLM Scenario Command Handler initialized');
    }

    /**
     * Main command processor - handles all natural language commands
     */
    async processCommand(message) {
        try {
            message = message.toLowerCase().trim();

            // Check for time commands
            const timeMatch = this.extractTime(message);
            if (timeMatch !== null) {
                return await this.handleTimeCommand(timeMatch);
            }

            // Check for temperature commands
            const tempMatch = this.extractTemperature(message);
            if (tempMatch !== null) {
                return await this.handleTemperatureCommand(tempMatch);
            }

            // Check for test scenario commands
            const scenarioMatch = this.extractScenario(message);
            if (scenarioMatch) {
                return await this.handleScenarioCommand(scenarioMatch);
            }

            // Check for status request
            if (message.includes('status') || message.includes('current') || message.includes('what')) {
                return await this.handleStatusRequest();
            }

            // Check for suggestions request
            if (message.includes('suggest') || message.includes('recommend') || message.includes('what should')) {
                return await this.provideSuggestions();
            }

            return null; // No scenario command detected

        } catch (error) {
            console.error('Command processing error:', error);
            return {
                success: false,
                message: `Error processing command: ${error.message}`
            };
        }
    }

    /**
     * Extract time from message
     */
    extractTime(message) {
        for (const pattern of this.patterns.time) {
            const match = message.match(pattern);
            if (match) {
                let hour = parseInt(match[1]);
                // Handle PM/AM
                if (message.includes('pm') && hour < 12) hour += 12;
                if (message.includes('am') && hour === 12) hour = 0;
                // Clamp to 0-23
                return Math.max(0, Math.min(23, hour));
            }
        }
        return null;
    }

    /**
     * Extract temperature from message
     */
    extractTemperature(message) {
        for (const pattern of this.patterns.temperature) {
            const match = message.match(pattern);
            if (match) {
                const temp = parseInt(match[1]);
                // Clamp to reasonable range
                return Math.max(10, Math.min(120, temp));
            }
        }
        return null;
    }

    /**
     * Extract scenario from message
     */
    extractScenario(message) {
        for (const [scenarioKey, patterns] of Object.entries(this.patterns.scenarios)) {
            for (const pattern of patterns) {
                if (message.includes(pattern)) {
                    return scenarioKey;
                }
            }
        }
        return null;
    }

    /**
     * Handle time setting command
     */
    async handleTimeCommand(hour) {
        try {
            // Check for conflicts
            if (this.hasActiveScenarioConflict()) {
                return {
                    success: false,
                    message: `⚠️ Cannot change time: Active scenario in progress (${Array.from(this.activeScenarios).join(', ')}). Please wait for scenario completion or cancel it first.`,
                    conflict: true
                };
            }

            // Set time via API
            const response = await fetch('/api/scenario/set_time', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({hour: hour})
            });

            const data = await response.json();

            if (data.success) {
                this.currentTime = hour;
                this.updateMapOverlay();

                // Update status bar time display
                if (window.updateTime) {
                    window.updateTime();
                }

                // **START PROGRESSIVE TIME SYSTEM**
                if (window.timeVehicleManager) {
                    await window.timeVehicleManager.setTimeAndStart(hour, 0);
                }

                // **AUTOMATIC VEHICLE SPAWNING BASED ON TIME PATTERN**
                let vehicleInfo = null;
                if (window.trafficPatternManager) {
                    const trafficDesc = window.trafficPatternManager.getTrafficDescription(hour);
                    const spawnResult = await window.trafficPatternManager.spawnVehiclesForTime(hour);

                    if (spawnResult.success) {
                        vehicleInfo = {
                            count: spawnResult.vehicleCount,  // Actual spawned count
                            requested: spawnResult.requestedCount,  // Requested count
                            icon: trafficDesc.icon,
                            description: trafficDesc.description
                        };
                    }
                }

                // Sync with scenario control panel sliders
                if (window.scenarioControls) {
                    window.scenarioControls.currentTime = hour;
                    const timeSlider = document.getElementById('time-slider');
                    if (timeSlider) {
                        timeSlider.value = hour;
                    }
                    if (window.scenarioControls.updateTimeDisplay) {
                        window.scenarioControls.updateTimeDisplay(hour);
                    }
                }

                // Get suggestions
                const suggestions = this.getSuggestionsForContext();

                let message = `✅ Time set to ${String(hour).padStart(2, '0')}:00 (${this.getTimeDescription(hour)})`;

                if (vehicleInfo) {
                    // Show actual spawned count, with note if different from requested
                    if (vehicleInfo.requested && vehicleInfo.count !== vehicleInfo.requested) {
                        message += `\n🚗 Traffic: ${vehicleInfo.count} vehicles spawned (${vehicleInfo.requested} requested)\n${vehicleInfo.icon} ${vehicleInfo.description}`;
                        message += `\n⚠️ Note: ${vehicleInfo.requested - vehicleInfo.count} vehicles couldn't find suitable road edges`;
                    } else {
                        message += `\n🚗 Traffic: ${vehicleInfo.count} vehicles\n${vehicleInfo.icon} ${vehicleInfo.description}`;
                    }
                }

                return {
                    success: true,
                    message: message,
                    time: hour,
                    vehicleCount: vehicleInfo ? vehicleInfo.count : null,
                    suggestions: suggestions
                };
            } else {
                return {
                    success: false,
                    message: `❌ Failed to set time: ${data.error || 'Unknown error'}`
                };
            }

        } catch (error) {
            console.error('Time command error:', error);
            return {
                success: false,
                message: `❌ Error setting time: ${error.message}`
            };
        }
    }

    /**
     * Handle temperature setting command
     */
    async handleTemperatureCommand(temp) {
        try {
            // Check for conflicts
            if (this.hasActiveScenarioConflict()) {
                return {
                    success: false,
                    message: `⚠️ Cannot change temperature: Active scenario in progress (${Array.from(this.activeScenarios).join(', ')}). Please wait for scenario completion or cancel it first.`,
                    conflict: true
                };
            }

            // Set temperature via API
            const response = await fetch('/api/scenario/set_temperature', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({temperature: temp})
            });

            const data = await response.json();

            if (data.success) {
                this.currentTemperature = temp;
                this.updateMapOverlay();

                // Update status bar temperature
                const statusTemp = document.getElementById('temperature');
                if (statusTemp) {
                    statusTemp.textContent = temp;
                }

                // Sync with scenario control panel sliders
                if (window.scenarioControls) {
                    window.scenarioControls.currentTemp = temp;
                    const tempSlider = document.getElementById('temp-slider');
                    if (tempSlider) {
                        tempSlider.value = temp;
                    }
                    const tempDisplay = document.getElementById('temp-display');
                    if (tempDisplay) {
                        tempDisplay.textContent = `${temp}°F`;
                    }
                    const weatherDisplay = document.getElementById('weather-display');
                    if (weatherDisplay) {
                        weatherDisplay.textContent = window.scenarioControls.getWeatherDescription(temp);
                    }
                }

                // Get suggestions
                const suggestions = this.getSuggestionsForContext();

                return {
                    success: true,
                    message: `✅ Temperature set to ${temp}°F (${this.getWeatherDescription(temp)})`,
                    temperature: temp,
                    suggestions: suggestions
                };
            } else {
                return {
                    success: false,
                    message: `❌ Failed to set temperature: ${data.error || 'Unknown error'}`
                };
            }

        } catch (error) {
            console.error('Temperature command error:', error);
            return {
                success: false,
                message: `❌ Error setting temperature: ${error.message}`
            };
        }
    }

    /**
     * Handle test scenario command
     */
    async handleScenarioCommand(scenarioKey) {
        try {
            // Check for conflicts
            if (this.hasActiveScenarioConflict()) {
                return {
                    success: false,
                    message: `⚠️ Cannot start scenario: Active scenario in progress (${Array.from(this.activeScenarios).join(', ')}). Please wait for completion or cancel it first.`,
                    conflict: true
                };
            }

            const scenario = this.testScenarios[scenarioKey];
            if (!scenario) {
                return {
                    success: false,
                    message: `❌ Unknown scenario: ${scenarioKey}`
                };
            }

            // Mark scenario as active
            this.activeScenarios.add(scenarioKey);

            // **USE SCENARIO CONTROLS WORKFLOW IF AVAILABLE**
            if (window.scenarioControls) {
                // Use the full scenario workflow from scenario-controls.js
                await window.scenarioControls.runScenario(scenarioKey);

                // Update our internal state to match
                this.currentTime = scenario.time;
                this.currentTemperature = scenario.temp;
                this.updateMapOverlay();

                if (window.updateTime) {
                    window.updateTime();
                }
            } else {
                // Fallback: manual execution
                await this.setTimeQuiet(scenario.time);
                await this.setTemperatureQuiet(scenario.temp);
                await this.spawnVehiclesForScenario(scenario.vehicles);
            }

            // Remove from active after completion
            setTimeout(() => {
                this.activeScenarios.delete(scenarioKey);
            }, 5000); // Scenarios complete after 5 seconds

            return {
                success: true,
                message: `${scenario.icon} **${scenario.description}** scenario started!\n\n` +
                         `⏰ Time: ${scenario.time}:00\n` +
                         `🌡️ Temperature: ${scenario.temp}°F\n` +
                         `🚗 Vehicles: ${scenario.vehicles}\n` +
                         `📊 Difficulty: ${scenario.difficulty.toUpperCase()}`,
                scenario: scenario
            };

        } catch (error) {
            this.activeScenarios.delete(scenarioKey);
            console.error('Scenario command error:', error);
            return {
                success: false,
                message: `❌ Error starting scenario: ${error.message}`
            };
        }
    }

    /**
     * Set time quietly (without suggestions)
     */
    async setTimeQuiet(hour) {
        await fetch('/api/scenario/set_time', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({hour: hour})
        });
        this.currentTime = hour;
        this.updateMapOverlay();

        // Update status bar time display
        if (window.updateTime) {
            window.updateTime();
        }
    }

    /**
     * Set temperature quietly (without suggestions)
     */
    async setTemperatureQuiet(temp) {
        await fetch('/api/scenario/set_temperature', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({temperature: temp})
        });
        this.currentTemperature = temp;
        this.updateMapOverlay();
    }

    /**
     * Spawn vehicles for scenario
     */
    async spawnVehiclesForScenario(count) {
        try {
            // Stop existing simulation
            await fetch('/api/sumo/stop', {method: 'POST'});
            await new Promise(resolve => setTimeout(resolve, 500));

            // Start with specified vehicle count
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
                // Update EV charging load
                await fetch('/api/scenario/add_vehicles', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({count: count})
                });
            }

        } catch (error) {
            console.error('Vehicle spawn error:', error);
        }
    }

    /**
     * Handle status request
     */
    async handleStatusRequest() {
        try {
            const response = await fetch('/api/scenario/status');
            const data = await response.json();

            if (data.success) {
                const substationCount = Object.keys(data.substations || {}).length;
                const operationalCount = Object.values(data.substations || {})
                    .filter(s => s.operational).length;

                let message = `📊 **Current Scenario Status**\n\n`;
                message += `⏰ Time: ${String(this.currentTime).padStart(2, '0')}:00 (${this.getTimeDescription(this.currentTime)})\n`;
                message += `🌡️ Temperature: ${this.currentTemperature}°F (${this.getWeatherDescription(this.currentTemperature)})\n`;
                message += `🏭 Substations: ${operationalCount}/${substationCount} operational\n`;

                if (this.activeScenarios.size > 0) {
                    message += `\n🎯 Active Scenarios: ${Array.from(this.activeScenarios).join(', ')}`;
                } else {
                    message += `\n✅ No active scenarios - Ready for commands`;
                }

                return {
                    success: true,
                    message: message,
                    status: data
                };
            }

        } catch (error) {
            console.error('Status request error:', error);
            return {
                success: false,
                message: `❌ Error fetching status: ${error.message}`
            };
        }
    }

    /**
     * Provide intelligent suggestions
     */
    async provideSuggestions() {
        const suggestions = this.getSuggestionsForContext();

        let message = `💡 **Scenario Suggestions**\n\n`;
        message += `Based on current conditions (${this.getTimeDescription(this.currentTime)}, ${this.currentTemperature}°F):\n\n`;

        suggestions.forEach((suggestion, index) => {
            const scenario = this.testScenarios[suggestion.key];
            message += `${index + 1}. ${scenario.icon} **${scenario.description}**\n`;
            message += `   Reason: ${suggestion.reason}\n\n`;
        });

        message += `Say any scenario name to start it!`;

        return {
            success: true,
            message: message,
            suggestions: suggestions
        };
    }

    /**
     * Get intelligent suggestions based on current context
     */
    getSuggestionsForContext() {
        const suggestions = [];

        // ALWAYS suggest all scenarios, prioritized by relevance

        // 1. Time-based primary suggestion
        if (this.currentTime >= 7 && this.currentTime <= 9) {
            suggestions.push({
                key: 'morning_rush',
                reason: 'Current time matches morning rush hour',
                priority: 1
            });
        } else if (this.currentTime >= 17 && this.currentTime <= 19) {
            suggestions.push({
                key: 'evening_rush',
                reason: 'Current time matches evening rush hour',
                priority: 1
            });
        } else if (this.currentTime >= 0 && this.currentTime <= 4) {
            suggestions.push({
                key: 'late_night',
                reason: 'Late night conditions',
                priority: 1
            });
        } else {
            suggestions.push({
                key: 'normal_day',
                reason: 'Regular daytime operations',
                priority: 1
            });
        }

        // 2. Temperature-based suggestions
        if (this.currentTemperature >= 110) {
            suggestions.push({
                key: 'catastrophic_heat',
                reason: 'Extreme heat conditions - test grid limits',
                priority: 2
            });
        } else if (this.currentTemperature >= 95) {
            suggestions.push({
                key: 'heatwave_crisis',
                reason: 'High temperature stress test',
                priority: 2
            });
        }

        // 3. Always add all other scenarios as additional options
        const allScenarios = ['morning_rush', 'evening_rush', 'normal_day', 'heatwave_crisis', 'catastrophic_heat', 'late_night'];

        allScenarios.forEach(key => {
            // Only add if not already in suggestions
            if (!suggestions.find(s => s.key === key)) {
                suggestions.push({
                    key: key,
                    reason: this.testScenarios[key].description,
                    priority: 3
                });
            }
        });

        // Sort by priority, then return all (no limit)
        return suggestions.sort((a, b) => a.priority - b.priority);
    }

    /**
     * Check for active scenario conflicts
     */
    hasActiveScenarioConflict() {
        // Check for blackout or V2G scenarios
        if (window.scenarioDirector) {
            const state = window.scenarioDirector.scenarioState;
            if (state === 'running' || state === 'preparing') {
                this.activeScenarios.add(window.scenarioDirector.currentScenario || 'unknown');
                return true;
            }
        }

        return false;
    }

    /**
     * Update map overlay with current time and temperature
     * DISABLED: User requested removal of scenario status box
     */
    updateMapOverlay() {
        // Remove existing overlay if it exists
        const overlay = document.getElementById('scenario-map-overlay');
        if (overlay) {
            overlay.remove();
        }
        // Do not create or update the overlay - feature disabled
    }

    /**
     * Get time description
     */
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

    /**
     * Get weather description
     */
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
}

// Create global instance
window.llmScenarioHandler = new LLMScenarioCommandHandler();

// Initialize map overlay on load
document.addEventListener('DOMContentLoaded', () => {
    if (window.llmScenarioHandler) {
        window.llmScenarioHandler.updateMapOverlay();

        // Initialize status bar time to scenario time
        setTimeout(() => {
            if (window.updateTime) {
                window.updateTime();
            }
        }, 500);
    }
});

console.log('✅ LLM Scenario Command Handler loaded');
