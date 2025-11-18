/**
 * AI Enhanced Functions for Manhattan Power Grid
 * Support functions for the world-class AI integration
 */

/**
 * Send a suggestion to the Ultra-Intelligent Chatbot
 */
function sendSuggestion(text) {
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = text;
        sendChatMessage();
    }
}

async function showAIResearchInsights() {
    try {
        showNotification('🔬 Generating research-level AI insights...', 'info');

        const response = await fetch('/api/ai/enhanced/research');
        const data = await response.json();

        const resultsDiv = document.getElementById('ml-results');
        if (resultsDiv) {
            resultsDiv.style.display = 'block';

            if (data.error) {
                resultsDiv.innerHTML = `
                    <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 12px; padding: 16px; margin-top: 16px;">
                        <h4 style="color: #ff6b6b; margin-bottom: 12px;">❌ Research Analysis Error</h4>
                        <p style="color: var(--text-secondary);">${data.error}</p>
                    </div>
                `;
            } else {
                resultsDiv.innerHTML = `
                    <div style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 170, 255, 0.05)); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; padding: 20px; margin-top: 16px;">
                        <h4 style="color: #00ff88; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                            🔬 Research-Level AI Analysis
                            <span style="font-size: 11px; background: rgba(0, 255, 136, 0.2); padding: 2px 8px; border-radius: 10px;">
                                World-Class Intelligence
                            </span>
                        </h4>

                        <div style="margin-bottom: 16px; padding: 12px; background: rgba(0, 0, 0, 0.2); border-radius: 8px;">
                            <p style="color: var(--text-secondary); font-style: italic; margin: 0;">
                                ${data.research_summary || 'Advanced AI analysis complete'}
                            </p>
                        </div>

                        ${data.pattern_analysis ? `
                            <div style="margin-bottom: 16px;">
                                <h5 style="color: #00aaff; margin-bottom: 8px;">📊 Pattern Analysis</h5>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px;">
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #00ff88;">${data.pattern_analysis.detected_patterns}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Patterns</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #ffaa00;">${(data.pattern_analysis.anomaly_score || 0).toFixed(3)}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Anomaly Score</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #c8a2ff;">${data.pattern_analysis.trend_direction || 'stable'}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Trend</div>
                                    </div>
                                </div>
                            </div>
                        ` : ''}

                        ${data.predictive_intelligence ? `
                            <div style="margin-bottom: 16px;">
                                <h5 style="color: #00aaff; margin-bottom: 8px;">🔮 Predictive Intelligence</h5>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px;">
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #00ff88;">${data.predictive_intelligence.forecast_horizon}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Forecast</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #ffaa00;">${((data.predictive_intelligence.grid_stability_trend || 0) * 100).toFixed(1)}%</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Stability</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #c8a2ff;">${data.predictive_intelligence.optimization_windows}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Opt Windows</div>
                                    </div>
                                </div>
                            </div>
                        ` : ''}

                        ${data.ai_performance ? `
                            <div style="margin-bottom: 16px;">
                                <h5 style="color: #00aaff; margin-bottom: 8px;">⚡ AI Performance</h5>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px;">
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #00ff88;">${(data.ai_performance.response_time || 0).toFixed(2)}s</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Response Time</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #ffaa00;">${((data.ai_performance.accuracy || 0) * 100).toFixed(1)}%</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Accuracy</div>
                                    </div>
                                    <div style="background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 18px; font-weight: bold; color: #c8a2ff;">${data.ai_performance.learning_progress || 'stable'}</div>
                                        <div style="font-size: 12px; color: var(--text-muted);">Learning</div>
                                    </div>
                                </div>
                            </div>
                        ` : ''}

                        ${data.advanced_capabilities ? `
                            <div>
                                <h5 style="color: #00aaff; margin-bottom: 8px;">🚀 Advanced Capabilities</h5>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 8px; font-size: 12px;">
                                    ${data.advanced_capabilities.map(cap => `
                                        <div style="background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 16px; color: var(--text-secondary);">
                                            ${cap}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            }

            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        showNotification('🔬 Research insights generated successfully!', 'success');

    } catch (error) {
        console.error('AI research insights failed:', error);
        showNotification(`❌ Research insights failed: ${error.message}`, 'error');
    }
}

async function showAIVisualAnalysis() {
    try {
        showNotification('👁️ Analyzing visual map state...', 'info');

        const response = await fetch('/api/ai/enhanced/visual', { method: 'POST' });
        const data = await response.json();

        if (window.aiEnhanced) {
            window.aiEnhanced.displayAIResponse('👁️ Visual analysis completed', data, 'visual-analysis');
        } else {
            console.log('Visual Analysis Result:', data);
            showNotification('👁️ Visual analysis completed - check console', 'success');
        }

    } catch (error) {
        console.error('Visual analysis failed:', error);
        showNotification(`❌ Visual analysis failed: ${error.message}`, 'error');
    }
}

async function showAIPatternAnalysis() {
    try {
        showNotification('📊 Analyzing system patterns...', 'info');

        const response = await fetch('/api/ai/enhanced/patterns');
        const data = await response.json();

        if (window.aiEnhanced) {
            window.aiEnhanced.displayAIResponse('📊 Pattern analysis completed', data, 'pattern-analysis');
        } else {
            console.log('Pattern Analysis Result:', data);
            showNotification('📊 Pattern analysis completed - check console', 'success');
        }

    } catch (error) {
        console.error('Pattern analysis failed:', error);
        showNotification(`❌ Pattern analysis failed: ${error.message}`, 'error');
    }
}

async function showAIPredictions() {
    try {
        showNotification('🔮 Generating AI predictions...', 'info');

        const response = await fetch('/api/ai/enhanced/predictions');
        const data = await response.json();

        if (window.aiEnhanced) {
            window.aiEnhanced.displayAIResponse('🔮 Predictions generated', data, 'predictions');
        } else {
            console.log('AI Predictions Result:', data);
            showNotification('🔮 Predictions generated - check console', 'success');
        }

    } catch (error) {
        console.error('AI predictions failed:', error);
        showNotification(`❌ AI predictions failed: ${error.message}`, 'error');
    }
}

async function showAIComprehensiveReport() {
    try {
        showNotification('📋 Generating comprehensive AI report...', 'info');

        const response = await fetch('/api/ai/enhanced/comprehensive-report');
        const data = await response.json();

        if (data.text) {
            // Display the report in the chat
            if (window.aiEnhanced) {
                window.aiEnhanced.displayAIResponse('📋 Comprehensive report generated', data, 'comprehensive-report');
            }

            // Also create a modal or dedicated display
            showAIReportModal(data);
        } else {
            console.log('Comprehensive Report Result:', data);
            showNotification('📋 Comprehensive report generated - check console', 'success');
        }

    } catch (error) {
        console.error('Comprehensive report failed:', error);
        showNotification(`❌ Comprehensive report failed: ${error.message}`, 'error');
    }
}

function showAIReportModal(reportData) {
    // Create modal for comprehensive report
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(10px);
    `;

    modal.innerHTML = `
        <div style="background: var(--bg-dark); border-radius: 16px; padding: 32px; max-width: 900px; max-height: 80vh; overflow-y: auto; border: 1px solid rgba(0, 255, 136, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h2 style="color: #00ff88; margin: 0;">📋 Comprehensive AI Report</h2>
                <button onclick="this.closest('div').parentElement.remove()" style="background: none; border: none; color: #fff; font-size: 24px; cursor: pointer;">✕</button>
            </div>

            <div style="white-space: pre-line; color: var(--text-secondary); line-height: 1.6; font-family: 'JetBrains Mono', monospace; font-size: 13px;">
                ${reportData.text || JSON.stringify(reportData, null, 2)}
            </div>

            <div style="margin-top: 24px; display: flex; gap: 12px;">
                <button onclick="downloadAIReport('${reportData.timestamp || Date.now()}')" class="btn btn-primary">📄 Download Report</button>
                <button onclick="copyAIReportToClipboard('${encodeURIComponent(reportData.text || '')}')" class="btn btn-secondary">📋 Copy to Clipboard</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function downloadAIReport(timestamp) {
    // This would generate and download a PDF report
    showNotification('📄 Report download feature would be implemented here', 'info');
}

function copyAIReportToClipboard(encodedText) {
    try {
        const text = decodeURIComponent(encodedText);
        navigator.clipboard.writeText(text);
        showNotification('📋 Report copied to clipboard!', 'success');
    } catch (error) {
        showNotification('❌ Failed to copy report', 'error');
    }
}

async function getAIStatus() {
    try {
        const response = await fetch('/api/ai/enhanced/status');
        const status = await response.json();

        console.log('🤖 AI System Status:', status);
        return status;

    } catch (error) {
        console.error('AI status check failed:', error);
        return null;
    }
}

async function getConversationIntelligence(userId = 'anonymous') {
    try {
        const response = await fetch(`/api/ai/enhanced/conversation/${userId}`);
        const intelligence = await response.json();

        console.log('🧠 Conversation Intelligence:', intelligence);
        return intelligence;

    } catch (error) {
        console.error('Conversation intelligence failed:', error);
        return null;
    }
}

// Enhanced askAIAdvice function
async function askAIAdvice() {
    if (window.aiEnhanced) {
        // Use the enhanced AI system
        try {
            const response = await window.aiEnhanced.sendEnhancedMessage(
                'Please provide comprehensive system insights, optimization recommendations, and current status analysis.',
                { request_type: 'comprehensive_advice' }
            );

            if (response) {
                showNotification('🤖 AI advice generated successfully!', 'success');
            }
        } catch (error) {
            console.error('Enhanced AI advice failed:', error);
            // Fallback to original implementation
            originalAskAIAdvice();
        }
    } else {
        // Fallback to fetch API directly
        try {
            const response = await fetch('/api/ai/advice?q=Provide comprehensive system insights and recommendations');
            const data = await response.json();

            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                const aiMessage = document.createElement('div');
                aiMessage.className = 'chat-message assistant';
                aiMessage.innerHTML = `
                    <div class="message-content">
                        <div style="color: #00ff88; font-weight: 600; margin-bottom: 8px;">🤖 AI Advisor</div>
                        <div style="white-space: pre-line;">${data.advice || 'AI advice not available'}</div>
                    </div>
                `;
                chatMessages.appendChild(aiMessage);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            showNotification('🤖 AI advice provided', 'success');

        } catch (error) {
            console.error('AI advice failed:', error);
            showNotification(`❌ AI advice failed: ${error.message}`, 'error');
        }
    }
}

// Initialize AI functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Enhanced Functions loaded');

    // Add AI status check
    setTimeout(async () => {
        const status = await getAIStatus();
        if (status) {
            console.log(`✅ AI System Active: ${status.active_conversations} conversations, ${status.advanced_features?.length || 0} features`);
        }
    }, 2000);
});

// Export functions for global use
window.showAIResearchInsights = showAIResearchInsights;
window.showAIVisualAnalysis = showAIVisualAnalysis;
window.showAIPatternAnalysis = showAIPatternAnalysis;
window.showAIPredictions = showAIPredictions;
window.showAIComprehensiveReport = showAIComprehensiveReport;
window.getAIStatus = getAIStatus;
window.getConversationIntelligence = getConversationIntelligence;