import sys
import time
from opcua import Client

# OPC UA server URL
SERVER_URL = "opc.tcp://10.10.14.104:4840"

# Valid tags for store (A1S–E7S) and retrieve (A1–E7)
STORE_TAGS = {f"{letter}{num}s".lower(): f"{letter}{num}s" for letter in "ABCDE" for num in range(1, 8)}
RETRIEVE_TAGS = {f"{letter}{num}".lower(): f"{letter}{num}" for letter in "ABCDE" for num in range(1, 8)}

def pulse_node(client, tag_name, duration=0.1):
    """Pulse a Boolean node on the PLC."""
    node = client.get_node(f"ns=4;s={tag_name}")
    node.set_value(True)
    time.sleep(duration)
    node.set_value(False)

def main():
    if len(sys.argv) != 2:
        print("Usage: python asrs_control.py <tag>")
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()

    action = None
    tag = None

    if cmd in STORE_TAGS:
        action = "Store"
        tag = STORE_TAGS[cmd]
    elif cmd in RETRIEVE_TAGS:
        action = "Retrieve"
        tag = RETRIEVE_TAGS[cmd]
    else:
        print(f"Invalid tag '{cmd}'. Use A1–E7 for retrieve or A1S–E7S for store.")
        sys.exit(1)

    client = Client(SERVER_URL)
    try:
        client.connect()
        pulse_node(client, tag)
        print(f"{action} at {tag[:-1] if action=='Store' else tag}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
