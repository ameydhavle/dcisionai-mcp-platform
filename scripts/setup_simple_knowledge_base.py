#!/usr/bin/env python3
"""
Simple Knowledge Base Setup for DcisionAI MCP Server
===================================================

This script creates a simple knowledge base by converting our training data
into a searchable format that can be used with the MCP server.
"""

import json
import boto3
from typing import Dict, List, Any
import argparse
from pathlib import Path

class SimpleKnowledgeBase:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        self.s3_client = boto3.client('s3')
        
    def create_knowledge_base(self, training_data_path: str, output_path: str):
        """Create a simple knowledge base from training data."""
        
        print("📚 Creating Simple Knowledge Base...")
        
        # Load training data
        training_examples = self._load_training_data(training_data_path)
        
        # Process examples into knowledge base format
        knowledge_base = self._process_training_examples(training_examples)
        
        # Save knowledge base
        self._save_knowledge_base(knowledge_base, output_path)
        
        # Upload to S3
        s3_key = self._upload_to_s3(output_path)
        
        print(f"✅ Knowledge Base created successfully!")
        print(f"Local file: {output_path}")
        print(f"S3 location: s3://dcisionai-training-bucket/{s3_key}")
        
        return {
            'local_path': output_path,
            's3_key': s3_key,
            'num_examples': len(knowledge_base['examples'])
        }
    
    def _load_training_data(self, training_data_path: str) -> List[Dict[str, Any]]:
        """Load training data from JSONL file."""
        
        examples = []
        
        with open(training_data_path, 'r') as f:
            for line in f:
                if line.strip():
                    example = json.loads(line)
                    examples.append(example)
        
        print(f"📖 Loaded {len(examples)} training examples")
        return examples
    
    def _process_training_examples(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process training examples into knowledge base format."""
        
        knowledge_base = {
            'metadata': {
                'created_at': '2025-10-17',
                'total_examples': len(examples),
                'description': 'DcisionAI Optimization Knowledge Base'
            },
            'examples': [],
            'categories': {
                'production_planning': [],
                'portfolio_optimization': [],
                'scheduling': [],
                'generic_optimization': []
            }
        }
        
        for i, example in enumerate(examples):
            # Extract problem and solution
            if 'messages' in example:
                # Converse API format
                user_msg = None
                assistant_msg = None
                
                for msg in example['messages']:
                    if msg['role'] == 'user':
                        user_msg = msg['content']
                    elif msg['role'] == 'assistant':
                        assistant_msg = msg['content']
                
                if user_msg and assistant_msg:
                    processed_example = self._process_example(user_msg, assistant_msg, i)
                    knowledge_base['examples'].append(processed_example)
                    
                    # Categorize example
                    self._categorize_example(processed_example, knowledge_base['categories'])
            
            elif 'prompt' in example and 'completion' in example:
                # Prompt/completion format
                processed_example = self._process_example(example['prompt'], example['completion'], i)
                knowledge_base['examples'].append(processed_example)
                
                # Categorize example
                self._categorize_example(processed_example, knowledge_base['categories'])
        
        print(f"📝 Processed {len(knowledge_base['examples'])} examples")
        return knowledge_base
    
    def _process_example(self, problem: str, solution: str, index: int) -> Dict[str, Any]:
        """Process a single example into knowledge base format."""
        
        # Extract key information
        problem_type = self._classify_problem_type(problem)
        variables = self._extract_variables(solution)
        constraints = self._extract_constraints(solution)
        objective = self._extract_objective(solution)
        
        return {
            'id': f'example_{index:04d}',
            'problem_type': problem_type,
            'problem_description': problem,
            'solution': solution,
            'variables': variables,
            'constraints': constraints,
            'objective': objective,
            'keywords': self._extract_keywords(problem + ' ' + solution),
            'complexity': self._assess_complexity(variables, constraints)
        }
    
    def _classify_problem_type(self, problem: str) -> str:
        """Classify the type of optimization problem."""
        
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ['production', 'factory', 'manufacturing', 'line']):
            return 'production_planning'
        elif any(word in problem_lower for word in ['portfolio', 'investment', 'asset', 'return']):
            return 'portfolio_optimization'
        elif any(word in problem_lower for word in ['schedule', 'task', 'resource', 'time']):
            return 'scheduling'
        else:
            return 'generic_optimization'
    
    def _extract_variables(self, solution: str) -> List[str]:
        """Extract variable names from solution."""
        
        import re
        # Look for patterns like x0, x1, x2, etc.
        variables = re.findall(r'\bx\d+\b', solution)
        return list(set(variables))
    
    def _extract_constraints(self, solution: str) -> List[str]:
        """Extract constraint expressions from solution."""
        
        import re
        # Look for constraint patterns
        constraints = re.findall(r'[^:]*<=[^:]*', solution)
        return constraints[:10]  # Limit to first 10 constraints
    
    def _extract_objective(self, solution: str) -> str:
        """Extract objective function from solution."""
        
        import re
        # Look for objective patterns
        objectives = re.findall(r'(?:Minimize|Maximize):[^\\n]*', solution)
        return objectives[0] if objectives else ''
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        
        import re
        
        # Common optimization keywords
        keywords = [
            'minimize', 'maximize', 'optimize', 'constraint', 'variable',
            'objective', 'linear', 'programming', 'production', 'portfolio',
            'scheduling', 'resource', 'capacity', 'demand', 'cost', 'profit'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _assess_complexity(self, variables: List[str], constraints: List[str]) -> str:
        """Assess the complexity of the optimization problem."""
        
        num_vars = len(variables)
        num_constraints = len(constraints)
        
        if num_vars <= 5 and num_constraints <= 5:
            return 'simple'
        elif num_vars <= 20 and num_constraints <= 20:
            return 'medium'
        else:
            return 'complex'
    
    def _categorize_example(self, example: Dict[str, Any], categories: Dict[str, List[str]]):
        """Categorize example into appropriate category."""
        
        problem_type = example['problem_type']
        if problem_type in categories:
            categories[problem_type].append(example['id'])
    
    def _save_knowledge_base(self, knowledge_base: Dict[str, Any], output_path: str):
        """Save knowledge base to file."""
        
        with open(output_path, 'w') as f:
            json.dump(knowledge_base, f, indent=2)
        
        print(f"💾 Saved knowledge base to {output_path}")
    
    def _upload_to_s3(self, local_path: str) -> str:
        """Upload knowledge base to S3."""
        
        s3_key = f"knowledge_base/dcisionai_optimization_kb.json"
        
        self.s3_client.upload_file(
            local_path, 
            'dcisionai-training-bucket', 
            s3_key
        )
        
        print(f"☁️ Uploaded to S3: s3://dcisionai-training-bucket/{s3_key}")
        return s3_key
    
    def search_knowledge_base(self, query: str, knowledge_base_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant examples."""
        
        # Load knowledge base
        with open(knowledge_base_path, 'r') as f:
            kb = json.load(f)
        
        # Simple keyword-based search
        query_lower = query.lower()
        results = []
        
        for example in kb['examples']:
            score = 0
            
            # Check problem description
            if any(word in example['problem_description'].lower() for word in query_lower.split()):
                score += 2
            
            # Check keywords
            for keyword in example['keywords']:
                if keyword in query_lower:
                    score += 1
            
            # Check problem type
            if any(word in query_lower for word in example['problem_type'].split('_')):
                score += 1
            
            if score > 0:
                results.append({
                    'example': example,
                    'score': score
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

def main():
    parser = argparse.ArgumentParser(description='Create simple knowledge base for DcisionAI')
    parser.add_argument('--training-data', 
                       default='training_data/train.jsonl',
                       help='Path to training data JSONL file')
    parser.add_argument('--output', 
                       default='knowledge_base/dcisionai_kb.json',
                       help='Output path for knowledge base')
    parser.add_argument('--search', 
                       help='Search query to test knowledge base')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize knowledge base
    kb = SimpleKnowledgeBase()
    
    # Create knowledge base
    result = kb.create_knowledge_base(args.training_data, args.output)
    
    if args.search:
        print(f"\n🔍 Searching for: {args.search}")
        results = kb.search_knowledge_base(args.search, args.output)
        
        print(f"Found {len(results)} relevant examples:")
        for i, result in enumerate(results):
            print(f"\n--- Result {i+1} (Score: {result['score']}) ---")
            print(f"Type: {result['example']['problem_type']}")
            print(f"Problem: {result['example']['problem_description'][:100]}...")
            print(f"Variables: {result['example']['variables']}")

if __name__ == "__main__":
    main()
