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
    base = r"C:\Users\kanad\PycharmProjects\FSMFINAL"

    print("Starting ASRS control server...")
    asrs = await run_command("python AS_RS_System\\asrs_control.py", cwd=base)
    await asyncio.sleep(2)

    print("Starting aryan.py service...")
    aryan = await run_command("python aryan.py", cwd=base)
    await asyncio.sleep(2)

    print("Starting backend server...")
    backend = await run_command("npm run dev", cwd=os.path.join(base, "AS_RS_System","inventory-system","inventory-system","backend"))
    await asyncio.sleep(5)

    print("Starting frontend server...")
    frontend = await run_command("npm run dev", cwd=os.path.join(base, "AS_RS_System","inventory-system","inventory-system","frontend"))
    await asyncio.sleep(5)

    print("✅ All services started successfully!")

    # Health check URLs
    services = {
        "Frontend": f"http://localhost:{os.getenv('PORT_FRONTEND', '3000')}",
        "Backend":  f"http://localhost:{os.getenv('PORT_BACKEND', '4000')}/health",
        "Aryan":    f"http://localhost:{os.getenv('PORT_ARYAN', '5000')}/health"
    }

    for name, url in services.items():
        print(f"Checking {name} at {url}...", end=" ")
        for _ in range(5):
            try:
                r = requests.get(url, timeout=3)
                print(f"OK ({r.status_code})")
                if name == "Frontend":
                    webbrowser.open(url)
                break
            except Exception:
                time.sleep(2)
        else:
            print("Failed")

    # Keep all servers running
    await asyncio.gather(
        asrs.wait(),
        aryan.wait(),
        backend.wait(),
        frontend.wait()
    )

if __name__ == "__main__":
    asyncio.run(main())
