import os
import time
import subprocess
import webbrowser
import sys

# Set environment variables
os.environ['NODE_ENV'] = 'development'
os.environ['PORT_FRONTEND'] = '3000'
os.environ['PORT_BACKEND'] = '4000'
os.environ['PORT_ARYAN'] = '5000'
os.environ['ASRS_HOST'] = '127.0.0.1'
os.environ['ASRS_PORT'] = '8888'
os.environ['OPCUA_SERVER_URL'] = 'opc.tcp://localhost:4840'

def start_service(name, cmd, cwd='.'): 
    print(f"Starting {name}...")
    try:
        process = subprocess.Popen(cmd, shell=True, cwd=cwd)
        print(f"✅ {name} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🚀 FSMFINAL STARTUP SEQUENCE")
    print("=" * 40)
    
    processes = []
    
    # Start ASRS Control
    p1 = start_service("ASRS Control", "python asrs_control.py")
    if p1: processes.append(p1)
    time.sleep(3)
    
    # Start Aryan Service
    p2 = start_service("Aryan Service", "python aryan.py")
    if p2: processes.append(p2)
    time.sleep(3)
    
    # Start Backend
    p3 = start_service("Backend API", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\backend")
    if p3: processes.append(p3)
    time.sleep(8)
    
    # Start Frontend
    p4 = start_service("Frontend UI", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\frontend")
    if p4: processes.append(p4)
    time.sleep(8)
    
    print("\n✅ All services started!")
    print("🌐 Opening http://localhost:3000")
    webbrowser.open('http://localhost:3000')
    
    print("\n📋 Service URLs:")
    print("   Frontend:  http://localhost:3000")
    print("   Backend:   http://localhost:4000") 
    print("   Aryan:     http://localhost:5000")
    print("   ASRS API:  http://localhost:4001")
    print("\n🔄 Services running. Press Ctrl+C to stop all.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
