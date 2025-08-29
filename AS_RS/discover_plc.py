"""
BVM AS/RS PLC Discovery - Using User's Proven Pattern
Exact replication of user's working discover_path.py approach
"""

import asyncio
from asyncua import Client

# User's proven configuration - exact copy
PLC_IP = "10.10.14.104"
PLC_URL = f"opc.tcp://{PLC_IP}:4840"
KNOWN_PATH = ["0:Objects", "4:new_Controller_0"]

async def discover():
    """User's proven discovery function - exact copy"""
    print(f"Connecting to {PLC_URL}...")
    try:
        async with Client(url=PLC_URL) as client:
            print("Successfully connected!")

            # --- Navigate to the known correct folder ---
            current_node = client.get_objects_node()
            for part in KNOWN_PATH[1:]: # Start from the second item
                try:
                    current_node = await current_node.get_child(part)
                except Exception as e:
                    print(f"Error: Could not navigate to '{part}'. Double check KNOWN_PATH. Error: {e}")
                    return
            print(f"\n--- Contents of the '{KNOWN_PATH[-1]}' Folder ---")
            print("Look for the name that holds all your variables (like Global_Variables, Tags, etc.)")
            print("--------------------------------------------------")
            # --- Get and print the children of the last known folder ---
            children = await current_node.get_children()

            if not children:
                print("This folder is empty.")

            for child in children:
                browse_name = await child.read_browse_name()
                print(f"Name: '{browse_name.Name}', Namespace Index: {browse_name.NamespaceIndex}")

            print("\n--------------------------------------------------")
            print("Use one of these names to update the final part of the path in plc_monitor.py.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def enhanced_discovery():
    """Enhanced discovery with AS/RS analysis"""
    print(f"🔍 BVM AS/RS PLC Discovery (User's Proven Pattern)")
    print("=" * 55)
    print(f"Target PLC: {PLC_IP}")
    print(f"OPC UA URL: {PLC_URL}")
    print("Using your exact working connection pattern...")
    print()

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Successfully connected using proven pattern!")

            # Use user's exact navigation method
            current_node = client.get_objects_node()
            for part in KNOWN_PATH[1:]:
                try:
                    current_node = await current_node.get_child(part)
                    print(f"✅ Navigated to: {part}")
                except Exception as e:
                    print(f"❌ Could not navigate to '{part}': {e}")
                    return False

            print(f"\n📂 Contents of '{KNOWN_PATH[-1]}' folder:")
            print("=" * 50)

            children = await current_node.get_children()
            if not children:
                print("📭 This folder is empty")
                return False

            # Find variables folder
            variables_folder = None
            print("Available folders:")
            for child in children:
                browse_name = await child.read_browse_name()
                print(f"   📁 {browse_name.Name} (namespace: {browse_name.NamespaceIndex})")

                # Check if this might be variables folder
                if any(keyword in browse_name.Name.lower() for keyword in ['global', 'vars', 'variables', 'tags']):
                    variables_folder = child
                    print(f"      👆 This looks like the variables folder!")

            if not variables_folder:
                print("\n⚠️ No obvious variables folder found")
                return False

            # Explore variables using user's proven method
            print(f"\n🔍 Exploring Variables Folder...")
            variables_to_monitor = await variables_folder.get_children()

            if not variables_to_monitor:
                print("❌ Variables folder is empty")
                return False

            print(f"Found {len(variables_to_monitor)} variables:")

            # Categorize variables for AS/RS
            leds = []
            buttons = []
            emergency = []
            other = []

            # Read and categorize using user's pattern
            for var_node in variables_to_monitor:
                try:
                    browse_name = await var_node.read_browse_name()
                    var_name = browse_name.Name

                    # Try to read initial value (user's pattern)
                    try:
                        value = await var_node.get_value()
                        value_str = f" = {bool(value)}"
                    except Exception:
                        value_str = " (could not read)"

                    # Categorize for AS/RS
                    if var_name.startswith('led') and var_name[3:].isdigit():
                        leds.append((var_name, value_str, int(var_name[3:])))
                    elif var_name.startswith('pb') and var_name[2:].isdigit():
                        buttons.append((var_name, value_str, int(var_name[2:])))
                    elif var_name.lower() in ['kill', 'emergency', 'estop']:
                        emergency.append((var_name, value_str))
                    else:
                        other.append((var_name, value_str))

                except Exception as e:
                    print(f"   ❌ Error reading {var_name}: {e}")

            # Display results
            print(f"\n📊 AS/RS Variable Analysis:")
            print("=" * 40)

            # LED Variables
            if leds:
                leds.sort(key=lambda x: x[2])  # Sort by number
                print(f"\n💡 LED Variables ({len(leds)} found):")
                for var_name, value_str, num in leds[:10]:  # Show first 10
                    print(f"   ✅ {var_name}{value_str}")
                if len(leds) > 10:
                    print(f"   ... and {len(leds) - 10} more LEDs")

                # Check range
                led_numbers = [num for _, _, num in leds]
                if led_numbers:
                    led_range = f"LED{min(led_numbers)}-{max(led_numbers)}"
                    print(f"   📊 Range: {led_range}")

                    # Check for missing LEDs
                    expected = set(range(1, 36))  # AS/RS expects 1-35
                    actual = set(led_numbers)
                    missing = expected - actual
                    if missing and len(missing) < 10:
                        print(f"   ⚠️ Missing: LED{sorted(list(missing))}")
            else:
                print("\n💡 LED Variables: ❌ None found")

            # Button Variables
            if buttons:
                buttons.sort(key=lambda x: x[2])  # Sort by number
                print(f"\n🔘 Button Variables ({len(buttons)} found):")
                for var_name, value_str, num in buttons[:10]:  # Show first 10
                    print(f"   ✅ {var_name}{value_str}")
                if len(buttons) > 10:
                    print(f"   ... and {len(buttons) - 10} more buttons")

                # Check range
                button_numbers = [num for _, _, num in buttons]
                if button_numbers:
                    button_range = f"PB{min(button_numbers)}-{max(button_numbers)}"
                    print(f"   📊 Range: {button_range}")
            else:
                print("\n🔘 Button Variables: ❌ None found")

            # Emergency Variables
            if emergency:
                print(f"\n🚨 Emergency Variables:")
                for var_name, value_str in emergency:
                    print(f"   ✅ {var_name}{value_str}")
            else:
                print("\n🚨 Emergency Variables: ❌ None found")

            # Other Variables
            if other:
                print(f"\n🔧 Other Variables ({len(other)} found):")
                for var_name, value_str in other[:10]:  # Show first 10
                    print(f"   📝 {var_name}{value_str}")
                if len(other) > 10:
                    print(f"   ... and {len(other) - 10} more variables")

            # AS/RS Compatibility Assessment
            print(f"\n⚙️ AS/RS System Compatibility:")
            print("=" * 35)

            led_count = len(leds)
            button_count = len(buttons)
            has_emergency = len(emergency) > 0

            print(f"   LEDs: {led_count}/35 {'✅' if led_count >= 35 else '⚠️' if led_count > 0 else '❌'}")
            print(f"   Buttons: {button_count}/35 {'✅' if button_count >= 35 else '⚠️' if button_count > 0 else '❌'}")
            print(f"   Emergency: {'✅' if has_emergency else '❌'}")

            if led_count >= 35 and button_count >= 35 and has_emergency:
                print("\n🎉 PERFECT! Your PLC is fully compatible with the BVM AS/RS system!")
                print("   All 35 positions can be controlled with LEDs and buttons")
                print("   Emergency safety system is available")
            elif led_count > 0 or button_count > 0:
                print("\n⚠️ PARTIAL COMPATIBILITY")
                print(f"   System will work with {min(led_count, button_count)} positions")
                if not has_emergency:
                    print("   ❌ Emergency safety system not found")
            else:
                print("\n❌ NO AS/RS VARIABLES FOUND")
                print("   Check PLC programming and variable names")

            # Path Information for AS/RS Configuration
            print(f"\n📋 Configuration Information:")
            print("=" * 30)
            print(f"   Proven Path: {KNOWN_PATH} → GlobalVars")
            print(f"   Full Path: {KNOWN_PATH + ['4:GlobalVars']}")
            print(f"   Variable Count: {len(variables_to_monitor)}")

            if has_emergency:
                emergency_name = emergency[0][0]  # First emergency variable name
                print(f"   Emergency Variable: '{emergency_name}'")

            return True

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

async def test_variable_monitoring():
    """Test variable monitoring using user's proven pattern"""
    print(f"\n🧪 Testing Variable Monitoring (User's Proven Pattern)")
    print("=" * 60)
    print("This will demonstrate real-time variable monitoring...")
    print("Press Ctrl+C to stop")
    print()

    try:
        async with Client(url=PLC_URL) as client:
            print("✅ Connected for monitoring test")

            # Navigate using proven method
            current_node = client.get_objects_node()
            for part in KNOWN_PATH[1:]:
                current_node = await current_node.get_child(part)

            # Find GlobalVars
            children = await current_node.get_children()
            variables_folder = None
            for child in children:
                browse_name = await child.read_browse_name()
                if 'global' in browse_name.Name.lower():
                    variables_folder = child
                    break

            if not variables_folder:
                print("❌ Could not find variables folder")
                return

            # Get variables to monitor (user's pattern)
            variables_to_monitor = await variables_folder.get_children()
            if not variables_to_monitor:
                print("❌ No variables to monitor")
                return

            print(f"Monitoring {len(variables_to_monitor)} variables...")
            print("==================================================")
            print(">>> Go to the HMI and press a button now! <<<")
            print("==================================================")

            # Read initial state (user's exact pattern)
            initial_states = {}
            for var_node in variables_to_monitor:
                name = (await var_node.read_browse_name()).Name
                try:
                    value = await var_node.get_value()
                    initial_states[name] = value
                except Exception as e:
                    print(f"Warning: Could not read initial value for '{name}': {e}")

            print("Initial state recorded. Monitoring for changes...")

            # Monitor for changes (user's exact pattern)
            while True:
                for var_node in variables_to_monitor:
                    name = (await var_node.read_browse_name()).Name

                    if name not in initial_states:
                        continue

                    try:
                        new_value = await var_node.get_value()
                        old_value = initial_states[name]
                        if new_value != old_value:
                            print("\n*** CHANGE DETECTED! ***")
                            print(f"   Variable: '{name}'")
                            print(f"   Old Value: {old_value}")
                            print(f"   New Value: {new_value}")
                            print("************************")
                            initial_states[name] = new_value
                    except Exception as e:
                        print(f"Error reading variable '{name}': {e}")
                        if name in initial_states:
                            del initial_states[name]

                await asyncio.sleep(0.1)  # User's proven scan rate

    except KeyboardInterrupt:
        print("\n⏹️ Monitoring test stopped by user")
    except Exception as e:
        print(f"❌ Monitoring test error: {e}")

async def main():
    """Main function with options"""
    print("🔍 BVM AS/RS PLC Discovery Tool")
    print("Using your proven asyncua connection pattern")
    print("=" * 50)

    print("\nSelect discovery mode:")
    print("1. Basic discovery (your original method)")
    print("2. Enhanced AS/RS analysis")
    print("3. Test variable monitoring")

    try:
        choice = input("\nEnter choice (1, 2, or 3): ").strip()

        if choice == "1":
            print("\n🚀 Running basic discovery (your proven method)...")
            await discover()

        elif choice == "2":
            print("\n🚀 Running enhanced AS/RS analysis...")
            success = await enhanced_discovery()

            if success:
                print("\n🎉 Discovery completed successfully!")
                print("\nNext steps:")
                print("   1. python test_system.py     # Test full system")
                print("   2. python asrs_app.py        # Start AS/RS system")

        elif choice == "3":
            print("\n🚀 Testing variable monitoring...")
            await test_variable_monitoring()

        else:
            print("❌ Invalid choice")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n❌ Discovery cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)
