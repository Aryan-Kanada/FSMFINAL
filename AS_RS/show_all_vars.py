"""
Detailed PLC Variable Explorer - Show All Names
"""

import asyncio
from asyncua import Client

PLC_IP = "10.10.14.104"
PLC_URL = f"opc.tcp://{PLC_IP}:4840"

async def show_all_globalvars():
    print(f"🔍 Showing ALL 71 variables in GlobalVars...")
    print(f"Connecting to {PLC_URL}...")

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Connected!")

            # Navigate to GlobalVars
            current_node = client.get_objects_node()
            current_node = await current_node.get_child("4:new_Controller_0")
            globalvars_node = await current_node.get_child("3:GlobalVars")

            variables = await globalvars_node.get_children()
            print(f"\n📋 All {len(variables)} variables in GlobalVars:")
            print("=" * 60)

            # Show all variable names
            for i, var in enumerate(variables, 1):
                try:
                    var_browse = await var.read_browse_name()
                    var_name = var_browse.Name
                    print(f"{i:2d}. {var_name}")
                except Exception as e:
                    print(f"{i:2d}. <error reading name: {e}>")

            print("\n" + "=" * 60)
            print("🔍 ANALYSIS:")
            print("Look for patterns like:")
            print("  • LED variables (might be A1S, A3S, A5S... or LED01, LED02...)")
            print("  • Button variables (might be A2, A4, A6... or PB01, PB02...)")
            print("  • Emergency kill (might be named differently)")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(show_all_globalvars())
