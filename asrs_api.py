from flask import Flask, request, jsonify
from asrs_control import pulse_node, STORE_TAGS, RETRIEVE_TAGS, SERVER_URL
from opcua import Client, ua

app = Flask(__name__)

@app.route('/asrs', methods=['POST'])
def asrs_command():
    data = request.json
    # Accept operation and location from frontend/backend
    operation = data.get('operation', '').strip().lower()  # 'add' or 'retrieve'
    location = data.get('location', '').strip().upper()    # e.g. 'A1', 'B2', etc.

    if not operation or not location:
        return jsonify({'error': 'Operation and location required'}), 400

    if operation == 'add':
        cmd = location + 'S'  # Store command
        action = 'Store'
    elif operation == 'retrieve':
        cmd = location        # Retrieve command
        action = 'Retrieve'
    else:
        return jsonify({'error': f"Invalid operation '{operation}'. Use 'add' or 'retrieve'."}), 400

    if (operation == 'add' and cmd not in STORE_TAGS) or (operation == 'retrieve' and cmd not in RETRIEVE_TAGS):
        return jsonify({'error': f"Invalid location '{location}'. Use A1–E7."}), 400

    tag = cmd
    client = Client(SERVER_URL)
    client.connect()
    try:
        pulse_node(client, tag)
        return jsonify({'result': f"{action} at {location}"})
    except ua.UaStatusCodeError as e:
        return jsonify({'error': f"Write failed: {e}"}), 500
    finally:
        client.disconnect()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)