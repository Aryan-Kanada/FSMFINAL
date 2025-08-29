"""
Simple PLC Variable Explorer
Find all variables in all folders
"""

import asyncio
from asyncua import Client

PLC_IP = "10.10.14.104"
PLC_URL = f"opc.tcp://{PLC_IP}:4840"
KNOWN_PATH = ["0:Objects", "4:new_Controller_0"]

async def explore_all_folders():
    print(f"🔍 Exploring ALL folders in PLC...")
    print(f"Connecting to {PLC_URL}...")

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Connected!")

            # Navigate to controller
            current_node = client.get_objects_node()
            for part in KNOWN_PATH[1:]:
                current_node = await current_node.get_child(part)

            # Get all folders
            children = await current_node.get_children()
            print(f"\nFound {len(children)} folders:")

            for child in children:
                browse_name = await child.read_browse_name()
                folder_name = browse_name.Name
                namespace = browse_name.NamespaceIndex

                print(f"\n📁 Exploring: {folder_name} (namespace:{namespace})")
                print("-" * 50)

                try:
                    # Get variables in this folder
                    variables = await child.get_children()

                    if variables:
                        print(f"   Found {len(variables)} items:")

                        # Show first 10 variables
                        for i, var in enumerate(variables[:10]):
                            try:
                                var_browse = await var.read_browse_name()
                                var_name = var_browse.Name
                                print(f"   {i+1:2d}. {var_name}")
                            except:
                                print(f"   {i+1:2d}. <could not read name>")

                        if len(variables) > 10:
                            print(f"   ... and {len(variables) - 10} more")

                        # Check for AS/RS variables
                        led_count = 0
                        pb_count = 0
                        kill_found = False

                        for var in variables:
                            try:
                                var_browse = await var.read_browse_name()
                                var_name = var_browse.Name.lower()

                                if 'led' in var_name and any(c.isdigit() for c in var_name):
                                    led_count += 1
                                elif ('pb' in var_name or 'button' in var_name) and any(c.isdigit() for c in var_name):
                                    pb_count += 1
                                elif 'kill' in var_name or 'emergency' in var_name:
                                    kill_found = True
                            except:
                                pass

                        if led_count > 0 or pb_count > 0 or kill_found:
                            print(f"\n   🎯 AS/RS VARIABLES FOUND!")
                            print(f"      LEDs: {led_count}")
                            print(f"      Buttons: {pb_count}")
                            print(f"      Emergency: {'Yes' if kill_found else 'No'}")
                            print(f"\n   ✅ USE THIS PATH: ['0:Objects', '4:new_Controller_0', '{namespace}:{folder_name}']")
                    else:
                        print("   📭 Empty folder")

                except Exception as e:
                    print(f"   ❌ Could not explore folder: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_all_folders())
