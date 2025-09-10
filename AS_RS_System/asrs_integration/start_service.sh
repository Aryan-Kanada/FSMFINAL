#!/bin/bash
# Start ASRS Integration Service

echo "🚀 Starting ASRS Integration Service..."

# Activate virtual environment
source asrs_env/bin/activate

# Start the service
python main_service.py
