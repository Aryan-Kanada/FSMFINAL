# asrs_control.py
import os
import time
import asyncio
import logging
from opcua import Client, ua

# Logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('NODE_ENV')=='development' else logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

OPCUA_URL = os.getenv('OPCUA_SERVER_URL')
ASRS_HOST = os.getenv('ASRS_HOST','127.0.0.1')
ASRS_PORT = int(os.getenv('ASRS_PORT','8888'))

STORE_TAGS = {f"{l}{n}S":f"{l}{n}S" for l in "ABCDE" for n in range(1,8)}
RETRIEVE_TAGS = {f"{l}{n}":f"{l}{n}" for l in "ABCDE" for n in range(1,8)}

def pulse_node(client, tag,duration=0.1):
    node = client.get_node(f"ns=4;s={tag}")
    for val in (True, False):
        dv = ua.DataValue(ua.Variant(val, ua.VariantType.Boolean))
        node.set_attribute(ua.AttributeIds.Value, dv)
        time.sleep(duration)

async def handle(reader, writer):
    client=Client(OPCUA_URL); client.connect()
    addr=writer.get_extra_info('peername')
    logging.info(f"Client connected: {addr}")
    try:
        while data:=await reader.readline():
            cmd=data.decode().strip().upper()
            logging.debug(f"Command received: {cmd}")
            if cmd in STORE_TAGS:
                tag, action = STORE_TAGS[cmd], "Store"
            elif cmd in RETRIEVE_TAGS:
                tag, action = RETRIEVE_TAGS[cmd], "Retrieve"
            else:
                writer.write(f"Invalid {cmd}\n".encode()); await writer.drain(); continue
            await asyncio.to_thread(pulse_node, client, tag)
            resp=f"{action} at {tag.rstrip('S')}\n"
            writer.write(resp.encode()); await writer.drain()
    finally:
        client.disconnect(); writer.close()

async def main():
    server=await asyncio.start_server(handle, ASRS_HOST, ASRS_PORT)
    logging.info(f"ASRS server on {ASRS_HOST}:{ASRS_PORT}")
    async with server: await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
