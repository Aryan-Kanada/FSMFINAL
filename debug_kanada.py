import asyncio
import webbrowser
import requests
import os
import time
import subprocess
import sys
from pathlib import Path

def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    print(f"Environment loaded. Backend port: {os.getenv('PORT_BACKEND', '4000')}")

async def run_command_with_output(cmd, cwd=None, name="Service"):
    print(f"Starting {name}: {cmd}")
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            shell=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

async def check_port(port, name):
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            print(f"✅ {name} - Port {port} is open")
            return True
        else:
            print(f"❌ {name} - Port {port} is closed")
            return False
    except Exception as e:
        print(f"❌ {name} - Error checking port {port}: {e}")
        return False

async def wait_for_service_advanced(url, name, max_attempts=20):
    print(f"Waiting for {name} at {url}...")
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        port = parsed.port or (80 if parsed.scheme == 'http' else 443)
    except:
        port = None
    for attempt in range(max_attempts):
        try:
            if port:
                if not await check_port(port, name):
                    print(f"  Attempt {attempt+1}/{max_attempts}: Port {port} not ready")
                    await asyncio.sleep(3)
                    continue
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is ready!")
                return True
            else:
                print(f"  Attempt {attempt+1}/{max_attempts}: Got status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  Attempt {attempt+1}/{max_attempts}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"  Attempt {attempt+1}/{max_attempts}: Timeout")
        except Exception as e:
            print(f"  Attempt {attempt+1}/{max_attempts}: {str(e)}")
        await asyncio.sleep(3)
    print(f"❌ {name} failed to start after {max_attempts} attempts")
    return False

async def check_processes(processes):
    for name, process in processes.items():
        if process and process.returncode is None:
            print(f"✅ {name} process is running (PID: {process.pid})")
        elif process:
            print(f"❌ {name} process exited with code {process.returncode}")
            try:
                stderr = await process.stderr.read()
                if stderr:
                    print(f"   Error output: {stderr.decode()}")
            except:
                pass
        else:
            print(f"❌ {name} process failed to start")

async def main():
    load_env()
    base = os.path.dirname(os.path.abspath(__file__))
    print("=== ENHANCED SERVICE STARTUP DEBUG ===")
    print(f"Working directory: {base}")

    backend_path = os.path.join(base, "AS_RS_System", "inventory-system", "inventory-system", "backend")
    frontend_path = os.path.join(base, "AS_RS_System", "inventory-system", "inventory-system", "frontend")

    if not os.path.exists(backend_path):
        print(f"❌ Backend path not found: {backend_path}")
        return
    if not os.path.exists(frontend_path):
        print(f"❌ Frontend path not found: {frontend_path}")
        return

    print("✅ Directory structure verified")
    processes = {}

    print("\n🚀 Starting services...")

    processes['ASRS'] = await run_command_with_output(
        "python asrs_control.py",
        cwd=base,
        name="ASRS Control"
    )
    await asyncio.sleep(2)

    processes['Aryan'] = await run_command_with_output(
        "python aryan.py",
        cwd=base,
        name="Aryan Service"
    )
    await asyncio.sleep(3)

    processes['Backend'] = await run_command_with_output(
        "npm run dev",
        cwd=backend_path,
        name="Backend"
    )
    await asyncio.sleep(5)

    processes['Frontend'] = await run_command_with_output(
        "npm run dev",
        cwd=frontend_path,
        name="Frontend"
    )
    await asyncio.sleep(5)

    print("\n📊 Checking process status...")
    await check_processes(processes)

    print("\n🔍 Testing service connectivity...")

    services = {
        "Backend": f"http://localhost:{os.getenv('PORT_BACKEND', '4000')}/health",
        "Aryan": f"http://localhost:{os.getenv('PORT_ARYAN', '5000')}/health",
        "Frontend": f"http://localhost:{os.getenv('PORT_FRONTEND', '3000')}"
    }

    all_ready = True
    for name, url in services.items():
        ready = await wait_for_service_advanced(url, name)
        if not ready:
            all_ready = False

    if all_ready:
        print("\n🎉 All services are ready!")
        frontend_url = f"http://localhost:{os.getenv('PORT_FRONTEND', '3000')}"
        print(f"Opening {frontend_url}")
        webbrowser.open(frontend_url)
    else:
        print("\n❌ Some services failed to start properly")
        print("\nDEBUG INFORMATION:")
        print("1. Check if all dependencies are installed:")
        print("   npm install (in both backend and frontend folders)")
        print("   pip install flask flask-limiter opcua requests")
        print("\n2. Check if ports are already in use:")
        print("   netstat -an | findstr :3000")
        print("   netstat -an | findstr :4000")
        print("   netstat -an | findstr :5000")
        print("   netstat -an | findstr :8888")
        print("\n3. Check individual service logs by running them separately")
        return

    print("\n🔄 Services running. Press Ctrl+C to stop all services.")
    try:
        await asyncio.gather(
            *[p.wait() for p in processes.values() if p],
            return_exceptions=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in processes.items():
            if process and process.returncode is None:
                process.terminate()
                print(f"Stopped {name}")

if __name__ == "__main__":
    asyncio.run(main())
