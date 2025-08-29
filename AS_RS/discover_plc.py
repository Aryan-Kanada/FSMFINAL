"""
BVM AS/RS PLC Discovery Script
Based on working asyncua connection to find PLC variables
"""

import asyncio
from asyncua import Client

# Configuration - using working values
PLC_IP = "10.10.14.104"
PLC_URL = f"opc.tcp://{PLC_IP}:4840"
KNOWN_PATH = ["0:Objects", "4:new_Controller_0"]

async def discover_variables():
    """Discover PLC variables and structure"""
    print(f"🔍 Connecting to PLC at {PLC_URL}...")

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Successfully connected to PLC!")

            # Navigate to known path
            current_node = client.get_objects_node()
            print(f"\n📁 Navigating through PLC structure...")

            for part in KNOWN_PATH[1:]:
                try:
                    current_node = await current_node.get_child(part)
                    print(f"   ✅ Found: {part}")
                except Exception as e:
                    print(f"   ❌ Could not find: {part} - {e}")
                    return

            print(f"\n📂 Contents of '{KNOWN_PATH[-1]}' folder:")
            print("=" * 60)

            children = await current_node.get_children()

            if not children:
                print("   📭 This folder is empty")
                return

            # Look for GlobalVars or similar
            variables_folder = None
            for child in children:
                browse_name = await child.read_browse_name()
                print(f"   📁 {browse_name.Name} (namespace: {browse_name.NamespaceIndex})")

                # Check if this might be the variables folder
                if any(keyword in browse_name.Name.lower() for keyword in ['global', 'vars', 'variables', 'tags']):
                    variables_folder = child
                    print(f"      👆 This looks like the variables folder!")

            # If we found a likely variables folder, explore it
            if variables_folder:
                print(f"\n🔍 Exploring variables folder...")
                await explore_variables_folder(variables_folder)
            else:
                print("\n⚠️  No obvious variables folder found.")
                print("   Try exploring each folder manually.")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

async def explore_variables_folder(folder_node):
    """Explore the variables folder to find LED/button variables"""
    try:
        children = await folder_node.get_children()

        print(f"\n📋 Variables found ({len(children)} total):")
        print("-" * 60)

        led_vars = []
        button_vars = []
        other_vars = []

        for child in children:
            browse_name = await child.read_browse_name()
            var_name = browse_name.Name

            # Categorize variables
            if var_name.startswith('led'):
                led_vars.append(var_name)
            elif var_name.startswith('pb'):
                button_vars.append(var_name)
            elif var_name == 'kill':
                other_vars.append(f"{var_name} (EMERGENCY)")
            else:
                other_vars.append(var_name)

        # Display categorized variables
        if led_vars:
            print(f"\n💡 LED Variables ({len(led_vars)}):")
            for i, var in enumerate(sorted(led_vars), 1):
                if i <= 35:  # Only show first 35
                    print(f"   ✅ {var}")
                elif i == 36:
                    print(f"   ... and {len(led_vars) - 35} more")
                    break

        if button_vars:
            print(f"\n🔘 Button Variables ({len(button_vars)}):")
            for i, var in enumerate(sorted(button_vars), 1):
                if i <= 35:  # Only show first 35
                    print(f"   ✅ {var}")
                elif i == 36:
                    print(f"   ... and {len(button_vars) - 35} more")
                    break

        if other_vars:
            print(f"\n🔧 Other Variables ({len(other_vars)}):")
            for var in other_vars[:10]:  # Show first 10
                print(f"   📝 {var}")
            if len(other_vars) > 10:
                print(f"   ... and {len(other_vars) - 10} more")

        # Test reading a few variables
        print(f"\n🧪 Testing variable access...")

        if led_vars:
            try:
                test_led = await folder_node.get_child(f"4:{led_vars[0]}")
                value = await test_led.read_value()
                print(f"   ✅ {led_vars[0]} = {value}")
            except Exception as e:
                print(f"   ❌ Could not read {led_vars[0]}: {e}")

        if button_vars:
            try:
                test_button = await folder_node.get_child(f"4:{button_vars[0]}")
                value = await test_button.read_value()
                print(f"   ✅ {button_vars[0]} = {value}")
            except Exception as e:
                print(f"   ❌ Could not read {button_vars[0]}: {e}")

        if 'kill' in [v.split(' ')[0] for v in other_vars]:
            try:
                kill_node = await folder_node.get_child("4:kill")
                value = await kill_node.read_value()
                print(f"   ✅ kill = {value}")
            except Exception as e:
                print(f"   ❌ Could not read kill: {e}")

        print(f"\n🎉 Discovery completed!")
        print("   Variables are ready for AS/RS system")

    except Exception as e:
        print(f"❌ Error exploring variables: {e}")

async def test_connection():
    """Simple connection test"""
    print(f"🔗 Testing connection to {PLC_URL}...")

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Connection successful!")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🏗️ BVM AS/RS PLC Discovery Tool")
    print("=" * 40)
    print(f"PLC IP: {PLC_IP}")
    print(f"OPC UA URL: {PLC_URL}")
    print()

    # First test basic connection
    if asyncio.run(test_connection()):
        # If connection works, do full discovery
        asyncio.run(discover_variables())
    else:
        print("\n💡 Troubleshooting tips:")
        print("   - Check PLC power and network connection")
        print("   - Verify IP address is correct")
        print("   - Ensure OPC UA server is enabled in Sysmac Studio")
        print("   - Check firewall settings")
