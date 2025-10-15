
// Async Optimization Frontend Integration
class AsyncOptimizationClient {
    constructor(apiEndpoint) {
        this.apiEndpoint = apiEndpoint;
        this.activeOptimizations = new Map();
    }
    
    async startAsyncOptimization(workflow) {
        try {
            // Generate optimization ID
            const optimizationId = `opt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            // Start async optimization
            const response = await fetch(`${this.apiEndpoint}/async-optimization`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    optimization_id: optimizationId,
                    workflow_data: {
                        optimization_id: optimizationId,
                        workflow_type: workflow.id,
                        problem_description: workflow.problem_description,
                        custom_parameters: {},
                        industry: workflow.industry,
                        title: workflow.title
                    }
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Track optimization
                this.activeOptimizations.set(optimizationId, {
                    workflow: workflow,
                    startTime: new Date(),
                    status: 'running',
                    progress: 'Starting optimization...'
                });
                
                // Start polling for results
                this.pollOptimizationStatus(optimizationId);
                
                return {
                    optimization_id: optimizationId,
                    status: 'started',
                    message: 'Optimization started successfully'
                };
            } else {
                throw new Error(result.error || 'Failed to start optimization');
            }
        } catch (error) {
            console.error('Async optimization start failed:', error);
            throw error;
        }
    }
    
    async pollOptimizationStatus(optimizationId) {
        const maxAttempts = 120; // 20 minutes with 10-second intervals
        let attempts = 0;
        
        const poll = async () => {
            try {
                const response = await fetch(`${this.apiEndpoint}/optimization-status/${optimizationId}`);
                const status = await response.json();
                
                // Update progress
                this.activeOptimizations.set(optimizationId, {
                    ...this.activeOptimizations.get(optimizationId),
                    status: status.status,
                    progress: status.message,
                    lastUpdate: new Date()
                });
                
                if (status.status === 'completed') {
                    // Optimization completed
                    this.activeOptimizations.set(optimizationId, {
                        ...this.activeOptimizations.get(optimizationId),
                        status: 'completed',
                        results: status.result,
                        endTime: new Date()
                    });
                    
                    // Notify UI
                    this.notifyOptimizationComplete(optimizationId, status.result);
                } else if (status.status === 'failed') {
                    // Optimization failed
                    this.activeOptimizations.set(optimizationId, {
                        ...this.activeOptimizations.get(optimizationId),
                        status: 'failed',
                        error: status.message,
                        endTime: new Date()
                    });
                    
                    // Notify UI
                    this.notifyOptimizationFailed(optimizationId, status.message);
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
    
    getOptimizationStatus(optimizationId) {
        return this.activeOptimizations.get(optimizationId);
    }
    
    getAllActiveOptimizations() {
        return Array.from(this.activeOptimizations.entries()).map(([id, data]) => ({
            id,
            ...data
        }));
    }
}

// Usage in your existing Hero component
const asyncOptimizationClient = new AsyncOptimizationClient('https://your-api-endpoint.com');

// Update your executeWorkflow function
const executeWorkflow = async (workflow) => {
    try {
        setIsLoading(true);
        setShowValueProposition(false);
        setActiveSection('chat');
        
        // Start async optimization
        const result = await asyncOptimizationClient.startAsyncOptimization(workflow);
        
        // Add initial message
        const workflowMessage = {
            id: Date.now(),
            type: 'user',
            content: `Starting ${workflow.title} optimization...`,
            timestamp: new Date().toISOString()
        };
        
        setMessages([workflowMessage]);
        
        // Add progress message
        const progressMessage = {
            id: Date.now() + 1,
            type: 'assistant',
            content: `🚀 Optimization started successfully!\n\n**Optimization ID:** ${result.optimization_id}\n**Status:** ${result.status}\n\nThe optimization is running in the background. You'll receive updates as it progresses.`,
            timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, progressMessage]);
        
        // Listen for completion
        window.addEventListener('optimizationComplete', (event) => {
            const { optimizationId, results } = event.detail;
            
            const successMessage = {
                id: Date.now() + 2,
                type: 'assistant',
                content: `🎉 **${workflow.title}** optimization completed successfully!\n\n**Results:**\n${JSON.stringify(results, null, 2)}`,
                timestamp: new Date().toISOString()
            };
            
            setMessages(prev => [...prev, successMessage]);
            setCurrentOptimizationResult(results);
            setShowOptimizationResults(true);
            setIsLoading(false);
        });
        
        // Listen for failures
        window.addEventListener('optimizationFailed', (event) => {
            const { optimizationId, error } = event.detail;
            
            const errorMessage = {
                id: Date.now() + 2,
                type: 'assistant',
                content: `❌ **${workflow.title}** optimization failed.\n\n**Error:** ${error}\n\nLet me help you with a custom optimization instead.`,
                timestamp: new Date().toISOString()
            };
            
            setMessages(prev => [...prev, errorMessage]);
            setInput(workflow.problem_description || `Optimize ${workflow.title.toLowerCase()}`);
            setIsLoading(false);
        });
        
    } catch (error) {
        console.error('Workflow execution error:', error);
        
        const errorMessage = {
            id: Date.now() + 1,
            type: 'assistant',
            content: `❌ **${workflow.title}** workflow execution failed.\n\n**Error:** ${error.message}\n\nLet me help you with a custom optimization instead.`,
            timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, errorMessage]);
        setInput(workflow.problem_description || `Optimize ${workflow.title.toLowerCase()}`);
        setIsLoading(false);
    }
};
