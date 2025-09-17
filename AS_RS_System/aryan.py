import asyncio
import re

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

async def send_command(cmd):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    print(f"Sending command: {cmd}")
    writer.write((cmd + "\n").encode())
    await writer.drain()
    response = await reader.readline()
    print(f"Response: {response.decode().strip()}")
    writer.close()
    await writer.wait_closed()

def process_input_and_send(data):
    lines = data.splitlines()
    command = None
    if "Locations:" in data:
        # Retrieval command example
        for i, line in enumerate(lines):
            if line.startswith("Locations:"):
                j = i + 1
                while j < len(lines) and lines[j].strip():
                    loc_match = re.search(r"\d+\.\s*([A-E][1-7])[a-z]?", lines[j])
                    if loc_match:
                        loc = parse_retrieval_location(loc_match.group(1))
                        if loc:
                            # Retrieval command does NOT have "S"
                            command = loc
                            return command
                    j += 1
    elif "Status:" in data and "Location:" in data:
        location = None
        status = None
        for line in lines:
            if line.startswith("Location:"):
                location = line.split(":",1)[1].strip()
            elif line.startswith("Status:"):
                status = line.split(":",1)[1].strip()
        if location and status:
            command = parse_storage_update(location, status)
            return command
    return None

async def main():
    # Example inputs, replace with real dynamic input handling
    retrieval_input = """Results
Successfully retrieved 1 item(s)!
Item: Bearing
Quantity: 1
Locations:
1. C1c (ID: C1c)
Retrieval Strategy: Column-wise (A1→A7, then B1→B7, etc.)"""

    storage_update_input = """Product added successfully!
Item: Gear
Location: A1a
Status: Occupied
Note: Updated empty place to occupied"""

    for data in [retrieval_input, storage_update_input]:
        cmd = process_input_and_send(data)
        if cmd:
            await send_command(cmd)
        else:
            print("No valid command found in input.")

if __name__ == "__main__":
    asyncio.run(main())
