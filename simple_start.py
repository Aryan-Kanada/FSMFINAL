import subprocess
import time
import webbrowser
import os

def run_service(cmd, cwd=None, shell=True):
    print(f"Starting: {cmd}")
    return subprocess.Popen(cmd, cwd=cwd, shell=shell)

# Start ASRS Control (Python)
asrs_control = run_service("C:/Users/kanad/PycharmProjects/FSMFINAL/.venv/Scripts/python.exe asrs_control.py", cwd=".")
time.sleep(2)

# Start Aryan Middleware (Python)
aryan = run_service("C:/Users/kanad/PycharmProjects/FSMFINAL/.venv/Scripts/python.exe aryan.py", cwd=".")
time.sleep(2)

# Start ASRS API (Python)
asrs_api = run_service("C:/Users/kanad/PycharmProjects/FSMFINAL/.venv/Scripts/python.exe asrs_api.py", cwd=".")
time.sleep(2)

# Start Backend (Node.js)
backend = run_service("npm start", cwd="AS_RS_System/inventory-system/inventory-system/backend")
time.sleep(2)

# Start Frontend (Node.js)
frontend = run_service("npm run dev", cwd="AS_RS_System/inventory-system/inventory-system/frontend")
time.sleep(5)

# Open frontend in browser
webbrowser.open("http://localhost:3000")

print("All services started. Check terminals for errors.")
