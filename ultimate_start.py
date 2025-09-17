import os
import time
import subprocess
import webbrowser
import sys
import requests

# Set environment variables
os.environ['NODE_ENV'] = 'development'
os.environ['PORT_FRONTEND'] = '3000'
os.environ['PORT_BACKEND'] = '4000'
os.environ['PORT_ARYAN'] = '5000'
os.environ['ASRS_HOST'] = '127.0.0.1'
os.environ['ASRS_PORT'] = '8888'
os.environ['OPCUA_SERVER_URL'] = 'opc.tcp://localhost:4840'

def check_service(url, name):
    for attempt in range(5):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {name} is responding")
                return True
        except:
            pass
        time.sleep(2)
    print(f"❌ {name} not responding")
    return False

def start_service(name, cmd, cwd='.'): 
    print(f"Starting {name}...")
    try:
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(cmd, shell=True, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            process = subprocess.Popen(cmd, shell=True, cwd=cwd)
        print(f"✅ {name} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🚀 FSMFINAL COMPLETE STARTUP")
    print("=" * 50)
    
    # Setup database first
    print("Setting up database...")
    subprocess.run([sys.executable, "setup_db.py"])
    
    processes = []
    
    # Start ASRS Control
    p1 = start_service("ASRS Control", "python asrs_control.py")
    if p1: processes.append(p1)
    time.sleep(4)
    
    # Start Aryan Service
    p2 = start_service("Aryan Service", "python aryan.py")
    if p2: processes.append(p2)
    time.sleep(4)
    
    # Start Backend
    p3 = start_service("Backend API", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\backend")
    if p3: processes.append(p3)
    time.sleep(10)
    
    # Start Frontend
    p4 = start_service("Frontend UI", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\frontend")
    if p4: processes.append(p4)
    time.sleep(8)
    
    print("\n🔍 Testing services...")
    
    services = [
        ("http://localhost:4000/health", "Backend API"),
        ("http://localhost:5000/health", "Aryan Service"),
        ("http://localhost:3000", "Frontend")
    ]
    
    all_good = True
    for url, name in services:
        if not check_service(url, name):
            all_good = False
    
    if all_good:
        print("\n✅ ALL SERVICES RUNNING!")
        print("🌐 Opening http://localhost:3000")
        webbrowser.open('http://localhost:3000')
        
        print("\n📋 Service URLs:")
        print("   Frontend:    http://localhost:3000")
        print("   Backend API: http://localhost:4000")
        print("   Aryan:       http://localhost:5000")
        print("   ASRS Control: TCP port 8888")
        
        print("\n🎯 ASRS SYSTEM READY!")
        print("   - Add/remove items from web interface")
        print("   - Orders will trigger ASRS movements")
        print("   - Check console for ASRS commands")
        
    else:
        print("\n❌ Some services failed to start")
        print("Check individual service windows for errors")
    
    print("\n🔄 Press Enter to stop all services...")
    input()
    
    print("🛑 Stopping services...")
    for p in processes:
        if p.poll() is None:
            p.terminate()
    print("✅ All services stopped")

if __name__ == "__main__":
    main()
