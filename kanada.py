import asyncio
import webbrowser
import requests
import os
import time

async def run_command(cmd, cwd=None):
    return await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        shell=True,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

async def main():
    base = os.path.dirname(os.path.abspath(__file__))

    print("Starting ASRS control server...")
    asrs = await run_command("python AS_RS_System/asrs_control.py", cwd=base)
    print("Starting aryan.py service...")
    aryan = await run_command("python aryan.py", cwd=base)
    print("Starting backend server...")
    backend = await run_command("npm run dev", cwd=os.path.join(base, "AS_RS_System","inventory-system","inventory-system","backend"))
    print("Starting frontend server...")
    frontend = await run_command("npm run dev", cwd=os.path.join(base, "AS_RS_System","inventory-system","inventory-system","frontend"))

    print("✅ All services started successfully!")

    async def wait_for_service(url, max_attempts=10):
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    return True
            except:
                await asyncio.sleep(2)
        return False

    services = {
        "Frontend": f"http://localhost:{os.getenv('PORT_FRONTEND', '3000')}",
        "Backend":  f"http://localhost:{os.getenv('PORT_BACKEND', '4000')}/health",
        "Aryan":    f"http://localhost:{os.getenv('PORT_ARYAN', '5000')}/health"
    }

    for name, url in services.items():
        print(f"Waiting for {name} at {url}...", end=" ")
        if await wait_for_service(url):
            print("OK")
            if name == "Frontend":
                webbrowser.open(url)
        else:
            print("Failed")

    await asyncio.gather(
        asrs.wait(),
        aryan.wait(),
        backend.wait(),
        frontend.wait()
    )

if __name__ == "__main__":
    asyncio.run(main())
