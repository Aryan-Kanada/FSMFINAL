import os
import time
import subprocess
import webbrowser
import sys
import requests
import signal

env_vars = {
    'NODE_ENV': 'development',
    'PORT_FRONTEND': '3000',
    'PORT_BACKEND': '4000', 
    'PORT_ARYAN': '5000',
    'ASRS_HOST': '127.0.0.1',
    'ASRS_PORT': '8888',
    'OPCUA_SERVER_URL': 'opc.tcp://localhost:4840'
}
for key, value in env_vars.items():
    os.environ[key] = value
processes = []
def cleanup():
    print("\n🛑 Shutting down all services...")
    for name, process in processes:
        if process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"   ✅ Stopped {name}")
            except:
                process.kill()
                print(f"   🔪 Killed {name}")
def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
def test_service(url, name, max_attempts=10):
    print(f"🧪 Testing {name}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} responding (status: {response.status_code})")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            print(f"   ⚠️ {name} test error: {e}")
        if attempt < max_attempts - 1:
            time.sleep(3)
    print(f"   ❌ {name} not responding after {max_attempts} attempts")
    return False
def start_service(name, cmd, cwd='.'): 
    print(f"🚀 Starting {name}...")
    try:
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                f'cmd /k "title {name} && {cmd}"',
                cwd=cwd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(cmd, cwd=cwd, shell=True)
        processes.append((name, process))
        print(f"   ✅ {name} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start {name}: {e}")
        return None
def main():
    print("🎯 FSMFINAL - COMPLETE ASRS SYSTEM STARTUP")
    print("=" * 60)
    # Setup database first
    print("🗄️ Setting up database...")
    try:
        subprocess.run([sys.executable, "setup_database.py"], timeout=30)
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")
    # Start all services
    services_config = [
        ("ASRS Control", "python asrs_control.py", ".", 4),
        ("Aryan Middleware", "python aryan.py", ".", 5),
        ("Backend API", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\backend", 15),
        ("Frontend UI", "npm run dev", "AS_RS_System\\inventory-system\\inventory-system\\frontend", 10)
    ]
    for name, cmd, cwd, delay in services_config:
        start_service(name, cmd, cwd)
        print(f"⏳ Waiting {delay}s for {name} to initialize...")
        time.sleep(delay)
    # Test all services
    print("\n🔍 TESTING ALL SERVICES")
    print("-" * 40)
    tests = [
        ("Backend API", "http://localhost:4000/health"),
        ("Aryan Middleware", "http://localhost:5000/health"),
        ("Frontend UI", "http://localhost:3000")
    ]
    all_working = True
    for name, url in tests:
        if not test_service(url, name):
            all_working = False
    print(f"\n📊 SYSTEM STATUS")
    print("-" * 30)
    if all_working:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🌐 Opening Inventory Management System...")
        webbrowser.open('http://localhost:3000')
        print(f"\n📱 Available Services:")
        print(f"   Frontend:       http://localhost:3000")
        print(f"   Backend API:    http://localhost:4000") 
        print(f"   Aryan Service:  http://localhost:5000")
        print(f"   ASRS Control:   TCP://localhost:8888")
        print(f"\n🎯 ASRS INTEGRATION READY!")
        print(f"   • Web interface loads boxes and items from database")
        print(f"   • Add/retrieve operations trigger physical ASRS")
        print(f"   • E-commerce orders automatically move inventory")
        print(f"   • Real-time command monitoring in service windows")
    else:
        print("❌ SYSTEM STARTUP ISSUES DETECTED")
        print("\nTroubleshooting:")
        print("1. Check MySQL is running: net start mysql")
        print("2. Verify database exists: mysql -u root -e 'SHOW DATABASES;'")
        print("3. Check service windows for detailed error messages")
        print("4. Ensure no other processes using ports 3000, 4000, 5000, 8888")
    print(f"\n🔄 System running. Press Ctrl+C or Enter to stop all services.")
    try:
        input()  # Wait for user input
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
if __name__ == "__main__":
    main()
