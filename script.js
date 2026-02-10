/**
 * AI-BOS - Frontend Business Logic
 * Enterprise-level JavaScript for penalty calculator
 */

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        CALCULATE: '/api/v1/calculate',
        THRESHOLDS: '/api/v1/thresholds',
        BATCH: '/api/v1/calculate/batch'
    },
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// State Management
class AppState {
    constructor() {
        this.calculationHistory = JSON.parse(localStorage.getItem('ai-bos-history')) || [];
        this.currentResult = null;
        this.notificationEnabled = true;
    }

    saveToHistory(result) {
        const historyItem = {
            id: result.request_id,
            timestamp: result.timestamp,
            delay: result.input_data.delay_minutes,
            penalty: result.calculation_result.penalty_amount,
            rule: result.calculation_result.rule_applied,
            data: result
        };

        this.calculationHistory.unshift(historyItem);
        
        // Keep only last 50 items
        if (this.calculationHistory.length > 50) {
            this.calculationHistory = this.calculationHistory.slice(0, 50);
        }

        localStorage.setItem('ai-bos-history', JSON.stringify(this.calculationHistory));
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;

        historyList.innerHTML = '';
        
        this.calculationHistory.slice(0, 10).forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span class="history-delay">${item.delay} min</span>
                    <span class="history-penalty">₹${item.penalty.toFixed(2)}</span>
                </div>
                <div style="font-size: 11px; color: #6b7280;">
                    ${new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    • ${item.rule}
                </div>
            `;
            historyItem.onclick = () => this.loadResult(item.data);
            historyList.appendChild(historyItem);
        });
    }

    loadResult(result) {
        this.currentResult = result;
        displayResult(result);
    }
}

// Initialize application state
const appState = new AppState();

// DOM Elements Cache
const elements = {
    delayInput: document.getElementById('delayMinutes'),
    delaySlider: document.getElementById('delaySlider'),
    serviceType: document.getElementById('serviceType'),
    contractId: document.getElementById('contractId'),
    resultsCard: document.getElementById('resultsCard'),
    welcomeCard: document.getElementById('welcomeCard'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    progressFill: document.getElementById('progressFill')
};

// Utility Functions
class Utils {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(amount);
    }

    static formatDateTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    static showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);

        // Add CSS animations
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    static validateInputs() {
        const delay = parseInt(elements.delayInput.value);
        
        if (isNaN(delay) || delay < 0 || delay > 1440) {
            Utils.showNotification('Please enter a valid delay between 0 and 1440 minutes', 'error');
            return false;
        }

        return true;
    }

    static simulateProgress(callback) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            if (elements.progressFill) {
                elements.progressFill.style.width = `${progress}%`;
            }
            
            if (progress >= 100) {
                clearInterval(interval);
                callback();
            }
        }, 100);
    }
}

// API Service
class APIService {
    static async calculatePenalty(data) {
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CALCULATE}`, {
                method: 'POST',
                headers: API_CONFIG.DEFAULT_HEADERS,
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static async getThresholds() {
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.THRESHOLDS}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch thresholds:', error);
            return null;
        }
    }
}

// Core Business Logic
class CalculatorUI {
    static showLoading() {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.style.display = 'flex';
            if (elements.progressFill) {
                elements.progressFill.style.width = '0%';
            }
        }
    }

    static hideLoading() {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.style.display = 'none';
        }
    }

    static showResults() {
        if (elements.resultsCard && elements.welcomeCard) {
            elements.resultsCard.style.display = 'block';
            elements.welcomeCard.style.display = 'none';
        }
    }

    static hideResults() {
        if (elements.resultsCard && elements.welcomeCard) {
            elements.resultsCard.style.display = 'none';
            elements.welcomeCard.style.display = 'block';
        }
    }

    static updateResultDisplay(result) {
        // Update basic information
        document.getElementById('requestId').textContent = result.request_id;
        document.getElementById('timestamp').textContent = Utils.formatDateTime(result.timestamp);
        
        // Update delay value
        const delayValue = document.getElementById('delayValue');
        if (delayValue) {
            delayValue.textContent = `${result.input_data.delay_minutes} minutes`;
        }

        // Update penalty status
        const penaltyStatus = document.getElementById('penaltyStatus');
        if (penaltyStatus) {
            const applied = result.calculation_result.penalty_applied;
            penaltyStatus.textContent = applied ? 'Yes' : 'No';
            penaltyStatus.style.color = applied ? '#ef4444' : '#10b981';
        }

        // Update penalty amount
        const penaltyAmount = document.getElementById('penaltyAmount');
        if (penaltyAmount) {
            const amount = result.calculation_result.penalty_amount;
            penaltyAmount.textContent = Utils.formatCurrency(amount);
            penaltyAmount.style.color = amount > 0 ? '#ef4444' : '#10b981';
        }

        // Update rule applied
        document.getElementById('ruleApplied').textContent = result.calculation_result.rule_applied;

        // Update calculation breakdown
        this.updateBreakdown(result.calculation_result);

        // Update AI explanation
        this.updateAIExplanation(result.ai_explanation);
    }

    static updateBreakdown(calculation) {
        const breakdownContent = document.getElementById('breakdownContent');
        if (!breakdownContent) return;

        let html = '';

        if (calculation.penalty_applied) {
            const breakdown = calculation.calculation_breakdown;
            
            html += `
                <div style="margin-bottom: 16px;">
                    <strong>Base Amount:</strong> ${Utils.formatCurrency(breakdown.base_amount)}
                </div>
            `;

            if (breakdown.variable_amount > 0) {
                html += `
                    <div style="margin-bottom: 16px;">
                        <strong>Variable Amount:</strong> ${Utils.formatCurrency(breakdown.variable_amount)}
                        <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">
                            (${breakdown.overage_minutes} minutes × ${Utils.formatCurrency(breakdown.per_minute_rate)}/min)
                        </div>
                    </div>
                `;
            }

            html += `
                <div style="border-top: 2px solid #e5e7eb; padding-top: 16px; margin-top: 16px;">
                    <strong>Total Penalty:</strong> ${Utils.formatCurrency(breakdown.total)}
                </div>
            `;

            if (calculation.threshold_exceeded) {
                html += `
                    <div style="margin-top: 16px; padding: 12px; background: #fef3c7; border-radius: 6px; font-size: 14px;">
                        <strong>Note:</strong> Delay exceeded threshold by ${calculation.exceeded_by_minutes} minutes
                    </div>
                `;
            }
        } else {
            html = `
                <div style="text-align: center; padding: 20px;">
                    <div style="color: #10b981; font-size: 48px; margin-bottom: 16px;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <strong>No Penalty Applied</strong>
                    <div style="font-size: 14px; color: #6b7280; margin-top: 8px;">
                        Delay is within acceptable threshold
                    </div>
                </div>
            `;
        }

        breakdownContent.innerHTML = html;
    }

    static updateAIExplanation(explanation) {
        const explanationContent = document.getElementById('explanationContent');
        const confidenceScore = document.getElementById('confidenceScore');

        if (!explanationContent || !confidenceScore) return;

        if (explanation && explanation.explanation) {
            explanationContent.innerHTML = `
                <div style="font-size: 15px; line-height: 1.7; color: #374151;">
                    ${explanation.explanation}
                </div>
            `;

            if (explanation.confidence_score) {
                confidenceScore.textContent = `${(explanation.confidence_score * 100).toFixed(1)}%`;
                confidenceScore.style.color = explanation.confidence_score > 0.8 ? '#10b981' : 
                                           explanation.confidence_score > 0.6 ? '#f59e0b' : '#ef4444';
            }
        } else {
            explanationContent.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #6b7280;">
                    <i class="fas fa-robot" style="font-size: 24px; margin-bottom: 12px; display: block;"></i>
                    Unable to generate AI explanation at this time.
                </div>
            `;
            confidenceScore.textContent = '0%';
            confidenceScore.style.color = '#ef4444';
        }
    }
}

// Event Handlers
function updateSlider() {
    if (elements.delayInput && elements.delaySlider) {
        elements.delaySlider.value = elements.delayInput.value;
    }
}

function updateInput() {
    if (elements.delayInput && elements.delaySlider) {
        elements.delayInput.value = elements.delaySlider.value;
    }
}

function setDelay(minutes) {
    if (elements.delayInput && elements.delaySlider) {
        elements.delayInput.value = minutes;
        elements.delaySlider.value = minutes;
    }
}

async function calculatePenalty() {
    if (!Utils.validateInputs()) return;

    const requestData = {
        delay_minutes: parseInt(elements.delayInput.value),
        service_type: elements.serviceType?.value || 'standard',
        contract_id: elements.contractId?.value || undefined
    };

    CalculatorUI.showLoading();
    
    try {
        Utils.simulateProgress(async () => {
            try {
                const result = await APIService.calculatePenalty(requestData);
                
                // Update UI
                CalculatorUI.showResults();
                CalculatorUI.updateResultDisplay(result);
                CalculatorUI.hideLoading();
                
                // Save to history
                appState.saveToHistory(result);
                appState.currentResult = result;
                
                Utils.showNotification('Calculation completed successfully!', 'success');
            } catch (error) {
                CalculatorUI.hideLoading();
                Utils.showNotification('Failed to calculate penalty. Please try again.', 'error');
                console.error('Calculation error:', error);
            }
        });
    } catch (error) {
        CalculatorUI.hideLoading();
        Utils.showNotification('An unexpected error occurred.', 'error');
    }
}

function resetForm() {
    if (elements.delayInput) elements.delayInput.value = '45';
    if (elements.delaySlider) elements.delaySlider.value = '45';
    if (elements.serviceType) elements.serviceType.value = 'standard';
    if (elements.contractId) elements.contractId.value = '';
    
    CalculatorUI.hideResults();
    Utils.showNotification('Form has been reset', 'info');
}

async function sendNotification() {
    if (!appState.currentResult) {
        Utils.showNotification('Please calculate a penalty first', 'error');
        return;
    }

    const email = document.getElementById('recipientEmail')?.value;
    const phone = document.getElementById('recipientPhone')?.value;
    const statusElement = document.getElementById('notificationStatus');

    if (!email && !phone) {
        Utils.showNotification('Please enter email or phone number', 'error');
        return;
    }

    if (statusElement) {
        statusElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <i class="fas fa-spinner fa-spin"></i>
                Sending notifications...
            </div>
        `;
        statusElement.style.color = '#f59e0b';
    }

    // Simulate API call
    setTimeout(() => {
        if (statusElement) {
            statusElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <i class="fas fa-check-circle" style="color: #10b981;"></i>
                    Notifications sent successfully!
                </div>
            `;
            statusElement.style.color = '#10b981';
        }

        Utils.showNotification('Notifications sent successfully (simulated)', 'success');
        
        // Reset after 3 seconds
        setTimeout(() => {
            if (statusElement) {
                statusElement.innerHTML = 'Ready to send notifications';
                statusElement.style.color = '#6b7280';
            }
        }, 3000);
    }, 1500);
}

function saveResult() {
    if (!appState.currentResult) {
        Utils.showNotification('No result to save', 'error');
        return;
    }

    const dataStr = JSON.stringify(appState.currentResult, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `ai-bos-result-${appState.currentResult.request_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    Utils.showNotification('Result saved as JSON file', 'success');
}

function shareResult() {
    if (!appState.currentResult) {
        Utils.showNotification('No result to share', 'error');
        return;
    }

    if (navigator.share) {
        navigator.share({
            title: 'AI-BOS Penalty Calculation',
            text: `Delay: ${appState.currentResult.input_data.delay_minutes}min, Penalty: ₹${appState.currentResult.calculation_result.penalty_amount}`,
            url: window.location.href
        }).catch(error => {
            console.log('Error sharing:', error);
        });
    } else {
        // Fallback: Copy to clipboard
        const text = `AI-BOS Result: ${appState.currentResult.input_data.delay_minutes}min delay = ₹${appState.currentResult.calculation_result.penalty_amount} penalty`;
        navigator.clipboard.writeText(text).then(() => {
            Utils.showNotification('Result copied to clipboard', 'success');
        });
    }
}

function showHistory() {
    Utils.showNotification('Showing calculation history', 'info');
    // In a real implementation, this would open a modal or navigate to a history page
}

function exportData() {
    const data = {
        timestamp: new Date().toISOString(),
        history: appState.calculationHistory,
        thresholds: {
            no_penalty_max: 30,
            low_penalty_max: 60,
            amounts: {
                fixed_penalty: 500,
                variable_rate: 25,
                high_penalty_base: 1000
            }
        }
    };

    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `ai-bos-export-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    Utils.showNotification('Data exported successfully', 'success');
}

// Index Page Functions
function sc