import subprocess
import asyncio

async def run_command(cmd, cwd=None):
    process = await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return process

async def main():
    base_path = r"C:\Users\kanad\PycharmProjects\FSMFINAL"
    
    print("Starting all services...")
    
    # Start ASRS control first
    print("Starting ASRS control server...")
    asrs_process = await run_command(r"python AS_RS_System\asrs_control.py", base_path)
    
    # Wait a moment for ASRS to start
    await asyncio.sleep(2)
    
    # Start aryan.py
    print("Starting aryan.py integration service...")
    aryan_process = await run_command(r"python aryan.py", base_path)
    
    # Wait a moment for aryan.py to start
    await asyncio.sleep(2)
    
    # Start backend
    print("Starting backend server...")
    backend_process = await run_command(r"npm run dev", base_path + r"\AS_RS_System\inventory-system\inventory-system\backend")
    
    # Wait a moment for backend to start
    await asyncio.sleep(3)
    
    # Start frontend
    print("Starting frontend server...")
    frontend_process = await run_command(r"npm run dev", base_path + r"\AS_RS_System\inventory-system\inventory-system\frontend")
    
    print("✅ All services started successfully!")
    print("🔧 ASRS Control: Running on port 8888")  
    print("🤖 Aryan Integration: Running on port 5000")
    print("🚀 Backend API: Running on port 4000")
    print("🌐 Frontend: Running on port 3000")
    print("\nSystem is ready for automation!")
    
    # Keep all processes running
    processes = [asrs_process, aryan_process, backend_process, frontend_process]
    await asyncio.gather(*[p.wait() for p in processes])

if __name__ == "__main__":
    asyncio.run(main())
