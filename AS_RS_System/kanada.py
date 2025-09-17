import subprocess
import asyncio
import re

async def run_command(cmd, cwd=None):
    process = await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode

def parse_retrieval_location(loc_str):
    match = re.match(r"([A-E])([1-7])", loc_str)
    if match:
        return match.group(1) + match.group(2)
    return None

def parse_storage_update(location_str, status):
    loc = None
    match = re.match(r"([A-E])([1-7])", location_str)
    if match:
        loc = match.group(1) + match.group(2)
        if status.lower() == "occupied":
            loc += "s"
    return loc

async def main():
    base_path = r"C:\Users\kanad\PycharmProjects\FSMFINAL"
    cmds = [
        (r"python AS_RS_System\asrs_control.py", base_path),
        (r"npm run dev", base_path + r"\AS_RS_System\inventory-system\inventory-system\frontend"),
        (r"npm run dev", base_path + r"\AS_RS_System\inventory-system\inventory-system\backend"),
        (r"python aryan.py", base_path)
    ]

    tasks = [run_command(cmd, cwd) for cmd, cwd in cmds]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Command {i+1} raised exception: {result}")
            continue
        stdout, stderr, returncode = result
        print(f"Command {i+1} exited with code {returncode}")
        if stdout:
            print(f"Stdout:\n{stdout}")
        if stderr:
            print(f"Stderr:\n{stderr}")

if __name__ == "__main__":
    asyncio.run(main())
