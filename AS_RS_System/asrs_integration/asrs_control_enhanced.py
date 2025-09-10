
"""
Enhanced ASRS Control Module
Integrates with inventory system for automatic operation
Author: Integration Service
"""

import time
from opcua import Client, ua
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_URL = "opc.tcp://10.10.14.104:4840"

# Map location codes to ASRS commands
STORE_TAGS = {f"{l}{n}S": f"{l}{n}S" for l in "ABCDE" for n in range(1, 8)}
RETRIEVE_TAGS = {f"{l}{n}": f"{l}{n}" for l in "ABCDE" for n in range(1, 8)}

class ASRSController:
    def __init__(self):
        self.client = None
        self.connected = False

    def connect(self):
        """Connect to ASRS OPC UA server"""
        try:
            self.client = Client(SERVER_URL)
            self.client.connect()
            self.connected = True
            logger.info("✅ Connected to ASRS system")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to ASRS: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from ASRS OPC UA server"""
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                logger.info("🔌 Disconnected from ASRS system")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    def pulse_node(self, tag_name, duration=0.1):
        """Send pulse command to ASRS node"""
        if not self.connected:
            raise Exception("ASRS not connected")

        try:
            node = self.client.get_node(f"ns=4;s={tag_name}")
            variant_true = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
            variant_false = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))

            node.set_attribute(ua.AttributeIds.Value, variant_true)
            time.sleep(duration)
            node.set_attribute(ua.AttributeIds.Value, variant_false)

            logger.info(f"📡 Sent command: {tag_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send command {tag_name}: {e}")
            return False

    def store_item(self, location):
        """Store item at specified location (e.g., 'A1')"""
        store_cmd = f"{location}S"
        if store_cmd not in STORE_TAGS:
            raise ValueError(f"Invalid store location: {location}")

        logger.info(f"🏪 Storing item at location {location}")
        success = self.pulse_node(store_cmd)

        if success:
            logger.info(f"✅ Store operation completed: {location}")
        else:
            logger.error(f"❌ Store operation failed: {location}")

        return success

    def retrieve_item(self, location):
        """Retrieve item from specified location (e.g., 'A1')"""
        retrieve_cmd = location
        if retrieve_cmd not in RETRIEVE_TAGS:
            raise ValueError(f"Invalid retrieve location: {location}")

        logger.info(f"📦 Retrieving item from location {location}")
        success = self.pulse_node(retrieve_cmd)

        if success:
            logger.info(f"✅ Retrieve operation completed: {location}")
        else:
            logger.error(f"❌ Retrieve operation failed: {location}")

        return success

    def execute_command(self, command_type, location):
        """Execute store or retrieve command"""
        if not self.connect():
            return False

        try:
            if command_type.lower() == 'store':
                result = self.store_item(location)
            elif command_type.lower() == 'retrieve':
                result = self.retrieve_item(location)
            else:
                raise ValueError(f"Invalid command type: {command_type}")

            time.sleep(2)  # Wait for operation to complete
            return result

        finally:
            self.disconnect()

# Backward compatibility function for existing manual usage
def main():
    """Manual ASRS control (original functionality)"""
    controller = ASRSController()

    try:
        cmd = input("Write your command (e.g. A1S-E7S for Store or A1-E7 for Retrieve): ").strip().upper()

        if cmd in STORE_TAGS:
            location = cmd[:-1]  # Remove 'S'
            success = controller.execute_command('store', location)
            action = "Store"
        elif cmd in RETRIEVE_TAGS:
            location = cmd
            success = controller.execute_command('retrieve', location)
            action = "Retrieve"
        else:
            print(f"Invalid tag '{cmd}'. Use A1–E7 or A1S–E7S.")
            return

        if success:
            print(f"✅ {action} at {location} completed successfully")
        else:
            print(f"❌ {action} at {location} failed")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
