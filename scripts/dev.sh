#!/bin/bash
# Mithrava Development Server - Network Accessible

echo ""
echo "  ============================================================"
echo "   Mithrava — Development Server (Network Accessible)"
echo "  ============================================================"
echo ""

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "  Your Local IP: $LOCAL_IP"
echo ""
echo "  Access from any device on your WiFi:"
echo "    Phone/Tablet:  http://$LOCAL_IP:3000"
echo "    This PC:       http://localhost:3000"
echo ""
echo "  API Docs: http://$LOCAL_IP:8000/docs"
echo ""
echo "  ============================================================"
echo ""

# Start backend
echo "[1/2] Starting Backend..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Start frontend
echo "[2/2] Starting Frontend..."
cd frontend
npm run dev -- -H 0.0.0.0 &
FRONTEND_PID=$!
cd ..

echo ""
echo "  Both servers started!"
echo "  Press Ctrl+C to stop all servers."
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
