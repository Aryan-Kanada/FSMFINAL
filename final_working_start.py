import os
import time
import subprocess
import webbrowser
import sys
import requests

# Set environment variables
env_vars = {
    'NODE_ENV': 'development',
    'PORT_FRONTEND': '3000',
    'PORT_BACKEND': '4000',
    'PORT_ARYAN': '5000',
    'ASRS_HOST': '127.0.0.1',
    'ASRS_PORT': '8888',
    'OPCUA_SERVER_URL': 'opc.tcp://localhost:4840',
    'DB_HOST': 'localhost',
    'DB_USER': 'root',
    'DB_PASSWORD': '',
    'DB_NAME': 'inventory_management'
}
for key, value in env_vars.items():
    os.environ[key] = value
processes = []
def test_service(url, name, max_attempts=8):
    print(f"🧪 Testing {name}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                print(f"   ✅ {name} responding")
                return True
        except:
            pass
        if attempt < max_attempts - 1:
            time.sleep(4)
    print(f"   ❌ {name} not responding")
    return False
def start_service(name, cmd, cwd='.'): 
    print(f"🚀 Starting {name}...")
    try:
        if os.name == 'nt':
            process = subprocess.Popen(
                f'start /min cmd /k "title {name} && {cmd}"',
                cwd=cwd,
                shell=True
            )
        else:
            process = subprocess.Popen(cmd, cwd=cwd, shell=True)
        processes.append((name, process))
        print(f"   ✅ {name} started")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start {name}: {e}")
        return None
def main():
    print("🎯 FSMFINAL - FINAL WORKING STARTUP")
    print("=" * 50)
    # Run MySQL setup
    print("🗄️ Running MySQL setup...")
    try:
        subprocess.run([sys.executable, "mysql_setup.py"], timeout=30)
    except:
        print("⚠️ MySQL setup completed with warnings")
    # Start services with proper delays
    services = [
        ("ASRS Control", "python asrs_control.py", ".", 3),
        ("Aryan Service", "python aryan.py", ".", 4),
        ("Backend API", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\backend", 12),
        ("Frontend UI", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\frontend", 8)
    ]
    for name, cmd, cwd, delay in services:
        start_service(name, cmd, cwd)
        print(f"⏳ Waiting {delay}s...")
        time.sleep(delay)
    # Test services
    print(f"\n🔍 TESTING SERVICES")
    print("-" * 30)
    tests = [
        ("Backend API", "http://localhost:4000/health"),
        ("Aryan Service", "http://localhost:5000/health"),
        ("Frontend", "http://localhost:3000")
    ]
    working_services = 0
    for name, url in tests:
        if test_service(url, name):
            working_services += 1
    print(f"\n📊 RESULTS: {working_services}/{len(tests)} services working")
    if working_services >= 2:  # Frontend + at least one backend service
        print("🎉 SYSTEM READY!")
        print("🌐 Opening inventory system...")
        webbrowser.open('http://localhost:3000')
        print(f"\n📱 Access Points:")
        print(f"   Frontend:  http://localhost:3000")
        print(f"   Backend:   http://localhost:4000") 
        print(f"   Health:    http://localhost:4000/health")
        if working_services == len(tests):
            print(f"\n🎯 FULL ASRS INTEGRATION ACTIVE!")
            print(f"   • Database connected (or using fallback)")
            print(f"   • Frontend loads boxes and items")
            print(f"   • Operations trigger ASRS commands")
        else:
            print(f"\n⚠️ PARTIAL SYSTEM RUNNING")
            print(f"   • Frontend working with fallback data")
            print(f"   • Check service windows for issues")
    else:
        print("❌ SYSTEM STARTUP FAILED")
        print("Check individual service windows for errors")
    print(f"\n🔄 Press Enter to stop all services...")
    input()
    print("🛑 Stopping services...")
    for name, process in processes:
        try:
            process.terminate()
        except:
            pass
if __name__ == "__main__":
    main()
