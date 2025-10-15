
// Enhanced optimization with progress tracking
class EnhancedOptimizationClient {
    constructor(apiEndpoint) {
        this.apiEndpoint = apiEndpoint;
        this.activeOptimizations = new Map();
    }
    
    async startOptimization(workflow) {
        try {
            // Start async optimization
            const response = await fetch(`${this.apiEndpoint}/async-optimization`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    workflow_type: workflow.id,
                    problem_description: workflow.problem_description,
                    custom_parameters: {}
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'started') {
                // Track optimization
                this.activeOptimizations.set(result.optimization_id, {
                    workflow: workflow,
                    startTime: new Date(),
                    status: 'running'
                });
                
                // Start polling for results
                this.pollOptimizationStatus(result.optimization_id);
                
                return result;
            } else {
                throw new Error(result.error || 'Failed to start optimization');
            }
        } catch (error) {
            console.error('Optimization start failed:', error);
            throw error;
        }
    }
    
    async pollOptimizationStatus(optimizationId) {
        const maxAttempts = 60; // 10 minutes with 10-second intervals
        let attempts = 0;
        
        const poll = async () => {
            try {
                const response = await fetch(`${this.apiEndpoint}/optimization-status/${optimizationId}`);
                const status = await response.json();
                
                if (status.status === 'completed') {
                    // Optimization completed
                    this.activeOptimizations.set(optimizationId, {
                        ...this.activeOptimizations.get(optimizationId),
                        status: 'completed',
                        results: status.results,
                        endTime: new Date()
                    });
                    
                    // Notify UI
                    this.notifyOptimizationComplete(optimizationId, status.results);
                } else if (status.status === 'failed') {
                    // Optimization failed
                    this.activeOptimizations.set(optimizationId, {
                        ...this.activeOptimizations.get(optimizationId),
                        status: 'failed',
                        error: status.error,
                        endTime: new Date()
                    });
                    
                    // Notify UI
                    this.notifyOptimizationFailed(optimizationId, status.error);
                } else if (attempts < maxAttempts) {
                    // Still running, continue polling
                    attempts++;
                    setTimeout(poll, 10000); // Poll every 10 seconds
                } else {
                    // Timeout
                    this.activeOptimizations.set(optimizationId, {
                        ...this.activeOptimizations.get(optimizationId),
                        status: 'timeout',
                        endTime: new Date()
                    });
                    
                    this.notifyOptimizationTimeout(optimizationId);
                }
            } catch (error) {
                console.error('Status polling failed:', error);
                setTimeout(poll, 10000); // Retry after 10 seconds
            }
        };
        
        // Start polling
        setTimeout(poll, 5000); // Start polling after 5 seconds
    }
    
    notifyOptimizationComplete(optimizationId, results) {
        // Emit event or call callback
        const event = new CustomEvent('optimizationComplete', {
            detail: { optimizationId, results }
        });
        window.dispatchEvent(event);
    }
    
    notifyOptimizationFailed(optimizationId, error) {
        const event = new CustomEvent('optimizationFailed', {
            detail: { optimizationId, error }
        });
        window.dispatchEvent(event);
    }
    
    notifyOptimizationTimeout(optimizationId) {
        const event = new CustomEvent('optimizationTimeout', {
            detail: { optimizationId }
        });
        window.dispatchEvent(event);
    }
}

// Usage
const optimizationClient = new EnhancedOptimizationClient('https://your-api-endpoint.com');
