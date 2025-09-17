import time
import asyncio
from opcua import Client, ua

SERVER_URL = "opc.tcp://10.10.14.104:4840"

STORE_TAGS = {f"{l}{n}S": f"{l}{n}S" for l in "ABCDE" for n in range(1, 8)}
RETRIEVE_TAGS = {f"{l}{n}": f"{l}{n}" for l in "ABCDE" for n in range(1, 8)}

def pulse_node(client, tag_name, duration=0.1):
    node = client.get_node(f"ns=4;s={tag_name}")
    variant_true = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
    variant_false = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
    node.set_attribute(ua.AttributeIds.Value, variant_true)
    time.sleep(duration)
    node.set_attribute(ua.AttributeIds.Value, variant_false)

async def handle_client(reader, writer):
    client = Client(SERVER_URL)
    await asyncio.to_thread(client.connect)
    addr = writer.get_extra_info('peername')
    print(f"Connected to {addr}")
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            cmd = data.decode().strip().upper()
            print(f"Received command: {cmd}")
            if cmd in STORE_TAGS:
                tag = STORE_TAGS[cmd]
                action = "Store"
                loc = tag[:-1]
            elif cmd in RETRIEVE_TAGS:
                tag = RETRIEVE_TAGS[cmd]
                action = "Retrieve"
                loc = tag
            else:
                msg = f"Invalid tag '{cmd}'. Use A1–E7 or A1S–E7S.\n"
                writer.write(msg.encode())
                await writer.drain()
                continue
            try:
                await asyncio.to_thread(pulse_node, client, tag)
                response = f"{action} at {loc}\n"
                print(response.strip())
                writer.write(response.encode())
                await writer.drain()
            except Exception as e:
                err = f"Write failed: {e}\n"
                print(err.strip())
                writer.write(err.encode())
                await writer.drain()
    finally:
        client.disconnect()
        print(f"Disconnected from {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Server listening on {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
