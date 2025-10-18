#!/usr/bin/env python3
"""
Setup Bedrock Knowledge Base with DcisionAI Training Data
========================================================

This script creates a Bedrock Knowledge Base using our optimization training data
as the knowledge source, which can be used to enhance the MCP server responses.
"""

import boto3
import json
import time
from typing import Dict, List, Any
import argparse

class BedrockKnowledgeBaseSetup:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        self.bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name=region)
        self.s3_client = boto3.client('s3')
        
    def create_knowledge_base(self, 
                            knowledge_base_name: str,
                            data_source_s3_uri: str,
                            embedding_model_id: str = 'amazon.titan-embed-text-v1'):
        """Create a Bedrock Knowledge Base."""
        
        try:
            print(f"Creating Knowledge Base: {knowledge_base_name}")
            
            # Extract bucket and prefix from S3 URI
            s3_uri_parts = data_source_s3_uri.replace('s3://', '').split('/', 1)
            bucket = s3_uri_parts[0]
            prefix = s3_uri_parts[1] if len(s3_uri_parts) > 1 else ''
            
            # Create knowledge base directly
            response = self.bedrock_agent_client.create_knowledge_base(
                name=knowledge_base_name,
                description="Knowledge base for DcisionAI optimization expertise",
                roleArn=self._get_or_create_knowledge_base_role(),
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/{embedding_model_id}'
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': self._get_or_create_opensearch_collection(),
                        'vectorIndexName': f"{knowledge_base_name}-index",
                        'fieldMapping': {
                            'vectorField': 'bedrock-knowledge-base-default-vector',
                            'textField': 'AMAZON_BEDROCK_TEXT_CHUNK',
                            'metadataField': 'AMAZON_BEDROCK_METADATA'
                        }
                    }
                }
            )
            
            knowledge_base_id = response['knowledgeBase']['knowledgeBaseId']
            print(f"✅ Knowledge Base created: {knowledge_base_id}")
            
            # Create data source
            data_source_id = self._create_data_source(
                knowledge_base_id,
                knowledge_base_name, 
                data_source_s3_uri
            )
            
            # Start ingestion job
            ingestion_job_id = self._start_ingestion_job(
                knowledge_base_id,
                data_source_id
            )
            
            print(f"✅ Knowledge Base setup completed!")
            print(f"Knowledge Base ID: {knowledge_base_id}")
            print(f"Data Source ID: {data_source_id}")
            print(f"Ingestion Job ID: {ingestion_job_id}")
            
            return {
                'knowledge_base_id': knowledge_base_id,
                'data_source_id': data_source_id,
                'ingestion_job_id': ingestion_job_id
            }
            
        except Exception as e:
            print(f"❌ Error creating Knowledge Base: {e}")
            raise
    
    def _create_vector_store(self, vector_store_name: str) -> str:
        """Create a vector store for the knowledge base."""
        
        print(f"Creating vector store: {vector_store_name}")
        
        response = self.bedrock_agent_client.create_vector_store(
            name=vector_store_name,
            description="Vector store for DcisionAI optimization knowledge base"
        )
        
        vector_store_id = response['vectorStoreId']
        print(f"✅ Vector store created: {vector_store_id}")
        
        return vector_store_id
    
    def _create_data_source(self, 
                          knowledge_base_name: str, 
                          data_source_s3_uri: str, 
                          vector_store_id: str) -> str:
        """Create a data source for the knowledge base."""
        
        print(f"Creating data source for: {data_source_s3_uri}")
        
        # Extract bucket and prefix from S3 URI
        s3_uri_parts = data_source_s3_uri.replace('s3://', '').split('/', 1)
        bucket = s3_uri_parts[0]
        prefix = s3_uri_parts[1] if len(s3_uri_parts) > 1 else ''
        
        response = self.bedrock_agent_client.create_data_source(
            name=f"{knowledge_base_name}-data-source",
            description="Data source containing DcisionAI optimization examples",
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{bucket}',
                    'inclusionPrefixes': [prefix] if prefix else []
                }
            },
            vectorStoreId=vector_store_id
        )
        
        data_source_id = response['dataSourceId']
        print(f"✅ Data source created: {data_source_id}")
        
        return data_source_id
    
    def _create_knowledge_base_config(self, 
                                    knowledge_base_name: str,
                                    embedding_model_id: str,
                                    vector_store_id: str) -> str:
        """Create the knowledge base configuration."""
        
        print(f"Creating knowledge base configuration")
        
        response = self.bedrock_agent_client.create_knowledge_base(
            name=knowledge_base_name,
            description="Knowledge base for DcisionAI optimization expertise",
            roleArn=self._get_or_create_knowledge_base_role(),
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/{embedding_model_id}'
                }
            },
            storageConfiguration={
                'type': 'VECTOR_STORE',
                'vectorStoreConfiguration': {
                    'vectorStoreId': vector_store_id
                }
            }
        )
        
        knowledge_base_id = response['knowledgeBaseId']
        print(f"✅ Knowledge base created: {knowledge_base_id}")
        
        return knowledge_base_id
    
    def _start_ingestion_job(self, knowledge_base_id: str, data_source_id: str) -> str:
        """Start the ingestion job to process the data source."""
        
        print(f"Starting ingestion job")
        
        response = self.bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            description="Ingest DcisionAI optimization training data"
        )
        
        ingestion_job_id = response['ingestionJobId']
        print(f"✅ Ingestion job started: {ingestion_job_id}")
        
        return ingestion_job_id
    
    def _get_or_create_knowledge_base_role(self) -> str:
        """Get or create IAM role for Knowledge Base."""
        
        iam_client = boto3.client('iam')
        role_name = 'BedrockKnowledgeBaseRole'
        
        try:
            # Try to get existing role
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"Using existing role: {role_arn}")
            return role_arn
            
        except iam_client.exceptions.NoSuchEntityException:
            # Create new role
            print(f"Creating new IAM role: {role_name}")
            
            # Trust policy for Bedrock
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "bedrock.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # Create role
            iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Bedrock Knowledge Base'
            )
            
            # Attach policies
            policies = [
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
            
            for policy_arn in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            # Get role ARN
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            
            print(f"✅ Created role: {role_arn}")
            return role_arn
    
    def monitor_ingestion_job(self, knowledge_base_id: str, ingestion_job_id: str):
        """Monitor the ingestion job progress."""
        
        print(f"🔍 Monitoring ingestion job: {ingestion_job_id}")
        
        while True:
            try:
                response = self.bedrock_agent_client.get_ingestion_job(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=ingestion_job_id
                )
                
                status = response['ingestionJob']['status']
                print(f"Status: {status}")
                
                if status in ['COMPLETE', 'FAILED', 'CANCELLED']:
                    if status == 'COMPLETE':
                        print("✅ Ingestion job completed successfully!")
                        print(f"Documents processed: {response['ingestionJob'].get('statistics', {}).get('numberOfDocumentsScanned', 'N/A')}")
                    else:
                        print(f"❌ Job {status.lower()}")
                        if 'failureReasons' in response['ingestionJob']:
                            print(f"Failure reasons: {response['ingestionJob']['failureReasons']}")
                    break
                
                # Wait before checking again
                time.sleep(30)
                
            except Exception as e:
                print(f"Error monitoring job: {e}")
                break
    
    def query_knowledge_base(self, knowledge_base_id: str, query: str):
        """Query the knowledge base to test it."""
        
        try:
            print(f"🔍 Querying knowledge base: {query}")
            
            response = self.bedrock_agent_runtime_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            )
            
            print(f"✅ Found {len(response['retrievalResults'])} results")
            
            for i, result in enumerate(response['retrievalResults'][:3]):
                print(f"\n--- Result {i+1} ---")
                print(f"Score: {result['score']}")
                print(f"Content: {result['content']['text'][:200]}...")
            
            return response
            
        except Exception as e:
            print(f"❌ Error querying knowledge base: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Setup Bedrock Knowledge Base with DcisionAI training data')
    parser.add_argument('--knowledge-base-name', 
                       default='dcisionai-optimization-knowledge-base',
                       help='Name for the knowledge base')
    parser.add_argument('--data-source-s3', 
                       default='s3://dcisionai-training-bucket/training_data/',
                       help='S3 URI for training data')
    parser.add_argument('--embedding-model', 
                       default='amazon.titan-embed-text-v1',
                       help='Embedding model for vectorization')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor ingestion job progress')
    parser.add_argument('--test-query', 
                       help='Test query to run against the knowledge base')
    
    args = parser.parse_args()
    
    # Initialize knowledge base setup
    kb_setup = BedrockKnowledgeBaseSetup()
    
    # Create knowledge base
    result = kb_setup.create_knowledge_base(
        knowledge_base_name=args.knowledge_base_name,
        data_source_s3_uri=args.data_source_s3,
        embedding_model_id=args.embedding_model
    )
    
    if args.monitor:
        kb_setup.monitor_ingestion_job(
            result['knowledge_base_id'],
            result['ingestion_job_id']
        )
    
    if args.test_query:
        kb_setup.query_knowledge_base(
            result['knowledge_base_id'],
            args.test_query
        )
    
    print(f"\n🎯 Knowledge Base Setup Complete!")
    print(f"Knowledge Base ID: {result['knowledge_base_id']}")
    print(f"Use this ID to integrate with your MCP server")

if __name__ == "__main__":
    main()
