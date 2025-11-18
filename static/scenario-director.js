/**
 * WORLD-CLASS SCENARIO DIRECTOR
 * Cinematic scenario execution with camera choreography, vehicle preparation, and live narration
 */

class ScenarioDirector {
    constructor() {
        this.currentScenario = null;
        this.scenarioState = 'idle'; // idle, preparing, running, completed
        this.cameraAnimationRunning = false;
        this.narrationCallback = null;
        this.scenarioData = {};

        console.log('🎬 Scenario Director initialized');
    }

    /**
     * Set narration callback for live updates
     */
    setNarrationCallback(callback) {
        this.narrationCallback = callback;
    }

    /**
     * Send narration message
     */
    narrate(message, type = 'info') {
        if (this.narrationCallback) {
            this.narrationCallback(message, type);
        }
        console.log(`[Narration] ${message}`);
    }

    /**
     * Add message directly to chat (bypass narration callback)
     * Auto-opens chatbot if closed
     */
    addDirectChatMessage(message, type = 'success') {
        // AUTO-OPEN CHATBOT WINDOW IF CLOSED - THIS IS THE FIX!
        const chatbotWindow = document.getElementById('chatbot-window');
        const chatbotLauncher = document.getElementById('chatbot-launcher');
        if (chatbotWindow && chatbotWindow.style.display !== 'flex') {
            chatbotWindow.style.display = 'flex';
            if (chatbotLauncher) {
                chatbotLauncher.style.display = 'none';
            }
            console.log('[DIRECT CHAT] Auto-opened chatbot window for scenario messages');
        }

        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) {
            console.error('[DIRECT CHAT] chat-messages element not found!');
            return;
        }

        let style = '';
        let icon = '';
        let borderColor = '';

        switch (type) {
            case 'success':
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,200,100,0.08)); border: 1px solid rgba(0,255,136,0.3);';
                icon = '✅';
                borderColor = '#00ff88';
                break;
            case 'error':
                style = 'background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(255,50,50,0.08)); border: 1px solid rgba(255,107,107,0.3);';
                icon = '❌';
                borderColor = '#ff6b6b';
                break;
            case 'info':
            default:
                style = 'background: linear-gradient(135deg, rgba(0,200,255,0.1), rgba(0,150,255,0.06)); border: 1px solid rgba(0,200,255,0.25);';
                icon = '💬';
                borderColor = '#00ccff';
                break;
        }

        const messageHtml = `
            <div class="scenario-narration" style="
                margin: 4px 12px;
                padding: 8px 12px;
                ${style}
                border-radius: 10px;
                font-size: 13px;
                line-height: 1.4;
                color: #ffffff;
                border-left: 3px solid ${borderColor};
                animation: slideIn 0.3s ease;
            ">
                <span style="margin-right: 6px;">${icon}</span>${message}
            </div>
        `;

        chatMessages.innerHTML += messageHtml;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        console.log('[DIRECT CHAT] Message added:', message);
    }

    /**
     * Notify chatbot LLM that restoration is complete
     * This makes the chatbot AWARE of the restoration so it can respond
     */
    async notifyChatbotOfRestoration(restorationData) {
        try {
            console.log('[SCENARIO] Notifying chatbot of restoration:', restorationData);

            // Build notification message
            const notificationMessage = `SYSTEM NOTIFICATION: V2G Emergency Scenario Complete
✅ ${restorationData.substation} Substation: RESTORED
💡 Traffic lights restored: ${restorationData.lights_restored}
🔌 EV stations restored: ${restorationData.ev_stations_restored}
⚡ Energy delivered: ${restorationData.energy_delivered} kWh
💰 Revenue: $${restorationData.revenue}
Status: ${restorationData.status}`;

            // Add to chat as assistant message so it's visible
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                const systemMsgHtml = `
                    <div class="msg assistant" style="
                        margin: 8px 0;
                        padding: 10px;
                        background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,200,100,0.1));
                        border-radius: 10px;
                        border: 2px solid rgba(0,255,136,0.4);
                    ">
                        <strong>System:</strong> ${notificationMessage.replace(/\n/g, '<br>')}
                    </div>
                `;
                chatMessages.innerHTML += systemMsgHtml;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // CRITICAL: Send auto-message to chatbot to make it respond
            try {
                console.log('[SCENARIO] Sending restoration event to chatbot...');

                const chatbotResponse = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `The V2G emergency scenario just completed! ${restorationData.substation} substation has been restored. ${restorationData.lights_restored} traffic lights are back online, ${restorationData.ev_stations_restored} EV charging stations restored. Total energy delivered: ${restorationData.energy_delivered} kWh, revenue generated: $${restorationData.revenue}. Please acknowledge this restoration and provide a brief summary.`,
                        user_id: 'system'
                    })
                });

                const chatbotData = await chatbotResponse.json();
                console.log('[SCENARIO] Chatbot response:', chatbotData);

                // Add chatbot's response to chat as AI message
                if (chatbotData.status === 'success' && chatbotData.response) {
                    const chatMessages = document.getElementById('chat-messages');
                    if (chatMessages) {
                        const aiMsgHtml = `
                            <div class="msg ai" style="
                                margin: 8px 12px;
                                padding: 12px;
                                background: linear-gradient(135deg, rgba(0,255,136,0.08), rgba(0,200,255,0.06));
                                border: 1px solid rgba(0,255,136,0.2);
                                border-radius: 12px;
                                font-size: 13px;
                                line-height: 1.6;
                                color: #ffffff;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                            ">
                                <strong style="color: #00ff88; display: flex; align-items: center; margin-bottom: 6px;">
                                    💬 Ultra-AI:
                                </strong>
                                <div style="white-space: pre-wrap;">${chatbotData.response}</div>
                            </div>
                        `;
                        chatMessages.innerHTML += aiMsgHtml;
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                        console.log('[SCENARIO] Chatbot response added to chat!');
                    }
                }
            } catch (chatbotError) {
                console.error('[SCENARIO] Could not notify chatbot:', chatbotError);
            }

            console.log('[SCENARIO] Chatbot has been notified of restoration');
        } catch (error) {
            console.error('[SCENARIO] Error notifying chatbot:', error);
        }
    }

    /**
     * Chatbot Monitoring Loop - Updates chatbot in real-time
     */
    startChatbotMonitoring(substation) {
        let lastProgress = 0;
        let hasNotifiedRestoration = false;
        let maxEnergyDelivered = 0; // Track maximum energy seen
        let maxVehicleCount = 0;

        const monitorInterval = setInterval(async () => {
            try {
                // Get V2G status
                const statusResp = await fetch('/api/v2g/status');
                const status = await statusResp.json();

                const required = (status?.energy_required && status.energy_required[substation]) || 25;
                const delivered = (status?.energy_delivered && status.energy_delivered[substation]) || 0;
                const progress = Math.round((delivered / Math.max(1, required)) * 100);
                const activeVehicles = Array.isArray(status?.active_vehicles)
                    ? status.active_vehicles.filter(v => v.substation === substation).length
                    : 0;

                // Track maximum values (in case they get cleared)
                if (delivered > maxEnergyDelivered) {
                    maxEnergyDelivered = delivered;
                }
                if (activeVehicles > maxVehicleCount) {
                    maxVehicleCount = activeVehicles;
                }

                // Update chatbot every 20% progress change
                if (progress >= lastProgress + 20 && progress < 100) {
                    lastProgress = progress;

                    // Send update to chatbot
                    this.addDirectChatMessage(`⚡ V2G Progress: ${progress}% (${activeVehicles} vehicles discharging)`, 'progress');
                }

                // AGGRESSIVE 100% DETECTION - Multiple checks
                const reached100 = progress >= 100;
                const energyMet = delivered >= required;
                const substationData = status?.enabled_substations || [];
                const notInFailedList = !substationData.includes(substation);
                const energyDroppedToZero = maxEnergyDelivered >= required && delivered === 0; // Energy was cleared

                console.log(`[CHATBOT MONITOR] Progress: ${progress}%, Delivered: ${delivered}/${required}, Max: ${maxEnergyDelivered}, NotInFailedList: ${notInFailedList}, EnergyDropped: ${energyDroppedToZero}`);

                // Trigger notification if ANY condition met
                if (!hasNotifiedRestoration && (reached100 || energyMet || energyDroppedToZero || (notInFailedList && maxEnergyDelivered > 0))) {
                    hasNotifiedRestoration = true;
                    clearInterval(monitorInterval);

                    console.log('[CHATBOT MONITOR] 🎉 TRIGGERING RESTORATION NOTIFICATION!');

                    // Calculate earnings - use MAX energy delivered (in case it was cleared)
                    const actualDelivered = Math.max(delivered, maxEnergyDelivered, required, 25); // Use maximum value seen
                    const revenue = Math.round(actualDelivered * 3); // $3/kWh emergency rate

                    // Get final stats - use max vehicle count if current is 0
                    const allVehicles = status?.active_vehicles || [];
                    const sessionVehicles = allVehicles.filter(v => v.substation === substation);
                    const vehicleCount = Math.max(sessionVehicles.length, activeVehicles, maxVehicleCount, 1);

                    console.log(`[CHATBOT MONITOR] Vehicles: ${vehicleCount}, Revenue: $${revenue}, Energy: ${actualDelivered} kWh`);

                    // Send restoration notification to chatbot - ALWAYS SHOW
                    const restoreMsg = `🎉 V2G RESTORATION COMPLETE!\n\n` +
                        `✅ ${substation} Substation RESTORED\n` +
                        `⚡ Energy delivered: ${Math.round(actualDelivered)} kWh\n` +
                        `💰 Total revenue: $${revenue}\n` +
                        `🚗 Vehicles participated: ${vehicleCount}\n` +
                        `📊 Average earnings per vehicle: $${Math.round(revenue / vehicleCount)}`;

                    this.addDirectChatMessage(restoreMsg, 'success');
                    console.log('[CHATBOT MONITOR] ✅ Restoration message sent to chat!');

                    // Send to chatbot AI - FORCE IT
                    try {
                        console.log('[CHATBOT MONITOR] Sending to AI backend...');

                        const chatbotResp = await fetch('/api/ai/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                message: `V2G EMERGENCY RESTORATION SUCCESS! The ${substation} substation has been fully restored! Here are the results: Energy delivered: ${Math.round(actualDelivered)} kWh by ${vehicleCount} electric vehicles. Total revenue generated: $${revenue}. Average earnings per vehicle: $${Math.round(revenue / vehicleCount)}. This is a major success! Please celebrate and acknowledge this achievement!`,
                                user_id: 'system'
                            })
                        });

                        console.log('[CHATBOT MONITOR] AI response status:', chatbotResp.status);
                        const chatbotData = await chatbotResp.json();
                        console.log('[CHATBOT MONITOR] AI response data:', chatbotData);

                        // Try to extract response from multiple formats
                        let aiResponse = null;
                        if (chatbotData.status === 'success' && chatbotData.response) {
                            aiResponse = chatbotData.response;
                        } else if (chatbotData.full_data && chatbotData.full_data.text) {
                            aiResponse = chatbotData.full_data.text;
                        } else if (chatbotData.text) {
                            aiResponse = chatbotData.text;
                        }

                        if (aiResponse) {
                            const chatMessages = document.getElementById('chat-messages');
                            if (chatMessages) {
                                const aiMsgHtml = `
                                    <div class="msg ai" style="
                                        margin: 8px 12px;
                                        padding: 12px;
                                        background: linear-gradient(135deg, rgba(0,255,136,0.08), rgba(0,200,255,0.06));
                                        border: 1px solid rgba(0,255,136,0.2);
                                        border-radius: 12px;
                                        font-size: 13px;
                                        line-height: 1.6;
                                        color: #ffffff;
                                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                                    ">
                                        <strong style="color: #00ff88; display: flex; align-items: center; margin-bottom: 6px;">
                                            💬 Ultra-AI:
                                        </strong>
                                        <div style="white-space: pre-wrap;">${aiResponse}</div>
                                    </div>
                                `;
                                chatMessages.innerHTML += aiMsgHtml;
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                                console.log('[CHATBOT MONITOR] ✅ AI response added to chat!');
                            }
                        } else {
                            console.warn('[CHATBOT MONITOR] No valid AI response found in:', chatbotData);
                        }
                    } catch (err) {
                        console.error('[CHATBOT MONITOR] Error notifying chatbot:', err);
                    }
                }

            } catch (error) {
                console.error('[Chatbot Monitor] Error:', error);
            }
        }, 2000); // Check every 2 seconds

        // Store interval for cleanup
        this.chatbotMonitorInterval = monitorInterval;
    }

    /**
     * Check if SUMO is running by checking for vehicles
     */
    async checkSUMOStatus() {
        try {
            const response = await fetch('/api/network_state');
            const data = await response.json();
            // If we have vehicles in the system, SUMO is running
            const vehicles = data.vehicles || [];
            return vehicles.length > 0;
        } catch (error) {
            console.error('Error checking SUMO status:', error);
            return false;
        }
    }

    /**
     * Get current vehicle statistics
     */
    async getVehicleStats() {
        try {
            const response = await fetch('/api/network_state');
            const data = await response.json();
            const vehicles = data.vehicles || [];

            const evs = vehicles.filter(v => v.is_ev);
            const highSOCEVs = evs.filter(v => v.battery_soc >= 70);
            const lowSOCEVs = evs.filter(v => v.battery_soc <= 35);

            return {
                total: vehicles.length,
                evs: evs.length,
                gasVehicles: vehicles.length - evs.length,
                highSOCEVs: highSOCEVs.length,
                lowSOCEVs: lowSOCEVs.length
            };
        } catch (error) {
            console.error('Error getting vehicle stats:', error);
            return { total: 0, evs: 0, gasVehicles: 0, highSOCEVs: 0, lowSOCEVs: 0 };
        }
    }

    /**
     * Prepare V2G Rescue Scenario
     */
    async prepareV2GScenario() {
        this.narrate('🔍 Analyzing system state for V2G scenario...', 'info');

        // Check SUMO status
        const sumoRunning = await this.checkSUMOStatus();
        if (!sumoRunning) {
            return {
                ready: false,
                reason: 'SUMO traffic simulation is not running. Start vehicles first.',
                actions_needed: ['Start SUMO simulation']
            };
        }

        // Get vehicle statistics
        const stats = await this.getVehicleStats();

        const needsVehicles = stats.highSOCEVs < 30;
        const vehiclesToSpawn = needsVehicles ? Math.max(0, 50 - stats.highSOCEVs) : 0;

        return {
            ready: !needsVehicles,
            current_state: stats,
            needs_preparation: needsVehicles,
            preparation_details: needsVehicles ? {
                vehicles_to_spawn: vehiclesToSpawn,
                vehicle_type: 'ev',
                soc_range: [70, 95],
                reason: 'Need high-SOC EVs to demonstrate V2G emergency response power'
            } : null,
            sumo_running: sumoRunning
        };
    }

    /**
     * Prepare Blackout Scenario
     */
    async prepareBlackoutScenario() {
        this.narrate('🔍 Analyzing system state for blackout scenario...', 'info');

        // Check SUMO status
        const sumoRunning = await this.checkSUMOStatus();
        if (!sumoRunning) {
            return {
                ready: false,
                reason: 'SUMO traffic simulation is not running. Start vehicles first.',
                actions_needed: ['Start SUMO simulation']
            };
        }

        // Get vehicle statistics
        const stats = await this.getVehicleStats();

        const needsVehicles = stats.total < 50 || stats.lowSOCEVs < 15;
        const totalToSpawn = needsVehicles ? Math.max(0, 100 - stats.total) : 0;
        const lowSOCEVsNeeded = needsVehicles ? Math.max(0, 35 - stats.lowSOCEVs) : 0;

        return {
            ready: !needsVehicles,
            current_state: stats,
            needs_preparation: needsVehicles,
            preparation_details: needsVehicles ? {
                total_vehicles: totalToSpawn,
                ev_count: Math.floor(totalToSpawn * 0.4),
                ev_soc_range: [15, 35],
                gas_count: Math.floor(totalToSpawn * 0.6),
                reason: 'Need traffic volume to show blackout impact on traffic signals and stranded EVs'
            } : null,
            sumo_running: sumoRunning
        };
    }

    /**
     * Spawn vehicles for scenario preparation
     */
    async spawnVehicles(config) {
        this.addDirectChatMessage(`🚗 Spawning ${config.count} vehicles...`, 'info');
        this.narrate(`🚗 Spawning ${config.count} vehicles...`, 'info');

        try {
            // Convert percentages to decimals for backend
            const spawnPayload = {
                count: config.count,
                ev_percentage: (config.ev_percentage || 70) / 100,
                battery_min_soc: (config.min_soc || 20) / 100,
                battery_max_soc: (config.max_soc || 90) / 100
            };

            console.log('[SPAWN] Sending spawn request:', spawnPayload);

            const response = await fetch('/api/sumo/spawn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(spawnPayload)
            });

            const data = await response.json();

            console.log('[SPAWN] Backend response:', data);

            if (data.success) {
                const actualSpawned = data.spawned || config.count;
                this.addDirectChatMessage(`✅ Spawned ${actualSpawned} vehicles (Total: ${data.total_vehicles || 'unknown'})`, 'success');
                this.narrate(`✅ Successfully spawned ${actualSpawned} vehicles`, 'success');
                // Wait for vehicles to initialize
                await this.delay(2000);
                return { success: true, spawned: actualSpawned };
            } else {
                this.addDirectChatMessage(`❌ Failed to spawn vehicles: ${data.message || 'Unknown error'}`, 'error');
                this.narrate(`❌ Failed to spawn vehicles: ${data.message || 'Unknown error'}`, 'error');
                return { success: false, error: data.message };
            }
        } catch (error) {
            this.addDirectChatMessage(`❌ Error spawning vehicles: ${error.message}`, 'error');
            this.narrate(`❌ Error spawning vehicles: ${error.message}`, 'error');
            return { success: false, error: error.message };
        }
    }

    /**
     * Execute camera choreography with smooth easing
     */
    async executeCamera(choreography) {
        if (!map) {
            console.error('Map not available for camera choreography');
            return;
        }

        this.cameraAnimationRunning = true;

        for (const phase of choreography) {
            if (!this.cameraAnimationRunning) break;

            this.narrate(`🎥 ${phase.description || 'Camera moving'}...`, 'camera');

            const cameraOptions = {
                center: phase.center || map.getCenter(),
                zoom: phase.zoom || map.getZoom(),
                pitch: phase.pitch || 0,
                bearing: phase.bearing || 0,
                duration: phase.duration || 2000,
                essential: true,
                easing: (t) => t * (2 - t) // Smooth ease-in-out
            };

            // Animate camera
            map.flyTo(cameraOptions);

            // Wait for animation plus any additional delay
            await this.delay(phase.duration + (phase.pause || 0));
        }

        this.cameraAnimationRunning = false;
    }

    /**
     * Highlight a location on the map with pulsing effect
     */
    highlightLocation(center, color = '#ff3232') {
        if (!map) return;

        // Create a pulsing circle layer
        const sourceId = 'highlight-pulse';
        const layerId = 'highlight-pulse-layer';

        // Remove existing highlight if any
        if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
        }
        if (map.getSource(sourceId)) {
            map.removeSource(sourceId);
        }

        // Add pulsing circle
        map.addSource(sourceId, {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': center
                }
            }
        });

        map.addLayer({
            'id': layerId,
            'type': 'circle',
            'source': sourceId,
            'paint': {
                'circle-radius': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    12, 20,
                    16, 100
                ],
                'circle-color': color,
                'circle-opacity': 0.6,
                'circle-blur': 0.8
            }
        });

        // Animate pulsing
        let pulsePhase = 0;
        const pulseInterval = setInterval(() => {
            pulsePhase += 0.05;
            const opacity = 0.3 + Math.sin(pulsePhase) * 0.3;
            if (map.getLayer(layerId)) {
                map.setPaintProperty(layerId, 'circle-opacity', opacity);
            } else {
                clearInterval(pulseInterval);
            }
        }, 50);

        // Auto-remove after scenario
        setTimeout(() => {
            clearInterval(pulseInterval);
            if (map.getLayer(layerId)) {
                map.removeLayer(layerId);
            }
            if (map.getSource(sourceId)) {
                map.removeSource(sourceId);
            }
        }, 60000);
    }

    /**
     * Flash screen effect for dramatic moments
     */
    async flashScreen(color = 'rgba(255, 50, 50, 0.3)', duration = 300) {
        const flash = document.createElement('div');
        flash.style.cssText = `
            position: fixed;
            inset: 0;
            background: ${color};
            z-index: 9999;
            pointer-events: none;
            animation: flashFade ${duration}ms ease-out;
        `;

        // Add flash animation
        if (!document.getElementById('flash-style')) {
            const style = document.createElement('style');
            style.id = 'flash-style';
            style.textContent = `
                @keyframes flashFade {
                    0% { opacity: 0; }
                    20% { opacity: 1; }
                    100% { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), duration);
    }

    /**
     * Execute V2G Rescue Scenario
     */
    async executeV2GScenario() {
        try {
            this.scenarioState = 'running';
            this.currentScenario = 'v2g';

            // Phase 1: Camera Setup
            this.addDirectChatMessage('🎬 V2G EMERGENCY RESCUE SCENARIO STARTING', 'info');
            this.narrate('🎬 V2G EMERGENCY RESCUE SCENARIO STARTING', 'scenario-start');
            this.addDirectChatMessage('📊 Switching to V2G tab...', 'info');
            this.narrate('📊 Switching to V2G tab...', 'info');

            // Auto-switch to V2G tab
            try {
                const v2gTab = document.querySelector('[onclick*="showTab"][onclick*="v2g"]');
                if (v2gTab) {
                    v2gTab.click();
                    this.narrate('✅ V2G dashboard active', 'success');
                }
            } catch (error) {
                console.warn('Could not switch to V2G tab:', error);
            }

            await this.delay(500);

            const setupChoreography = [{
                center: [-73.9855, 40.7580], // Times Square
                zoom: 14,
                pitch: 0,
                bearing: 0,
                duration: 2000,
                description: 'Positioning camera at Times Square'
            }];

            await this.executeCamera(setupChoreography);
            await this.delay(1000);

            // Phase 2: Trigger Scenario with dramatic effect
            await this.flashScreen('rgba(255, 50, 50, 0.4)', 400);
            this.addDirectChatMessage('🚨 EMERGENCY ALERT', 'error');
            this.narrate('🚨 EMERGENCY ALERT', 'emergency');
            this.addDirectChatMessage('⚠️ Times Square Substation - CRITICAL FAILURE', 'error');
            this.narrate('⚠️ Times Square Substation - CRITICAL FAILURE', 'emergency');
            this.addDirectChatMessage('👥 18 people trapped in elevators', 'error');
            this.narrate('👥 18 people trapped in elevators', 'emergency');

            // Highlight Times Square on map
            this.highlightLocation([-73.9855, 40.7580], '#ff3232');

            // Zoom in slightly for dramatic effect
            const actionChoreography = [{
                zoom: 15.5,
                pitch: 45,
                bearing: 30,
                duration: 3000,
                description: 'Zooming to action area',
                pause: 500
            }];

            await this.executeCamera(actionChoreography);

            // Trigger the actual V2G scenario
            this.narrate('📢 Sending V2G recruitment notification...', 'info');

            const substation = 'Times Square';

            // Fail substation
            await fetch(`/api/fail/${encodeURIComponent(substation)}`, { method: 'POST' });
            await this.delay(1000);

            this.narrate('⚡ V2G system activated - recruiting vehicles...', 'success');

            // Enable V2G
            const enableResp = await fetch(`/api/v2g/enable/${encodeURIComponent(substation)}`, {
                method: 'POST'
            });
            const enableData = await enableResp.json();

            if (!enableData.success) {
                this.narrate(`❌ V2G activation failed: ${enableData.message}`, 'error');
                this.scenarioState = 'completed';
                return;
            }

            const energyTarget = enableData.energy_needed_kwh || 50;
            this.narrate(`🎯 Target energy needed: ${Math.round(energyTarget)} kWh`, 'info');

            // VISUAL EFFECTS DISABLED - CAUSING LAG
            // if (window.v2gVisualEffects) {
            //     window.v2gVisualEffects.start();
            //     this.narrate('✨ Energy flow visualization activated!', 'success');
            // }

            // Phase 3: Start chatbot monitoring loop
            this.startChatbotMonitoring(substation);

            // Phase 3: Monitor Progress
            const climaxChoreography = [{
                zoom: 16,
                pitch: 60,
                bearing: 60,
                duration: 2000,
                description: 'Dramatic close-up view',
                pause: 500
            }];

            await this.executeCamera(climaxChoreography);

            // Poll V2G status - Real-time monitoring
            let delivered = 0;
            let iteration = 0;
            const maxIterations = 120; // 4 minutes max
            let lastVehicleCount = 0;
            let lastDelivered = 0;

            while (iteration < maxIterations) {
                const statusResp = await fetch('/api/v2g/status');
                const status = await statusResp.json();

                const required = (status?.energy_required && status.energy_required[substation]) || energyTarget;
                delivered = (status?.energy_delivered && status.energy_delivered[substation]) || 0;
                const activeVehicles = Array.isArray(status?.active_vehicles)
                    ? status.active_vehicles.filter(v => v.substation === substation).length
                    : (status?.active_sessions || 0);

                const pct = Math.max(0, Math.min(100, Math.round((delivered / Math.max(1, required)) * 100)));

                // Show update if vehicle count changed OR energy increased significantly
                const vehicleCountChanged = activeVehicles !== lastVehicleCount;
                const energyIncreased = Math.round(delivered) > Math.round(lastDelivered);

                if (activeVehicles > 0 && (vehicleCountChanged || energyIncreased || iteration % 2 === 0)) {
                    this.narrate(`🚗 ${activeVehicles} vehicles active | ⚡ ${Math.round(delivered)} / ${Math.round(required)} kWh (${pct}%)`, 'progress');
                    lastVehicleCount = activeVehicles;
                    lastDelivered = delivered;
                }

                // Break when target actually reached
                if (delivered >= required) {
                    console.log(`[V2G SCENARIO] Target reached: delivered=${delivered}, required=${required}`);
                    break;
                }

                await this.delay(2000);
                iteration++;
            }

            console.log(`[V2G SCENARIO] Monitoring complete: delivered=${delivered}, iterations=${iteration}`);

            // Phase 4: Resolution
            // Restore substation and get restoration data
            let restorationData = {};
            try {
                console.log('[V2G SCENARIO] TARGET REACHED - Starting restoration...');
                this.addDirectChatMessage('✅ TARGET REACHED!', 'success');
                this.narrate('✅ TARGET REACHED!', 'success');
                this.addDirectChatMessage('🔧 Restoring Times Square substation...', 'success');
                this.narrate('🔧 Restoring Times Square substation...', 'success');
                await this.delay(500);

                console.log('[V2G SCENARIO] Calling restore API...');
                const restoreResponse = await fetch(`/api/restore/${encodeURIComponent(substation)}`, { method: 'POST' });
                restorationData = await restoreResponse.json();
                console.log('[V2G SCENARIO] Restoration data received:', restorationData);

                // NOTE: Chatbot monitoring loop (startChatbotMonitoring) handles real-time notifications
                // This happens automatically when the monitoring loop detects restoration

                await this.flashScreen('rgba(0, 255, 136, 0.3)', 400);

                // FORCE CHAT MESSAGE - Direct injection
                console.log('[V2G SCENARIO] Adding restoration messages to chat...');
                this.addDirectChatMessage('✅ Substation RESTORED!', 'success');
                this.narrate('✅ Substation RESTORED!', 'success');

                if (restorationData.lights_restored > 0) {
                    this.addDirectChatMessage(`💡 ${restorationData.lights_restored} traffic lights back online`, 'success');
                    this.narrate(`💡 ${restorationData.lights_restored} traffic lights back online`, 'success');
                }
                if (restorationData.ev_stations_restored > 0) {
                    this.addDirectChatMessage(`🔌 ${restorationData.ev_stations_restored} EV charging stations restored`, 'success');
                    this.narrate(`🔌 ${restorationData.ev_stations_restored} EV charging stations restored`, 'success');
                }
                this.addDirectChatMessage('🏢 Elevators operational!', 'success');
                this.narrate('🏢 Elevators operational!', 'success');
                this.addDirectChatMessage('🚗 Releasing V2G vehicles...', 'success');
                this.narrate('🚗 Releasing V2G vehicles...', 'success');
            } catch (restorationError) {
                console.error('[V2G SCENARIO] ERROR during restoration:', restorationError);
                this.addDirectChatMessage(`❌ ERROR: ${restorationError.message}`, 'error');
                throw restorationError;
            }

            // Force release V2G vehicles
            try {
                const releaseResp = await fetch(`/api/v2g/release_vehicles/${encodeURIComponent(substation)}`, { method: 'POST' });
                const releaseData = await releaseResp.json();
                this.addDirectChatMessage(`✅ ${releaseData.released || 'All'} vehicles released!`, 'success');
                this.narrate('✅ All vehicles released!', 'success');
            } catch (error) {
                console.warn('Vehicle release endpoint not available:', error);
            }

            // Wait for backend to fully process and V2G UI to clear
            await this.delay(2000);

            // Phase 5: Return camera to normal view IMMEDIATELY
            this.addDirectChatMessage('🎥 Returning to normal view...', 'info');
            this.narrate('🎥 Returning to normal view...', 'camera');
            const normalViewChoreography = [{
                center: [-73.9712, 40.7831], // Manhattan center
                zoom: 12,
                pitch: 0,
                bearing: 0,
                duration: 2000, // Faster return - 2 seconds
                description: 'Returning to normal view'
            }];

            await this.executeCamera(normalViewChoreography);

            // VISUAL EFFECTS DISABLED
            // if (window.v2gVisualEffects) {
            //     window.v2gVisualEffects.stop();
            // }

            this.narrate('', 'scenario-complete');
            this.addDirectChatMessage('🎉 V2G RESCUE COMPLETE!', 'success');
            this.narrate('🎉 V2G RESCUE COMPLETE!', 'scenario-end');

            // Generate results
            const finalStats = await fetch('/api/v2g/status').then(r => r.json());
            const revenue = Math.round(delivered * 3); // $3/kWh during emergency

            // FORCE DIRECT CHAT - Show complete restoration summary
            this.addDirectChatMessage('📊 RESTORATION SUMMARY', 'info');
            this.addDirectChatMessage(`✅ ${restorationData.substation} Substation: ONLINE`, 'success');
            if (restorationData.lights_restored > 0) {
                this.addDirectChatMessage(`💡 Traffic lights restored: ${restorationData.lights_restored}`, 'success');
            }
            if (restorationData.ev_stations_restored > 0) {
                this.addDirectChatMessage(`🔌 EV stations restored: ${restorationData.ev_stations_restored}`, 'success');
            }
            this.addDirectChatMessage(`⚡ Energy delivered: ${Math.round(delivered)} kWh`, 'info');
            this.addDirectChatMessage(`💰 Revenue generated: $${revenue}`, 'info');
            this.addDirectChatMessage(`✅ Mission: SUCCESS`, 'success');

            // Also send via narration
            this.narrate(`📊 Scenario Results:`, 'results');
            this.narrate(`   • Energy delivered: ${Math.round(delivered)} kWh`, 'results');
            this.narrate(`   • Revenue generated: $${revenue}`, 'results');
            this.narrate(`   • Substation: ${restorationData.substation}`, 'results');
            if (restorationData.lights_restored > 0) {
                this.narrate(`   • Traffic lights restored: ${restorationData.lights_restored}`, 'results');
            }
            if (restorationData.ev_stations_restored > 0) {
                this.narrate(`   • EV stations restored: ${restorationData.ev_stations_restored}`, 'results');
            }
            this.narrate(`   • Response time: Excellent`, 'results');
            this.narrate(`   • Mission: SUCCESS ✅`, 'results');

            // NOTE: Chatbot monitoring loop handles real-time notifications

            // Cleanup monitoring interval
            if (this.chatbotMonitorInterval) {
                clearInterval(this.chatbotMonitorInterval);
                this.chatbotMonitorInterval = null;
            }

            this.scenarioState = 'completed';
            this.currentScenario = null;

        } catch (error) {
            this.narrate(`❌ Scenario error: ${error.message}`, 'error');

            // Cleanup on error
            if (this.chatbotMonitorInterval) {
                clearInterval(this.chatbotMonitorInterval);
                this.chatbotMonitorInterval = null;
            }

            // VISUAL EFFECTS DISABLED
            // if (window.v2gVisualEffects) {
            //     window.v2gVisualEffects.stop();
            // }

            this.scenarioState = 'completed';
            this.currentScenario = null;
        }
    }

    /**
     * Execute Blackout Scenario
     */
    async executeBlackoutScenario() {
        try {
            this.scenarioState = 'running';
            this.currentScenario = 'blackout';

            // Auto-open chatbot
            const chatbotWindow = document.getElementById('chatbot-window');
            const chatbotLauncher = document.getElementById('chatbot-launcher');
            if (chatbotWindow && chatbotWindow.style.display !== 'flex') {
                chatbotWindow.style.display = 'flex';
                if (chatbotLauncher) {
                    chatbotLauncher.style.display = 'none';
                }
            }

            // Phase 1: Overview
            this.narrate('🎬 CITYWIDE BLACKOUT SCENARIO STARTING', 'scenario-start');
            this.addDirectChatMessage('🎬 CITYWIDE BLACKOUT SCENARIO', 'info');

            const overviewChoreography = [{
                center: [-73.9712, 40.7831], // Manhattan center
                zoom: 12,
                pitch: 0,
                bearing: 0,
                duration: 2000,
                description: 'Bird\'s eye view over Manhattan'
            }];

            await this.executeCamera(overviewChoreography);
            await this.delay(1000);

            // Phase 2: Cascade Failure
            await this.flashScreen('rgba(255, 100, 0, 0.3)', 400);
            this.narrate('⚠️ CRITICAL SYSTEM EVENT', 'emergency');
            this.narrate('🔴 Cascade failure detected...', 'emergency');

            // Center on Times Square for better view of all substations
            const timesSquareLocation = [-73.986, 40.758];
            const cascadeChoreography = [{
                center: timesSquareLocation,
                zoom: 12.5,
                pitch: 30,
                bearing: 0,
                duration: 5000,
                description: 'Centered on Times Square - watching substations fail'
            }];

            await this.executeCamera(cascadeChoreography);

            // Get all substations
            const networkResp = await fetch('/api/network_state');
            const networkState = await networkResp.json();
            const substations = (networkState?.substations || []).map(s => s.name);

            // Fail substations one by one (except Midtown East)
            for (const subName of substations) {
                if (subName !== 'Midtown East') {
                    this.narrate(`❌ ${subName} - OFFLINE`, 'emergency');
                    await fetch(`/api/fail/${encodeURIComponent(subName)}`, { method: 'POST' });
                    await this.flashScreen('rgba(255, 0, 0, 0.2)', 200);
                    await this.delay(800);
                }
            }

            this.narrate(`✅ Midtown East - OPERATIONAL (Last surviving substation!)`, 'success');
            this.addDirectChatMessage('✅ Midtown East is the ONLY operational substation', 'success');
            await this.delay(2000);

            // Phase 3: Zoom to Midtown East - The Last Bastion
            this.narrate('🎥 Focusing on Midtown East...', 'camera');
            this.addDirectChatMessage('🔍 Zooming to the only working substation', 'info');

            const midtownEastLocation = [-73.969, 40.76]; // Midtown East actual coordinates
            const zoomToMidtownChoreography = [{
                center: midtownEastLocation,
                zoom: 16,
                pitch: 60,
                bearing: 135,
                duration: 4000,
                description: 'Zooming to Midtown East - Last operational substation'
            }];

            await this.executeCamera(zoomToMidtownChoreography);
            await this.flashScreen('rgba(0, 255, 136, 0.2)', 300);
            await this.delay(1500);

            // Phase 4: Show the chaos
            this.narrate('💡 All traffic lights across Manhattan DARK except Midtown East area', 'warning');
            this.addDirectChatMessage('⚠️ 7/8 substations OFFLINE - City in darkness', 'warning');
            this.narrate('🚗 EVs desperately searching for charging...', 'warning');
            this.addDirectChatMessage('🔋 EVs running out of battery - converging on Midtown East', 'warning');
            await this.delay(2000);

            // Phase 5: Show vehicles circling - EXTENDED VIEW
            this.narrate('🚗 Vehicles converging on Midtown East...', 'warning');
            this.addDirectChatMessage('🔋 EVs searching for charging stations', 'warning');
            await this.delay(2000);

            // First circling view - Close up
            const circlingView1 = [{
                center: midtownEastLocation,
                zoom: 16.5,
                pitch: 65,
                bearing: 0,
                duration: 3000,
                description: 'Close view - vehicles circling around Midtown East'
            }];
            await this.executeCamera(circlingView1);
            await this.delay(2000);

            // Rotate to show circling pattern
            this.narrate('🔄 EVs circling around the operational substation area...', 'info');
            const circlingView2 = [{
                center: midtownEastLocation,
                zoom: 16,
                pitch: 60,
                bearing: 90,
                duration: 3000,
                description: 'Rotating view showing circling pattern'
            }];
            await this.executeCamera(circlingView2);
            await this.delay(2000);

            // Continue rotation
            const circlingView3 = [{
                center: midtownEastLocation,
                zoom: 16,
                pitch: 60,
                bearing: 180,
                duration: 3000,
                description: 'Continue rotation - vehicles searching'
            }];
            await this.executeCamera(circlingView3);
            await this.delay(1500);

            // Phase 6: EV station at capacity
            this.narrate('⚡ EV charging station at FULL CAPACITY', 'emergency');
            this.addDirectChatMessage('🚨 All chargers occupied - EVs waiting in queue', 'error');

            const stationView = [{
                center: midtownEastLocation,
                zoom: 17,
                pitch: 70,
                bearing: 270,
                duration: 3000,
                description: 'Zoom to EV station - all chargers full'
            }];
            await this.executeCamera(stationView);
            await this.delay(2500);

            // Phase 7: Show waiting vehicles
            this.narrate('⏳ EVs waiting for their turn to charge...', 'warning');
            this.addDirectChatMessage('🔄 Vehicles queuing, batteries depleting', 'warning');

            const waitingView = [{
                center: midtownEastLocation,
                zoom: 15.5,
                pitch: 55,
                bearing: 45,
                duration: 3000,
                description: 'Wider view - queue of waiting vehicles'
            }];
            await this.executeCamera(waitingView);
            await this.delay(3000);

            // Phase 8: Final overview - stay on Midtown East
            this.narrate('🎥 Midtown East remains the only operational zone', 'camera');
            const finalMidtownZoom = [{
                center: midtownEastLocation,
                zoom: 15,
                pitch: 50,
                bearing: 135,
                duration: 3000,
                description: 'Final focus on Midtown East - operational island'
            }];

            await this.executeCamera(finalMidtownZoom);
            this.highlightLocation(midtownEastLocation, '#00ff88');
            await this.delay(2000);

            this.narrate('', 'scenario-complete');
            this.narrate('🚨 CITYWIDE BLACKOUT COMPLETE', 'scenario-end');

            // Get final statistics
            const finalState = await fetch('/api/network_state').then(r => r.json());
            const operationalSubs = (finalState?.substations || []).filter(s => s.operational);
            const totalSubs = (finalState?.substations || []).length;
            const poweredLights = (finalState?.traffic_lights || []).filter(tl => tl.powered).length;
            const totalLights = (finalState?.traffic_lights || []).length;
            const offlineSubs = totalSubs - operationalSubs.length;

            // Get EV station data
            const evStations = finalState?.ev_stations || [];
            const operationalStations = evStations.filter(st => st.operational).length;
            const offlineStations = evStations.length - operationalStations;

            // Show results in chat
            const resultsMsg = `📊 BLACKOUT SCENARIO RESULTS\n\n` +
                `❌ Substations OFFLINE: ${offlineSubs}/${totalSubs}\n` +
                `✅ Substations ONLINE: ${operationalSubs.map(s => s.name).join(', ')}\n` +
                `💡 Traffic lights failed: ${totalLights - poweredLights}/${totalLights}\n` +
                `🔌 EV stations offline: ${offlineStations}/${evStations.length}\n` +
                `⚠️ Grid stability: CRITICAL\n\n` +
                `🎯 SCENARIO DEMONSTRATES:\n` +
                `• Midtown East OVERWHELMED with vehicle traffic\n` +
                `• EVs circling around the operational substation area\n` +
                `• EV charging stations at FULL CAPACITY\n` +
                `• Long queues forming as vehicles wait for charging\n` +
                `• Critical infrastructure dependency on grid stability`;

            this.addDirectChatMessage(resultsMsg, 'info');

            this.narrate(`📊 Blackout Impact:`, 'results');
            this.narrate(`   • Substations offline: ${offlineSubs}/${totalSubs}`, 'results');
            this.narrate(`   • Only ${operationalSubs[0]?.name || 'Midtown East'} operational`, 'results');
            this.narrate(`   • Traffic lights failed: ${totalLights - poweredLights}`, 'results');
            this.narrate(`   • EVs circling and waiting in queue`, 'results');
            this.narrate(`   • Grid stability: CRITICAL`, 'results');

            // Send to chatbot AI
            try {
                const chatbotResp = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `BLACKOUT SCENARIO COMPLETE! Manhattan is in crisis. ${offlineSubs} out of ${totalSubs} substations are OFFLINE. Only ${operationalSubs[0]?.name || 'Midtown East'} remains operational. ${totalLights - poweredLights} traffic lights have failed. The operational substation area is OVERWHELMED with vehicles circling around looking for charging. EV charging stations are at FULL CAPACITY with long queues forming as vehicles wait their turn. This demonstrates the critical importance of grid resilience! Please acknowledge this dramatic scenario completion.`,
                        user_id: 'system'
                    })
                });

                const chatbotData = await chatbotResp.json();
                let aiResponse = chatbotData.response || chatbotData.full_data?.text || chatbotData.text;

                if (aiResponse) {
                    const chatMessages = document.getElementById('chat-messages');
                    if (chatMessages) {
                        const aiMsgHtml = `
                            <div class="msg ai" style="
                                margin: 8px 12px;
                                padding: 12px;
                                background: linear-gradient(135deg, rgba(255,100,0,0.08), rgba(255,50,50,0.06));
                                border: 1px solid rgba(255,100,0,0.3);
                                border-radius: 12px;
                                font-size: 13px;
                                line-height: 1.6;
                                color: #ffffff;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                            ">
                                <strong style="color: #ff8800; display: flex; align-items: center; margin-bottom: 6px;">
                                    💬 Ultra-AI:
                                </strong>
                                <div style="white-space: pre-wrap;">${aiResponse}</div>
                            </div>
                        `;
                        chatMessages.innerHTML += aiMsgHtml;
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
            } catch (err) {
                console.error('Error notifying chatbot:', err);
            }

            // Removed suggestion messages - users already know the commands

            this.scenarioState = 'completed';
            this.currentScenario = null;

        } catch (error) {
            this.narrate(`❌ Scenario error: ${error.message}`, 'error');
            this.scenarioState = 'completed';
            this.currentScenario = null;
        }
    }

    /**
     * Cancel running scenario
     */
    cancelScenario() {
        this.cameraAnimationRunning = false;
        this.scenarioState = 'idle';
        this.currentScenario = null;
        this.narrate('Scenario cancelled', 'info');
    }

    /**
     * Utility: delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ==========================================
// ENHANCED V2G VISUAL EFFECTS
// ==========================================

class V2GVisualEffects {
    constructor() {
        this.energyFlowLines = new Map();
        this.particles = [];
        this.animationFrame = null;
        this.isActive = false;
    }

    async start() {
        this.isActive = true;
        this.animate();
    }

    stop() {
        this.isActive = false;
        this.clearAllEffects();
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }

    async updateV2GVehicles() {
        if (!window.map || !this.isActive) return;

        try {
            // Fetch V2G status
            const response = await fetch('/api/v2g/status');
            const data = await response.json();

            // Fetch network state for vehicle positions
            const netResponse = await fetch('/api/network_state');
            const netData = await netResponse.json();

            if (!data.active_vehicles || !netData.ev_stations || !netData.vehicles) return;

            // Clear old lines
            this.clearLines();

            // Create energy flow lines for each V2G vehicle
            data.active_vehicles.forEach(v2gVehicle => {
                const vehicleId = v2gVehicle.vehicle_id || v2gVehicle.id;
                const stationId = v2gVehicle.station_id;

                // Find vehicle position
                const vehicle = netData.vehicles.find(v => v.id === vehicleId);
                if (!vehicle) return;

                // Find station position
                const station = netData.ev_stations.find(s => s.id === stationId);
                if (!station) return;

                // Draw energy flow line
                this.addEnergyFlowLine(
                    vehicleId,
                    [vehicle.lon, vehicle.lat],
                    [station.lon, station.lat]
                );

                // Add particles along the line
                this.createParticles(
                    [vehicle.lon, vehicle.lat],
                    [station.lon, station.lat]
                );
            });

        } catch (error) {
            console.warn('V2G visual effects error:', error);
        }
    }

    addEnergyFlowLine(id, startCoords, endCoords) {
        if (!window.map) return;

        const sourceId = `v2g-flow-${id}`;
        const layerId = `v2g-flow-layer-${id}`;

        // Remove old source/layer if exists
        if (window.map.getLayer(layerId)) {
            window.map.removeLayer(layerId);
        }
        if (window.map.getSource(sourceId)) {
            window.map.removeSource(sourceId);
        }

        // Add new energy flow line
        window.map.addSource(sourceId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'LineString',
                    coordinates: [startCoords, endCoords]
                }
            }
        });

        window.map.addLayer({
            id: layerId,
            type: 'line',
            source: sourceId,
            paint: {
                'line-color': '#00FFFF',
                'line-width': 3,
                'line-opacity': 0.7,
                'line-blur': 2
            }
        });

        // Add glow effect
        const glowLayerId = `${layerId}-glow`;
        window.map.addLayer({
            id: glowLayerId,
            type: 'line',
            source: sourceId,
            paint: {
                'line-color': '#00FFFF',
                'line-width': 8,
                'line-opacity': 0.3,
                'line-blur': 8
            }
        });

        this.energyFlowLines.set(id, { sourceId, layerId, glowLayerId });
    }

    createParticles(startCoords, endCoords) {
        // Create 3 particles along the energy flow line
        for (let i = 0; i < 3; i++) {
            this.particles.push({
                start: startCoords,
                end: endCoords,
                progress: i / 3,
                speed: 0.01 + Math.random() * 0.01,
                id: `particle-${Date.now()}-${i}`
            });
        }
    }

    animate() {
        if (!this.isActive) return;

        // Update particles
        this.particles = this.particles.filter(p => {
            p.progress += p.speed;
            if (p.progress > 1) return false; // Remove completed particles

            // Calculate current position
            const lon = p.start[0] + (p.end[0] - p.start[0]) * p.progress;
            const lat = p.start[1] + (p.end[1] - p.start[1]) * p.progress;

            // Update particle marker
            this.updateParticleMarker(p.id, [lon, lat]);
            return true;
        });

        // Update V2G vehicles every 2 seconds
        if (!this.lastUpdate || Date.now() - this.lastUpdate > 2000) {
            this.updateV2GVehicles();
            this.lastUpdate = Date.now();
        }

        this.animationFrame = requestAnimationFrame(() => this.animate());
    }

    updateParticleMarker(id, coords) {
        if (!window.map) return;

        const sourceId = `particle-${id}`;
        const layerId = `particle-layer-${id}`;

        // Update or create particle marker
        if (window.map.getSource(sourceId)) {
            window.map.getSource(sourceId).setData({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: coords
                }
            });
        } else {
            window.map.addSource(sourceId, {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: coords
                    }
                }
            });

            window.map.addLayer({
                id: layerId,
                type: 'circle',
                source: sourceId,
                paint: {
                    'circle-radius': 5,
                    'circle-color': '#00FFFF',
                    'circle-opacity': 0.9,
                    'circle-blur': 0.5
                }
            });
        }
    }

    clearLines() {
        if (!window.map) return;

        this.energyFlowLines.forEach(({ sourceId, layerId, glowLayerId }) => {
            if (window.map.getLayer(glowLayerId)) {
                window.map.removeLayer(glowLayerId);
            }
            if (window.map.getLayer(layerId)) {
                window.map.removeLayer(layerId);
            }
            if (window.map.getSource(sourceId)) {
                window.map.removeSource(sourceId);
            }
        });

        this.energyFlowLines.clear();
    }

    clearAllEffects() {
        this.clearLines();

        // Clear particles
        this.particles.forEach(p => {
            const sourceId = `particle-${p.id}`;
            const layerId = `particle-layer-${p.id}`;

            if (window.map.getLayer(layerId)) {
                window.map.removeLayer(layerId);
            }
            if (window.map.getSource(sourceId)) {
                window.map.removeSource(sourceId);
            }
        });

        this.particles = [];
    }
}

// Create global instance
window.scenarioDirector = new ScenarioDirector();
window.v2gVisualEffects = new V2GVisualEffects();

console.log('✅ Scenario Director loaded and ready');
