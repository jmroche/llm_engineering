#!/bin/bash


export KIWI_API_TOKEN=$(aws secretsmanager get-secret-value --secret-id tequila_kiwi_api_token --region us-east-1 | jq ".SecretString" | sed 's/"//g')

