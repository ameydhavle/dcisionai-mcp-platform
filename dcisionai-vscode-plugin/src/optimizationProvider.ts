import * as vscode from 'vscode';
import { MCPClient } from './mcpClient';

export class DcisionAIOptimizationProvider {
    private mcpClient: MCPClient;
    private context: vscode.ExtensionContext;
    private resultsPanel: vscode.WebviewPanel | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.mcpClient = new MCPClient(context);
    }

    async showOptimizationDialog(): Promise<void> {
        const problemDescription = await vscode.window.showInputBox({
            prompt: 'Describe your optimization problem',
            placeHolder: 'e.g., "I need to optimize production of 3 products with capacity constraints..."',
            validateInput: (value) => {
                if (!value || value.trim().length < 10) {
                    return 'Please provide a detailed problem description (at least 10 characters)';
                }
                return null;
            }
        });

        if (!problemDescription) {
            return;
        }

        await this.runOptimization(problemDescription, 'general');
    }

    async showPortfolioOptimizationDialog(): Promise<void> {
        const assets = await vscode.window.showInputBox({
            prompt: 'Enter assets (comma-separated)',
            placeHolder: 'e.g., AAPL, MSFT, GOOGL, JNJ, JPM',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please provide at least one asset';
                }
                return null;
            }
        });

        if (!assets) {
            return;
        }

        const budget = await vscode.window.showInputBox({
            prompt: 'Enter investment budget',
            placeHolder: 'e.g., 1000000',
            validateInput: (value) => {
                const num = parseFloat(value || '0');
                if (isNaN(num) || num <= 0) {
                    return 'Please enter a valid positive number';
                }
                return null;
            }
        });

        if (!budget) {
            return;
        }

        const problemDescription = `Portfolio optimization for assets: ${assets}. Budget: $${budget}. Maximize returns while keeping risk under 18%.`;
        await this.runOptimization(problemDescription, 'portfolio_optimization');
    }

    async showProductionPlanningDialog(): Promise<void> {
        const products = await vscode.window.showInputBox({
            prompt: 'Enter products (comma-separated)',
            placeHolder: 'e.g., Product A, Product B, Product C',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please provide at least one product';
                }
                return null;
            }
        });

        if (!products) {
            return;
        }

        const resources = await vscode.window.showInputBox({
            prompt: 'Enter resources/constraints',
            placeHolder: 'e.g., Machine 1: 40 hours, Machine 2: 60 hours',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please provide resource constraints';
                }
                return null;
            }
        });

        if (!resources) {
            return;
        }

        const problemDescription = `Production planning for products: ${products}. Resources: ${resources}. Maximize profit.`;
        await this.runOptimization(problemDescription, 'production_planning');
    }

    async showSupplyChainOptimizationDialog(): Promise<void> {
        const locations = await vscode.window.showInputBox({
            prompt: 'Enter supply chain locations (comma-separated)',
            placeHolder: 'e.g., Warehouse A, Warehouse B, Distribution Center',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please provide at least one location';
                }
                return null;
            }
        });

        if (!locations) {
            return;
        }

        const problemDescription = `Supply chain optimization for locations: ${locations}. Minimize total cost while meeting demand requirements.`;
        await this.runOptimization(problemDescription, 'supply_chain_optimization');
    }

    private async runOptimization(problemDescription: string, optimizationType: string): Promise<void> {
        const progressOptions: vscode.ProgressOptions = {
            location: vscode.ProgressLocation.Notification,
            title: "Running Optimization",
            cancellable: true
        };

        try {
            await vscode.window.withProgress(progressOptions, async (progress, token) => {
                progress.report({ message: "Classifying problem intent..." });
                
                // Step 1: Intent Classification
                const intentResult = await this.mcpClient.classifyIntent(problemDescription, optimizationType);
                if (token.isCancellationRequested) return;

                progress.report({ message: "Analyzing data..." });
                
                // Step 2: Data Analysis
                const dataResult = await this.mcpClient.analyzeData(problemDescription, intentResult);
                if (token.isCancellationRequested) return;

                progress.report({ message: "Building mathematical model..." });
                
                // Step 3: Model Building
                const modelResult = await this.mcpClient.buildModel(problemDescription, intentResult, dataResult);
                if (token.isCancellationRequested) return;

                progress.report({ message: "Solving optimization..." });
                
                // Step 4: Optimization Solving
                const solutionResult = await this.mcpClient.solveOptimization(problemDescription, intentResult, dataResult, modelResult);
                if (token.isCancellationRequested) return;

                progress.report({ message: "Generating results..." });
                
                // Display results
                await this.displayResults({
                    problemDescription,
                    intentResult,
                    dataResult,
                    modelResult,
                    solutionResult
                });
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Optimization failed: ${error}`);
        }
    }

    private async displayResults(results: any): Promise<void> {
        // Create or show results panel
        if (!this.resultsPanel) {
            this.resultsPanel = vscode.window.createWebviewPanel(
                'dcisionaiResults',
                'DcisionAI Optimization Results',
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            this.resultsPanel.onDidDispose(() => {
                this.resultsPanel = undefined;
            });
        }

        // Generate HTML content
        const html = this.generateResultsHTML(results);
        this.resultsPanel.webview.html = html;
        this.resultsPanel.reveal();
    }

    private generateResultsHTML(results: any): string {
        const solution = results.solutionResult?.result || {};
        const model = results.modelResult?.result || {};
        
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DcisionAI Optimization Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .header {
            border-bottom: 2px solid var(--vscode-panel-border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status.optimal {
            background-color: #28a745;
            color: white;
        }
        .status.feasible {
            background-color: #ffc107;
            color: black;
        }
        .status.error {
            background-color: #dc3545;
            color: white;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            background-color: var(--vscode-panel-background);
        }
        .section h3 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metric {
            padding: 15px;
            background-color: var(--vscode-editor-background);
            border-radius: 6px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        .metric-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-top: 5px;
        }
        .variables {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        .variable {
            padding: 10px;
            background-color: var(--vscode-editor-background);
            border-radius: 4px;
            text-align: center;
        }
        .variable-name {
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        .variable-value {
            font-size: 18px;
            margin-top: 5px;
        }
        .constraints {
            font-family: 'Courier New', monospace;
            background-color: var(--vscode-editor-background);
            padding: 15px;
            border-radius: 4px;
            white-space: pre-wrap;
        }
        .business-impact {
            background-color: var(--vscode-editor-background);
            padding: 15px;
            border-radius: 4px;
        }
        .business-impact h4 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 DcisionAI Optimization Results</h1>
        <p><strong>Problem:</strong> ${results.problemDescription}</p>
        <span class="status ${solution.status || 'error'}">${solution.status || 'Error'}</span>
    </div>

    <div class="section">
        <h3>📊 Solution Summary</h3>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">${solution.objective_value || 'N/A'}</div>
                <div class="metric-label">Objective Value</div>
            </div>
            <div class="metric">
                <div class="metric-value">${solution.solve_time ? (solution.solve_time * 1000).toFixed(1) + 'ms' : 'N/A'}</div>
                <div class="metric-label">Solve Time</div>
            </div>
            <div class="metric">
                <div class="metric-value">${model.variables ? model.variables.length : 'N/A'}</div>
                <div class="metric-label">Variables</div>
            </div>
            <div class="metric">
                <div class="metric-value">${model.constraints ? model.constraints.length : 'N/A'}</div>
                <div class="metric-label">Constraints</div>
            </div>
        </div>
    </div>

    ${solution.optimal_values ? `
    <div class="section">
        <h3>🎯 Optimal Solution</h3>
        <div class="variables">
            ${Object.entries(solution.optimal_values).map(([name, value]) => `
                <div class="variable">
                    <div class="variable-name">${name}</div>
                    <div class="variable-value">${typeof value === 'number' ? value.toFixed(3) : value}</div>
                </div>
            `).join('')}
        </div>
    </div>
    ` : ''}

    ${model.constraints ? `
    <div class="section">
        <h3>📋 Model Constraints</h3>
        <div class="constraints">${model.constraints.map((c: any) => c.expression + ' // ' + c.description).join('\n')}</div>
    </div>
    ` : ''}

    ${solution.business_impact ? `
    <div class="section">
        <h3>💰 Business Impact</h3>
        <div class="business-impact">
            ${Object.entries(solution.business_impact).map(([key, value]) => `
                <h4>${key.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${value}</p>
            `).join('')}
        </div>
    </div>
    ` : ''}

    <div class="section">
        <h3>🔬 Technical Details</h3>
        <p><strong>Model Type:</strong> ${model.model_type || 'Unknown'}</p>
        <p><strong>Complexity:</strong> ${model.model_complexity || 'Unknown'}</p>
        <p><strong>Estimated Solve Time:</strong> ${model.estimated_solve_time || 'Unknown'}</p>
        ${solution.recommendations ? `
        <h4>Recommendations:</h4>
        <ul>
            ${solution.recommendations.map((rec: string) => `<li>${rec}</li>`).join('')}
        </ul>
        ` : ''}
    </div>
</body>
</html>`;
    }

    async showResults(): Promise<void> {
        if (this.resultsPanel) {
            this.resultsPanel.reveal();
        } else {
            vscode.window.showInformationMessage('No optimization results available. Run an optimization first.');
        }
    }
}
