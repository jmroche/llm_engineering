#!/bin/bash


export HF_API_TOKEN=$(aws secretsmanager get-secret-value --secret-id HUGGINGFACE_API_TOKEN --region us-east-1 | jq ".SecretString" | sed 's/"//g')

