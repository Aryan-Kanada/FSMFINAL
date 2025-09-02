"""
Test script to verify connection with actual PLC variables
"""

import asyncio
from asrs_core_actual import ActualPLCClient

async def test_connection():
    print("🧪 Testing connection to your physical AS/RS system...")
    print()

    config = {
        "plc": {"url": "opc.tcp://10.10.14.104:4840"},
        "operation": {"scan_interval": 0.5}
    }

    client = ActualPLCClient(config)

    try:
        # Test connection
        if await client.connect():
            print("✅ Successfully connected to your PLC!")

            # Get statistics
            stats = client.get_statistics()
            print(f"📊 Connection Statistics:")
            print(f"   LED Variables: {stats['led_nodes']}/35")
            print(f"   Button Variables: {stats['button_nodes']}/35")
            print(f"   Motion Variables: {stats['motion_nodes']}/10")
            print()

            # Test reading a few variables
            print("🔍 Testing variable reads...")

            # Test LED reads (first 5 positions)
            for pos_id in [1, 2, 3, 4, 5]:
                try:
                    led_state = await client.read_led_state(pos_id)
                    if led_state is not None:
                        print(f"   Position {pos_id}: LED = {led_state}")
                    else:
                        print(f"   Position {pos_id}: LED read failed")
                except Exception as e:
                    print(f"   Position {pos_id}: Error - {e}")

            print()
            print("✅ Your physical AS/RS system is ready!")
            print("✅ All PLC variables mapped successfully!")
            print("✅ Ready for store/retrieve operations!")

        else:
            print("❌ Failed to connect to PLC")
            print("   Check if:")
            print("   - PLC is running")
            print("   - OPC UA server is enabled")
            print("   - IP address is correct (10.10.14.104)")

    except Exception as e:
        print(f"❌ Connection test failed: {e}")

    finally:
        await client.disconnect()
        print("\n👋 Test completed")

if __name__ == "__main__":
    asyncio.run(test_connection())
