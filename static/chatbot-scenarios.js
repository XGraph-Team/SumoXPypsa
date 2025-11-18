/**
 * CHATBOT SCENARIO INTEGRATION
 * Connects chatbot to scenario director for world-class scenario execution
 */

class ChatbotScenarioHandler {
    constructor() {
        this.pendingScenario = null;
        this.scenarioPreparationData = null;
        this.awaitingConfirmation = false;

        // Initialize when scenario director is ready
        if (window.scenarioDirector) {
            this.initialize();
        } else {
            // Wait for scenario director to load
            setTimeout(() => this.initialize(), 1000);
        }
    }

    initialize() {
        if (!window.scenarioDirector) {
            console.error('Scenario Director not available');
            return;
        }

        // Set narration callback for live updates
        window.scenarioDirector.setNarrationCallback((message, type) => {
            this.displayScenarioNarration(message, type);
        });

        console.log('✅ Chatbot Scenario Handler initialized');
    }

    /**
     * Display scenario narration in chat
     */
    displayScenarioNarration(message, type) {
        console.log('[SCENARIO NARRATION]', type, message); // DEBUG

        if (!message && type !== 'scenario-complete') return;

        // AUTO-OPEN CHATBOT WINDOW IF CLOSED - THIS IS THE FIX!
        const chatbotWindow = document.getElementById('chatbot-window');
        const chatbotLauncher = document.getElementById('chatbot-launcher');
        if (chatbotWindow && chatbotWindow.style.display !== 'flex') {
            chatbotWindow.style.display = 'flex';
            if (chatbotLauncher) {
                chatbotLauncher.style.display = 'none';
            }
            console.log('[SCENARIO NARRATION] Auto-opened chatbot window');
        }

        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) {
            console.error('[SCENARIO NARRATION] Chat messages element not found!');
            return;
        }

        let style = '';
        let icon = '';
        let borderColor = '';

        switch (type) {
            case 'scenario-start':
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,200,255,0.12)); border: 2px solid rgba(0,255,136,0.5);';
                icon = '🎬';
                borderColor = '#00ff88';
                break;
            case 'scenario-end':
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,255,0,0.15)); border: 2px solid rgba(0,255,136,0.7);';
                icon = '🎉';
                borderColor = '#00ff88';
                break;
            case 'emergency':
                style = 'background: linear-gradient(135deg, rgba(255,50,50,0.2), rgba(200,0,0,0.15)); border: 1px solid rgba(255,50,50,0.5);';
                icon = '🚨';
                borderColor = '#ff3232';
                break;
            case 'success':
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,200,100,0.08)); border: 1px solid rgba(0,255,136,0.3);';
                icon = '✅';
                borderColor = '#00ff88';
                break;
            case 'warning':
                style = 'background: linear-gradient(135deg, rgba(255,170,0,0.12), rgba(255,120,0,0.08)); border: 1px solid rgba(255,170,0,0.3);';
                icon = '⚠️';
                borderColor = '#ffaa00';
                break;
            case 'error':
                style = 'background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(255,50,50,0.08)); border: 1px solid rgba(255,107,107,0.3);';
                icon = '❌';
                borderColor = '#ff6b6b';
                break;
            case 'camera':
                style = 'background: linear-gradient(135deg, rgba(0,170,255,0.1), rgba(0,120,200,0.06)); border: 1px solid rgba(0,170,255,0.25);';
                icon = '🎥';
                borderColor = '#00aaff';
                break;
            case 'progress':
                style = 'background: linear-gradient(135deg, rgba(0,200,255,0.1), rgba(0,150,255,0.06)); border: 1px solid rgba(0,200,255,0.25);';
                icon = '⚡';
                borderColor = '#00ccff';
                break;
            case 'results':
                style = 'background: linear-gradient(135deg, rgba(200,140,255,0.1), rgba(150,100,255,0.06)); border: 1px solid rgba(200,140,255,0.25);';
                icon = '📊';
                borderColor = '#c88cff';
                break;
            case 'scenario-complete':
                // Add spacing before results
                chatMessages.innerHTML += `<div style="height: 8px;"></div>`;
                return;
            default:
                style = 'background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);';
                icon = '💬';
                borderColor = 'rgba(255,255,255,0.2)';
        }

        const narrationHtml = `
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

        chatMessages.innerHTML += narrationHtml;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        console.log('[SCENARIO NARRATION] Message added to chat!'); // DEBUG
    }

    /**
     * Handle scenario preparation response from chatbot
     */
    async handleScenarioPrepResponse(scenarioType) {
        try {
            // Get preparation status
            let prepStatus;
            if (scenarioType === 'v2g') {
                prepStatus = await window.scenarioDirector.prepareV2GScenario();
            } else if (scenarioType === 'blackout') {
                prepStatus = await window.scenarioDirector.prepareBlackoutScenario();
            } else {
                this.displayChatMessage('❌ Unknown scenario type', 'error');
                return;
            }

            // Check if SUMO is running
            if (!prepStatus.sumo_running) {
                this.displayChatMessage(
                    `⚠️ SUMO traffic simulation is not running!\n\n` +
                    `To run scenarios, you need active vehicles. Please:\n` +
                    `1. Go to the "Vehicles" tab\n` +
                    `2. Click "▶️ Start Vehicles"\n` +
                    `3. Wait for vehicles to spawn\n` +
                    `4. Then try the scenario again\n\n` +
                    `Or type "start vehicles" and I'll do it for you!`,
                    'warning'
                );
                return;
            }

            // Store pending scenario
            this.pendingScenario = scenarioType;
            this.scenarioPreparationData = prepStatus;

            // Build scenario overview message
            let scenarioName = scenarioType === 'v2g' ? 'V2G EMERGENCY RESCUE' : 'CITYWIDE BLACKOUT';
            let scenarioDesc = scenarioType === 'v2g'
                ? 'Times Square substation fails, EVs provide emergency power'
                : 'Manhattan-wide power failure, 7/8 substations go offline';

            let message = `🎬 **${scenarioName}**\n`;
            message += `${scenarioDesc}\n\n`;

            // Show current state - condensed
            message += `📊 ${prepStatus.current_state.total} vehicles (${prepStatus.current_state.evs} EVs`;
            if (scenarioType === 'v2g') {
                message += `, ${prepStatus.current_state.highSOCEVs} high-charge)`;
            } else {
                message += `, ${prepStatus.current_state.lowSOCEVs} low-charge)`;
            }
            message += `\n\n`;

            // Check if preparation is needed - condensed
            if (prepStatus.needs_preparation) {
                if (scenarioType === 'v2g') {
                    message += `💡 Will spawn high-charge EVs (~90%) for emergency response\n\n`;
                } else {
                    message += `💡 Will spawn low-charge EVs (~30%) to show grid dependency\n\n`;
                }
            } else {
                message += `✅ System ready!\n\n`;
            }

            // Show what will happen - condensed
            if (scenarioType === 'v2g') {
                message += `🎥 Times Square fails → EVs respond → Auto-restore → Stats\n\n`;
            } else {
                message += `🎥 7/8 substations fail → Lights go dark → Emergency mode\n`;
                message += `⚠️ Manual restoration required\n\n`;
            }

            // Confirmation prompt
            message += `⏱️ ${scenarioType === 'v2g' ? '~60 seconds' : 'Until manual restore'}\n`;
            message += `Type "confirm" to ${prepStatus.needs_preparation ? 'prepare & ' : ''}start or "cancel" to abort`;

            // Display message with clickable confirmation buttons
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                const messageHtml = `
                    <div class="msg ai" style="
                        margin: 8px 12px;
                        padding: 12px;
                        background: linear-gradient(135deg, rgba(0,170,255,0.12), rgba(0,120,200,0.08));
                        border: 2px solid rgba(0,170,255,0.4);
                        border-radius: 12px;
                        font-size: 13px;
                        line-height: 1.6;
                        color: #ffffff;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    ">
                        <strong style="color: #00ff88; display: flex; align-items: center; margin-bottom: 6px;">
                            🎬 Ultra-AI:
                        </strong>
                        <div style="white-space: pre-wrap;">${message}</div>
                        <div style="display: flex; gap: 12px; margin-top: 16px; justify-content: center;">
                            <button onclick="sendSuggestion('confirm')" style="
                                padding: 10px 24px;
                                background: linear-gradient(135deg, #00ff88, #00cc66);
                                border: none;
                                border-radius: 8px;
                                color: #000;
                                font-weight: bold;
                                font-size: 14px;
                                cursor: pointer;
                                box-shadow: 0 4px 12px rgba(0,255,136,0.3);
                                transition: all 0.3s;
                            " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 16px rgba(0,255,136,0.5)'"
                               onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 12px rgba(0,255,136,0.3)'">
                                ✅ CONFIRM & START
                            </button>
                            <button onclick="sendSuggestion('cancel')" style="
                                padding: 10px 24px;
                                background: linear-gradient(135deg, #ff6b6b, #cc4444);
                                border: none;
                                border-radius: 8px;
                                color: #fff;
                                font-weight: bold;
                                font-size: 14px;
                                cursor: pointer;
                                box-shadow: 0 4px 12px rgba(255,107,107,0.3);
                                transition: all 0.3s;
                            " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 16px rgba(255,107,107,0.5)'"
                               onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 12px rgba(255,107,107,0.3)'">
                                ❌ CANCEL
                            </button>
                        </div>
                    </div>
                `;
                chatMessages.innerHTML += messageHtml;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            this.awaitingConfirmation = true;

        } catch (error) {
            console.error('Scenario preparation error:', error);
            this.displayChatMessage(`❌ Scenario preparation failed: ${error.message}`, 'error');
        }
    }

    /**
     * Handle scenario confirmation
     */
    async handleScenarioConfirmation() {
        if (!this.awaitingConfirmation || !this.pendingScenario) {
            this.displayChatMessage('No scenario pending confirmation.', 'info');
            return;
        }

        this.awaitingConfirmation = false;
        const scenarioType = this.pendingScenario;
        const prepData = this.scenarioPreparationData;

        this.displayChatMessage(`✅ Confirmed! Starting ${scenarioType === 'v2g' ? 'V2G Rescue' : 'Blackout'} scenario...`, 'success');

        try {
            // Step 1: Spawn vehicles if needed
            if (prepData.needs_preparation) {
                const chargeLevel = scenarioType === 'v2g' ? '90%' : '30%';
                this.displayScenarioNarration(`🚗 Spawning vehicles with ${chargeLevel} charge...`, 'info');

                const spawnConfig = {
                    count: 50, // Always spawn 50 vehicles for both scenarios
                    ev_percentage: scenarioType === 'v2g' ? 100 : 40,
                    min_soc: scenarioType === 'v2g' ? 70 : 25,  // V2G: 70-95%, Blackout: 25-35%
                    max_soc: scenarioType === 'v2g' ? 95 : 35
                };

                console.log('[SCENARIO] Spawning config:', spawnConfig);

                const spawnResult = await window.scenarioDirector.spawnVehicles(spawnConfig);

                if (!spawnResult.success) {
                    this.displayChatMessage(`❌ Vehicle spawning failed: ${spawnResult.error}`, 'error');
                    this.pendingScenario = null;
                    this.scenarioPreparationData = null;
                    return;
                }

                this.displayScenarioNarration('✅ Vehicle preparation complete!', 'success');
                await window.scenarioDirector.delay(1000);
            }

            // Step 2: Execute scenario
            if (scenarioType === 'v2g') {
                await window.scenarioDirector.executeV2GScenario();
            } else if (scenarioType === 'blackout') {
                await window.scenarioDirector.executeBlackoutScenario();
            }

            // Clear pending scenario
            this.pendingScenario = null;
            this.scenarioPreparationData = null;

        } catch (error) {
            console.error('Scenario execution error:', error);
            this.displayChatMessage(`❌ Scenario execution failed: ${error.message}`, 'error');
            this.pendingScenario = null;
            this.scenarioPreparationData = null;
        }
    }

    /**
     * Handle scenario cancellation
     */
    handleScenarioCancellation() {
        if (!this.awaitingConfirmation) {
            return;
        }

        this.awaitingConfirmation = false;
        this.pendingScenario = null;
        this.scenarioPreparationData = null;

        this.displayChatMessage('✅ Scenario cancelled. Let me know if you\'d like to try something else!', 'info');
    }

    /**
     * Display message in chatbot
     */
    displayChatMessage(message, type = 'info') {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        let style = '';
        let icon = '💬';

        switch (type) {
            case 'scenario-prep':
                style = 'background: linear-gradient(135deg, rgba(0,170,255,0.12), rgba(0,120,200,0.08)); border: 2px solid rgba(0,170,255,0.4);';
                icon = '🎬';
                break;
            case 'success':
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,200,100,0.08)); border: 1px solid rgba(0,255,136,0.3);';
                icon = '✅';
                break;
            case 'warning':
                style = 'background: linear-gradient(135deg, rgba(255,170,0,0.12), rgba(255,120,0,0.08)); border: 1px solid rgba(255,170,0,0.3);';
                icon = '⚠️';
                break;
            case 'error':
                style = 'background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(255,50,50,0.08)); border: 1px solid rgba(255,107,107,0.3);';
                icon = '❌';
                break;
            default:
                style = 'background: linear-gradient(135deg, rgba(0,255,136,0.08), rgba(0,200,255,0.06)); border: 1px solid rgba(0,255,136,0.2);';
        }

        const messageHtml = `
            <div class="msg ai" style="
                margin: 8px 12px;
                padding: 12px;
                ${style}
                border-radius: 12px;
                font-size: 13px;
                line-height: 1.6;
                color: #ffffff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            ">
                <strong style="color: #00ff88; display: flex; align-items: center; margin-bottom: 6px;">
                    ${icon} Ultra-AI:
                </strong>
                <div style="white-space: pre-wrap;">${message}</div>
            </div>
        `;

        chatMessages.innerHTML += messageHtml;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Process chatbot response for scenario commands
     */
    processChatbotResponse(response) {
        if (!response || !response.text) return false;

        const text = response.text;

        // Check for scenario preparation marker
        if (text.includes('[SCENARIO_PREP:v2g]')) {
            this.handleScenarioPrepResponse('v2g');
            return true;
        }

        if (text.includes('[SCENARIO_PREP:blackout]')) {
            this.handleScenarioPrepResponse('blackout');
            return true;
        }

        return false;
    }
}

// Create global instance
window.chatbotScenarioHandler = new ChatbotScenarioHandler();

console.log('✅ Chatbot Scenario Handler loaded');

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);
