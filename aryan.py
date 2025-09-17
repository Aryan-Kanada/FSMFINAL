# aryan.py
import os
import logging
import asyncio
import threading
import requests
import json

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils import parse_retrieval_location, parse_storage_update

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per minute"])

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('NODE_ENV')=='development' else logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

ASRS_HOST = os.getenv('ASRS_HOST', '127.0.0.1')
ASRS_PORT = int(os.getenv('ASRS_PORT', '8888'))
BACKEND_API = f"http://localhost:{os.getenv('PORT_BACKEND', '4000')}"

async def send_command_to_asrs(cmd):
    try:
        reader, writer = await asyncio.open_connection(ASRS_HOST, ASRS_PORT)
        logging.info(f"Sending command to ASRS: {cmd}")
        writer.write((cmd+"\n").encode())
        await writer.drain()
        resp = await reader.readline()
        writer.close()
        await writer.wait_closed()
        return resp.decode().strip()
    except Exception as e:
        logging.error(f"Error sending to ASRS: {e}")
        return None

def run_async(cmd):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_command_to_asrs(cmd))
    loop.close()

@app.route('/backend-data', methods=['POST'])
@limiter.limit("50/minute")
def handle_backend_data():
    data = request.json
    logging.debug(f"Received data: {json.dumps(data)}")
    commands = []
    # Handle product_added
    if data.get('type') == 'product_added':
        loc = parse_storage_update(data['subcom_place'], data['status'])
        if loc:
            commands.append(loc.upper())
    # Handle product_retrieved
    elif data.get('type') == 'product_retrieved':
        for loc in data.get('locations', []):
            loc_tag = parse_retrieval_location(loc)
            if loc_tag:
                commands.append(loc_tag.upper())
    # Send commands to ASRS TCP server
    for cmd in commands:
        threading.Thread(target=run_async, args=(cmd,)).start()
    return jsonify({"status": "success", "processed": commands})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status":"running","port":os.getenv('PORT_ARYAN','5000')})

if __name__=="__main__":
    port = int(os.getenv('PORT_ARYAN','5000'))
    logging.info(f"Starting aryan.py on port {port}")
    app.run(host='0.0.0.0', port=port)
