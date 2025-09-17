from flask import Flask, request, jsonify
import asyncio
import re
import threading
import requests
import json

app = Flask(__name__)

def parse_retrieval_location(loc_str):
    match = re.match(r"([A-E])([1-7])", loc_str)
    if match:
        return match.group(1) + match.group(2)
    return None

def parse_storage_update(location_str, status):
    match = re.match(r"([A-E])([1-7])", location_str)
    if match:
        loc = match.group(1) + match.group(2)
        if status.lower() == "occupied":
            loc += "s"
        return loc
    return None

async def send_command_to_asrs(cmd):
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
        print(f"Sending command to ASRS: {cmd}")
        writer.write((cmd + "\n").encode())
        await writer.drain()
        response = await reader.readline()
        print(f"ASRS Response: {response.decode().strip()}")
        writer.close()
        await writer.wait_closed()
        return response.decode().strip()
    except Exception as e:
        print(f"Error sending to ASRS: {e}")
        return None

def run_async_command(cmd):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(send_command_to_asrs(cmd))
    loop.close()
    return result

# Main endpoint for backend to send data
@app.route('/backend-data', methods=['POST'])
def handle_backend_data():
    data = request.json
    print(f"Received data from backend: {json.dumps(data, indent=2)}")
    
    commands = []
    
    # Handle order placement (items being retrieved from inventory)
    if data.get('type') == 'order_placed':
        order_items = data.get('order_items', [])
        for item in order_items:
            item_id = item.get('item_id')
            quantity = item.get('quantity', 1)
            
            # Get item locations from backend API
            try:
                locations_response = requests.get(f'http://localhost:4000/api/items/{item_id}/locations')
                if locations_response.status_code == 200:
                    locations_data = locations_response.json()
                    locations = locations_data.get('data', [])
                    
                    # Take only the required quantity of locations
                    for i, location in enumerate(locations[:quantity]):
                        subcom_place = location.get('subcom_place', '')
                        # Extract position like A1, B2, etc. from subcom_place (e.g., A1a -> A1)
                        if len(subcom_place) >= 2:
                            position = subcom_place[:2]  # A1, B2, etc.
                            if re.match(r"[A-E][1-7]", position):
                                commands.append(position)  # Retrieval command (no 's')
            except Exception as e:
                print(f"Error getting locations for item {item_id}: {e}")
    
    # Handle product addition to inventory
    elif data.get('type') == 'product_added':
        subcom_place = data.get('subcom_place', '')
        status = data.get('status', '')
        
        if len(subcom_place) >= 2:
            position = subcom_place[:2]  # A1, B2, etc.
            if re.match(r"[A-E][1-7]", position) and status.lower() == 'occupied':
                commands.append(position + 's')  # Storage command (with 's')
    
    # Handle product retrieval
    elif data.get('type') == 'product_retrieved':
        locations = data.get('locations', [])
        for location in locations:
            subcom_place = location.get('subcom_place', '')
            if len(subcom_place) >= 2:
                position = subcom_place[:2]  # A1, B2, etc.
                if re.match(r"[A-E][1-7]", position):
                    commands.append(position)  # Retrieval command (no 's')
    
    # Send commands to ASRS
    results = []
    for command in commands:
        if command:
            print(f"Processing command: {command}")
            thread = threading.Thread(target=run_async_command, args=(command,))
            thread.start()
            results.append(command)
    
    return jsonify({
        "status": "success", 
        "processed_commands": results,
        "total_commands": len(results)
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "aryan.py is running", "port": 5000})

if __name__ == "__main__":
    print("Starting aryan.py HTTP server on port 5000...")
    print("Endpoints available:")
    print("  POST /backend-data - Receive data from backend")
    print("  GET /health - Health check")
    app.run(host="127.0.0.1", port=5000, debug=True)
