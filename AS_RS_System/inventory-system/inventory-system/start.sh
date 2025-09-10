#!/bin/bash

echo "Starting Inventory Management System..."

# Start backend server
echo "Starting backend server..."
cd backend
node server.js &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
curl -s http://localhost:5001 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend server is running on port 5001"
else
    echo "❌ Backend server failed to start"
    exit 1
fi

# Start frontend (optional)
echo "Starting frontend dashboard..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend dashboard starting on port 5173"

# Open ecommerce store
echo "🛒 Opening ecommerce store..."
open ../ecommerce/index.html

echo ""
echo "🎉 All services started!"
echo "📊 Dashboard: http://localhost:5173"
echo "🛒 Ecommerce: file://$(pwd)/../ecommerce/index.html"
echo "🔧 API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
