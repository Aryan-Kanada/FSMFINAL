import time
from opcua import Client, ua

SERVER_URL = "opc.tcp://10.10.14.104:4840"

# Map uppercase commands to node names
STORE_TAGS = {f"{l}{n}S": f"{l}{n}S" for l in "ABCDE" for n in range(1, 8)}
RETRIEVE_TAGS = {f"{l}{n}": f"{l}{n}" for l in "ABCDE" for n in range(1, 8)}

def pulse_node(client, tag_name, duration=0.1):
    node = client.get_node(f"ns=4;s={tag_name}")
    variant_true = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
    variant_false = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
    node.set_attribute(ua.AttributeIds.Value, variant_true)
    time.sleep(duration)
    node.set_attribute(ua.AttributeIds.Value, variant_false)

def main():
    client = Client(SERVER_URL)
    client.connect()
    try:
        cmd = input("Write your command (e.g. A1S-E7S for Store or A1-E7 for Retrieve): ").strip().upper()
        if cmd in STORE_TAGS:
            tag = STORE_TAGS[cmd]
            action = "Store"
            loc = tag[:-1]
        elif cmd in RETRIEVE_TAGS:
            tag = RETRIEVE_TAGS[cmd]
            action = "Retrieve"
            loc = tag
        else:
            print(f"Invalid tag '{cmd}'. Use A1–E7 or A1S–E7S.")
            return
# Author: Aryan Kanada
        try:
            pulse_node(client, tag)
            print(f"{action} at {loc}")
        except ua.UaStatusCodeError as e:
            print(f"Write failed: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
