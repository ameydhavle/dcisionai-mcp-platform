#!/usr/bin/env python3
"""
Convert S3 Training Data to AWS Bedrock Fine-Tuning Format
==========================================================

This script converts our S3 optimization training data into the format required
for AWS Bedrock fine-tuning, specifically for Claude 3 Haiku using the Converse API format.
"""

import json
import boto3
import random
from typing import Dict, List, Any
from pathlib import Path
import argparse

class TrainingDataConverter:
    def __init__(self, s3_bucket: str, output_bucket: str):
        self.s3_bucket = s3_bucket
        self.output_bucket = output_bucket
        self.s3_client = boto3.client('s3')
        
        # System prompt for optimization expert
        self.system_prompt = """You are an expert optimization consultant specializing in mathematical modeling and constraint programming. You excel at converting business problems into precise mathematical formulations.

Your approach follows a systematic 7-step process:
1. Decision Analysis: Identify key decisions to be made
2. Constraint Analysis: Identify limitations and requirements  
3. Objective Analysis: Determine optimization goal
4. Variable Design: Define decision variables
5. Constraint Formulation: Create mathematical constraints
6. Objective Formulation: Create mathematical objective
7. Validation: Verify all variables are used and model is consistent

Always provide clear, step-by-step reasoning and mathematically sound formulations."""
    
    def generate_problem_description(self, model_data: Dict[str, Any]) -> str:
        """Generate natural language problem description from JSON model."""
        
        # Extract basic info
        title = model_data.get('title', 'Optimization Problem')
        category = model_data.get('category', 'linear')
        variables = model_data.get('variables', [])
        constraints = model_data.get('constraints', [])
        objective = model_data.get('objective', {})
        
        # Generate contextual description based on title and structure
        if 'production' in title.lower():
            return self._generate_production_problem(variables, constraints, objective)
        elif 'portfolio' in title.lower():
            return self._generate_portfolio_problem(variables, constraints, objective)
        elif 'scheduling' in title.lower():
            return self._generate_scheduling_problem(variables, constraints, objective)
        else:
            return self._generate_generic_problem(variables, constraints, objective)
    
    def _generate_production_problem(self, variables: List, constraints: List, objective: Dict) -> str:
        """Generate production planning problem description."""
        
        num_lines = len(variables)
        direction = objective.get('direction', 'minimize')
        
        # Extract coefficients from objective
        obj_expr = objective.get('expression', '')
        costs = self._extract_coefficients(obj_expr)
        
        # Extract capacity constraints
        capacities = []
        for constraint in constraints:
            if '<=' in constraint.get('expression', ''):
                capacities.append(constraint.get('rhs', 100))
        
        problem = f"I manage a factory with {num_lines} production lines. "
        
        for i, (var, cost, capacity) in enumerate(zip(variables, costs, capacities)):
            problem += f"Line {i+1} can produce {capacity} units/hour at ${cost}/hour. "
        
        problem += f"I need to {direction} total production cost while meeting demand requirements."
        
        return problem
    
    def _generate_portfolio_problem(self, variables: List, constraints: List, objective: Dict) -> str:
        """Generate portfolio optimization problem description."""
        
        num_assets = len(variables)
        direction = objective.get('direction', 'maximize')
        
        problem = f"I have a portfolio with {num_assets} investment options. "
        problem += f"I want to {direction} expected return while managing risk. "
        problem += "Each asset has different expected returns and risk levels. "
        problem += "I need to allocate my budget optimally across all assets."
        
        return problem
    
    def _generate_scheduling_problem(self, variables: List, constraints: List, objective: Dict) -> str:
        """Generate scheduling problem description."""
        
        num_tasks = len(variables)
        direction = objective.get('direction', 'minimize')
        
        problem = f"I need to schedule {num_tasks} tasks across available resources. "
        problem += f"I want to {direction} total completion time while respecting "
        problem += "resource constraints and task dependencies."
        
        return problem
    
    def _generate_generic_problem(self, variables: List, constraints: List, objective: Dict) -> str:
        """Generate generic optimization problem description."""
        
        num_vars = len(variables)
        num_constraints = len(constraints)
        direction = objective.get('direction', 'optimize')
        
        problem = f"I have an optimization problem with {num_vars} decision variables "
        problem += f"and {num_constraints} constraints. "
        problem += f"I want to {direction} the objective function while satisfying all constraints."
        
        return problem
    
    def _extract_coefficients(self, expression: str) -> List[float]:
        """Extract coefficients from mathematical expression."""
        # Simple coefficient extraction (can be enhanced)
        import re
        
        # Find patterns like "45*x1" or "9*x0"
        pattern = r'(\d+(?:\.\d+)?)\*x\d+'
        matches = re.findall(pattern, expression)
        
        return [float(match) for match in matches]
    
    def create_solution_response(self, model_data: Dict[str, Any]) -> str:
        """Create step-by-step solution response."""
        
        variables = model_data.get('variables', [])
        constraints = model_data.get('constraints', [])
        objective = model_data.get('objective', {})
        
        response = "I'll analyze this optimization problem step by step.\n\n"
        
        # Step 1: Decision Analysis
        response += "**Step 1 - Decision Analysis**: "
        response += f"The key decisions involve {len(variables)} variables: "
        var_names = [var.get('name', f'x{i}') for i, var in enumerate(variables)]
        response += f"{', '.join(var_names)}.\n\n"
        
        # Step 2: Constraint Analysis
        response += "**Step 2 - Constraint Analysis**: "
        response += f"The problem has {len(constraints)} constraints that limit the solution space.\n\n"
        
        # Step 3: Objective Analysis
        direction = objective.get('direction', 'optimize')
        response += f"**Step 3 - Objective Analysis**: The goal is to {direction} the objective function.\n\n"
        
        # Step 4: Variable Design
        response += "**Step 4 - Variable Design**:\n"
        for i, var in enumerate(variables):
            name = var.get('name', f'x{i}')
            var_type = var.get('type', 'continuous')
            bounds = var.get('bounds', [0, None])
            response += f"- {name}: {var_type} variable"
            if bounds[0] is not None:
                response += f" with lower bound {bounds[0]}"
            if bounds[1] is not None:
                response += f" and upper bound {bounds[1]}"
            response += "\n"
        response += "\n"
        
        # Step 5: Constraint Formulation
        response += "**Step 5 - Constraint Formulation**:\n"
        for i, constraint in enumerate(constraints):
            expr = constraint.get('expression', '')
            op = constraint.get('operator', '<=')
            rhs = constraint.get('rhs', 0)
            response += f"- {expr} {op} {rhs}\n"
        response += "\n"
        
        # Step 6: Objective Formulation
        response += "**Step 6 - Objective Formulation**:\n"
        direction = objective.get('direction', 'optimize')
        expression = objective.get('expression', '')
        response += f"{direction.capitalize()}: {expression}\n\n"
        
        # Step 7: Validation
        response += "**Step 7 - Validation**: All variables are used in the constraints and objective function.\n\n"
        
        # Mathematical Model
        response += "**Mathematical Model**:\n```\n"
        response += f"{direction.capitalize()}: {expression}\n"
        response += "Subject to:\n"
        for constraint in constraints:
            expr = constraint.get('expression', '')
            op = constraint.get('operator', '<=')
            rhs = constraint.get('rhs', 0)
            response += f"{expr} {op} {rhs}\n"
        
        # Add non-negativity constraints
        var_names = [var.get('name', f'x{i}') for var in variables]
        response += f"{', '.join(var_names)} >= 0\n"
        response += "```"
        
        return response
    
    def convert_json_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single JSON model to training format."""
        
        problem_description = self.generate_problem_description(model_data)
        solution_response = self.create_solution_response(model_data)
        
        # For Nova models, use prompt/completion format instead of messages
        return {
            "prompt": f"{self.system_prompt}\n\nUser: {problem_description}",
            "completion": solution_response
        }
    
    def download_json_models(self) -> List[Dict[str, Any]]:
        """Download all JSON models from S3."""
        
        models = []
        
        try:
            # List all JSON files in the optimization_models_json folder
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix='trainingdata/optimization_models_json/'
            )
            
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.json'):
                    # Download and parse JSON
                    response = self.s3_client.get_object(
                        Bucket=self.s3_bucket,
                        Key=obj['Key']
                    )
                    
                    content = response['Body'].read().decode('utf-8')
                    model_data = json.loads(content)
                    models.append(model_data)
                    
                    print(f"Downloaded: {obj['Key']}")
            
        except Exception as e:
            print(f"Error downloading models: {e}")
        
        return models
    
    def create_training_dataset(self, models: List[Dict[str, Any]], output_file: str):
        """Create training dataset in JSONL format."""
        
        training_examples = []
        
        for model in models:
            try:
                training_example = self.convert_json_model(model)
                training_examples.append(training_example)
            except Exception as e:
                print(f"Error converting model {model.get('id', 'unknown')}: {e}")
                continue
        
        # Write to JSONL file
        with open(output_file, 'w') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"Created training dataset with {len(training_examples)} examples")
        return training_examples
    
    def split_train_validation(self, training_examples: List[Dict[str, Any]], 
                             train_ratio: float = 0.9) -> tuple:
        """Split data into training and validation sets."""
        
        random.shuffle(training_examples)
        split_idx = int(len(training_examples) * train_ratio)
        
        train_data = training_examples[:split_idx]
        val_data = training_examples[split_idx:]
        
        return train_data, val_data
    
    def upload_to_s3(self, local_file: str, s3_key: str):
        """Upload file to S3."""
        
        try:
            self.s3_client.upload_file(local_file, self.output_bucket, s3_key)
            print(f"Uploaded {local_file} to s3://{self.output_bucket}/{s3_key}")
        except Exception as e:
            print(f"Error uploading to S3: {e}")

def main():
    parser = argparse.ArgumentParser(description='Convert S3 training data to AWS Bedrock format')
    parser.add_argument('--input-bucket', default='dcisionai-slm-training-data',
                       help='S3 bucket containing training data')
    parser.add_argument('--output-bucket', default='dcisionai-training-bucket',
                       help='S3 bucket for output training data')
    parser.add_argument('--output-dir', default='./training_data',
                       help='Local output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Initialize converter
    converter = TrainingDataConverter(args.input_bucket, args.output_bucket)
    
    print("Downloading JSON models from S3...")
    models = converter.download_json_models()
    
    if not models:
        print("No models found. Exiting.")
        return
    
    print(f"Downloaded {len(models)} models")
    
    # Convert to training format
    print("Converting to training format...")
    training_examples = converter.create_training_dataset(
        models, 
        f"{args.output_dir}/training_data.jsonl"
    )
    
    # Split into train/validation
    train_data, val_data = converter.split_train_validation(training_examples)
    
    # Save training data
    with open(f"{args.output_dir}/train.jsonl", 'w') as f:
        for example in train_data:
            f.write(json.dumps(example) + '\n')
    
    # Save validation data
    with open(f"{args.output_dir}/validation.jsonl", 'w') as f:
        for example in val_data:
            f.write(json.dumps(example) + '\n')
    
    print(f"Training examples: {len(train_data)}")
    print(f"Validation examples: {len(val_data)}")
    
    # Upload to S3
    print("Uploading to S3...")
    converter.upload_to_s3(f"{args.output_dir}/train.jsonl", "training_data/train.jsonl")
    converter.upload_to_s3(f"{args.output_dir}/validation.jsonl", "training_data/validation.jsonl")
    
    # Create metadata
    metadata = {
        "total_examples": len(training_examples),
        "train_examples": len(train_data),
        "validation_examples": len(val_data),
        "source_bucket": args.input_bucket,
        "conversion_date": "2025-10-17",
        "model_type": "claude-3-haiku",
        "format": "converse-api"
    }
    
    with open(f"{args.output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    converter.upload_to_s3(f"{args.output_dir}/metadata.json", "training_data/metadata.json")
    
    print("Training data conversion complete!")
    print(f"Files created:")
    print(f"- {args.output_dir}/train.jsonl")
    print(f"- {args.output_dir}/validation.jsonl")
    print(f"- {args.output_dir}/metadata.json")

if __name__ == "__main__":
    main()