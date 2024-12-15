#!/bin/bash


export OPEN_AI_API_TOKEN=$(aws secretsmanager get-secret-value --secret-id OPENAI_API_TOKEN --region us-east-1 | jq ".SecretString" | sed 's/"//g')

