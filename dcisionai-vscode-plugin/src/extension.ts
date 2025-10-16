import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { DcisionAIOptimizationProvider } from './optimizationProvider';
import { MCPClient } from './mcpClient';

export function activate(context: vscode.ExtensionContext) {
    console.log('DcisionAI Optimization extension is now active!');

    // Initialize the optimization provider
    const optimizationProvider = new DcisionAIOptimizationProvider(context);
    
    // Initialize MCP client
    const mcpClient = new MCPClient(context);

    // Register MCP server definition provider
    const didChangeEmitter = new vscode.EventEmitter<void>();
    
    const mcpProvider = vscode.lm.registerMcpServerDefinitionProvider('dcisionaiProvider', {
        onDidChangeMcpServerDefinitions: didChangeEmitter.event,
        provideMcpServerDefinitions: async () => {
            const config = vscode.workspace.getConfiguration('dcisionai');
            const mcpServerPath = config.get<string>('mcpServerPath');
            
            if (!mcpServerPath) {
                // Try to find the MCP server in the workspace
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (workspaceFolders) {
                    for (const folder of workspaceFolders) {
                        const possiblePath = path.join(folder.uri.fsPath, 'mcp-server', 'src');
                        if (fs.existsSync(possiblePath)) {
                            return [
                                new vscode.McpStdioServerDefinition(
                                    'dcisionai-optimization',
                                    'python',
                                    ['-m', 'dcisionai_mcp_server'],
                                    { cwd: possiblePath },
                                    '1.0.0'
                                )
                            ];
                        }
                    }
                }
                return [];
            }

            return [
                new vscode.McpStdioServerDefinition(
                    'dcisionai-optimization',
                    'python',
                    ['-m', 'dcisionai_mcp_server'],
                    { cwd: mcpServerPath },
                    '1.0.0'
                )
            ];
        },
        resolveMcpServerDefinition: async (server: vscode.McpServerDefinition) => {
            const config = vscode.workspace.getConfiguration('dcisionai');
            
            // Check if AWS credentials are configured
            const awsAccessKeyId = config.get<string>('awsAccessKeyId');
            const awsSecretAccessKey = config.get<string>('awsSecretAccessKey');
            
            if (!awsAccessKeyId || !awsSecretAccessKey) {
                const result = await vscode.window.showWarningMessage(
                    'AWS credentials are required for DcisionAI Optimization. Would you like to configure them now?',
                    'Configure',
                    'Cancel'
                );
                
                if (result === 'Configure') {
                    await vscode.commands.executeCommand('workbench.action.openSettings', 'dcisionai');
                    return undefined; // Don't start the server until credentials are configured
                }
            }

            return server;
        }
    });

    // Register commands
    const optimizeCommand = vscode.commands.registerCommand('dcisionai.optimize', async () => {
        await optimizationProvider.showOptimizationDialog();
    });

    const portfolioOptimizeCommand = vscode.commands.registerCommand('dcisionai.portfolioOptimize', async () => {
        await optimizationProvider.showPortfolioOptimizationDialog();
    });

    const productionPlanCommand = vscode.commands.registerCommand('dcisionai.productionPlan', async () => {
        await optimizationProvider.showProductionPlanningDialog();
    });

    const supplyChainOptimizeCommand = vscode.commands.registerCommand('dcisionai.supplyChainOptimize', async () => {
        await optimizationProvider.showSupplyChainOptimizationDialog();
    });

    const showResultsCommand = vscode.commands.registerCommand('dcisionai.showResults', async () => {
        await optimizationProvider.showResults();
    });

    // Register status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(graph) DcisionAI";
    statusBarItem.tooltip = "DcisionAI Optimization - Click to optimize";
    statusBarItem.command = 'dcisionai.optimize';
    statusBarItem.show();

    // Auto-start MCP server if configured
    const autoStart = vscode.workspace.getConfiguration('dcisionai').get<boolean>('autoStart');
    if (autoStart) {
        // The MCP server will be started automatically when needed
        vscode.window.showInformationMessage('DcisionAI Optimization extension loaded. MCP server will start when needed.');
    }

    // Add to subscriptions
    context.subscriptions.push(
        mcpProvider,
        optimizeCommand,
        portfolioOptimizeCommand,
        productionPlanCommand,
        supplyChainOptimizeCommand,
        showResultsCommand,
        statusBarItem,
        didChangeEmitter
    );
}

export function deactivate() {
    console.log('DcisionAI Optimization extension is now deactivated!');
}
