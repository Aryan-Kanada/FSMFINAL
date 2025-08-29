"""
Quick Variable Test - Debug the issue
"""

import asyncio
from asyncua import Client

async def test_variables():
    print("🔧 Testing variable access...")

    try:
        async with Client("opc.tcp://10.10.14.104:4840") as client:
            print("✅ Connected")

            # Navigate to GlobalVars
            current_node = client.get_objects_node()
            current_node = await current_node.get_child("4:new_Controller_0")
            globalvars_node = await current_node.get_child("3:GlobalVars")

            variables = await globalvars_node.get_children()
            print(f"✅ Found {len(variables)} variables")

            if len(variables) > 0:
                print("✅ Variable access is working!")
                return True
            else:
                print("❌ No variables found")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_variables())
