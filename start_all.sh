#!/usr/bin/env bash

# Exit on error
set -e

# 1. Start AS/RS Integration Service
echo “Starting AS/RS Integration Service…”
cd AS_RS_System/asrs_integration
# Activate virtualenv if needed
source ../../.venv/Scripts/activate
nohup python main_service.py > asrs_integration.log 2>&1 &

# 2. Start Backend API
echo “Starting Backend API…”
cd ../../AS_RS_System/inventory-system/backend
npm install
npm run dev > backend.log 2>&1 &

# 3. Start Frontend UI
echo “Starting Frontend UI…”
cd ../frontend
npm install
npm run dev > frontend.log 2>&1 &

echo “All services started. Frontend: http://localhost:5173  Backend: http://localhost:4000/api”
