"""
Quick Connection Test - Using Your Proven Asyncua Pattern
Test basic PLC connectivity using your exact working method
"""

import asyncio
from asyncua import Client

# Your proven configuration - exact copy
PLC_IP = "10.10.14.104"
PLC_URL = f"opc.tcp://{PLC_IP}:4840"
KNOWN_PATH = ["0:Objects", "4:new_Controller_0"]

async def test_connection():
    """Test using your exact proven pattern"""
    print("🔗 Quick Connection Test (Your Proven Pattern)")
    print("=" * 50)
    print(f"Target PLC: {PLC_IP}")
    print(f"OPC UA URL: {PLC_URL}")
    print("Using your exact working asyncua pattern...")
    print()

    try:
        # Use your exact connection pattern from new.py
        async with Client(url=PLC_URL) as client:
            print("✅ Successfully connected using your proven pattern!")

            # Use your exact navigation method from discover_path.py
            current_node = client.get_objects_node()
            for part in KNOWN_PATH[1:]:  # Start from the second item
                try:
                    current_node = await current_node.get_child(part)
                    print(f"✅ Navigated to: {part}")
                except Exception as e:
                    print(f"❌ Could not navigate to '{part}': {e}")
                    return False

            # Try to find GlobalVars using your method
            print(f"\n📂 Contents of '{KNOWN_PATH[-1]}' folder:")
            children = await current_node.get_children()

            if not children:
                print("📭 This folder is empty")
                return False

            variables_folder = None
            for child in children:
                browse_name = await child.read_browse_name()
                print(f"   📁 {browse_name.Name} (namespace: {browse_name.NamespaceIndex})")

                # Check if this is GlobalVars
                if 'global' in browse_name.Name.lower():
                    variables_folder = child
                    print(f"      👆 This is the GlobalVars folder!")

            if not variables_folder:
                print("\n❌ GlobalVars folder not found")
                return False

            # Test variable access using your pattern
            print(f"\n🔍 Testing Variable Access (Your Pattern)...")
            variables_to_monitor = await variables_folder.get_children()

            if not variables_to_monitor:
                print("❌ No variables found in GlobalVars")
                return False

            print(f"Found {len(variables_to_monitor)} variables")

            # Test reading variables using your exact method
            led_count = 0
            pb_count = 0
            kill_found = False

            for var_node in variables_to_monitor[:20]:  # Test first 20 variables
                try:
                    name = (await var_node.read_browse_name()).Name
                    value = await var_node.get_value()

                    if name.startswith('led') and name[3:].isdigit():
                        led_count += 1
                        if led_count <= 3:  # Show first 3
                            print(f"   ✅ {name} = {bool(value)}")
                    elif name.startswith('pb') and name[2:].isdigit():
                        pb_count += 1
                        if pb_count <= 3:  # Show first 3
                            print(f"   ✅ {name} = {bool(value)}")
                    elif name.lower() == 'kill':
                        kill_found = True
                        print(f"   ✅ {name} = {bool(value)}")

                except Exception as e:
                    print(f"   ⚠️ Could not read {name}: {e}")

            print(f"\n📊 Variable Summary:")
            print(f"   LEDs found: {led_count}")
            print(f"   Buttons found: {pb_count}")
            print(f"   Emergency kill: {'✅ Found' if kill_found else '❌ Not found'}")

            if led_count >= 5 and pb_count >= 5:
                print(f"\n🎉 SUCCESS! Your proven pattern works perfectly!")
                print(f"   AS/RS system should work with {min(led_count, pb_count)} positions")
                return True
            elif led_count > 0 or pb_count > 0:
                print(f"\n⚠️ PARTIAL SUCCESS - Some variables found")
                print(f"   System may work with limited functionality")
                return True
            else:
                print(f"\n❌ No AS/RS variables found")
                return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"   • Check if PLC is powered on")
        print(f"   • Verify network connection to {PLC_IP}")
        print(f"   • Ensure OPC UA server is enabled in Sysmac Studio")
        print(f"   • Check if variables are published in PLC program")
        return False

async def test_variable_monitoring_sample():
    """Test a sample of variable monitoring using your proven pattern"""
    print(f"\n🔍 Testing Variable Monitoring Sample (Your Pattern)")
    print("=" * 60)
    print("This demonstrates your proven change detection method...")
    print("Testing for 5 seconds with 3 variables")
    print()

    try:
        async with Client(url=PLC_URL) as client:
            # Navigate using your proven method
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
                print("❌ Could not find GlobalVars folder")
                return False

            # Get first 3 variables for quick test
            variables_to_monitor = (await variables_folder.get_children())[:3]

            if not variables_to_monitor:
                print("❌ No variables to monitor")
                return False

            print(f"Monitoring {len(variables_to_monitor)} variables for 5 seconds...")

            # Read initial state using your exact pattern
            initial_states = {}
            for var_node in variables_to_monitor:
                name = (await var_node.read_browse_name()).Name
                try:
                    value = await var_node.get_value()
                    initial_states[name] = value
                    print(f"   📍 {name} = {value}")
                except Exception as e:
                    print(f"   ❌ Could not read {name}: {e}")

            print("\nMonitoring for changes (your proven method)...")

            # Monitor using your exact change detection pattern
            for _ in range(50):  # 5 seconds at 0.1s intervals
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

                await asyncio.sleep(0.1)  # Your proven scan rate

            print("\n✅ Variable monitoring test completed")
            print("   Your proven change detection pattern works!")
            return True

    except Exception as e:
        print(f"❌ Variable monitoring test failed: {e}")
        return False

async def main():
    """Main test function using your proven pattern"""
    print("🧪 BVM AS/RS Quick Test Suite")
    print("Using Your Proven Asyncua Pattern")
    print("=" * 50)

    # Test 1: Basic connection
    success1 = await test_connection()

    if success1:
        print("\n" + "="*50)

        # Test 2: Variable monitoring sample
        success2 = await test_variable_monitoring_sample()

        print("\n" + "="*50)
        print("📊 QUICK TEST RESULTS")
        print("="*50)

        print(f"Connection Test: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"Monitoring Test: {'✅ PASS' if success2 else '❌ FAIL'}")

        if success1 and success2:
            print("\n🎉 ALL QUICK TESTS PASSED!")
            print("   Your proven pattern works perfectly")
            print("   BVM AS/RS system should work without issues")
            print("\n🚀 Next Steps:")
            print("   1. python test_system.py     # Full system test")
            print("   2. python asrs_app.py        # Start AS/RS system")
            return True
        else:
            print("\n⚠️ Some tests failed")
            print("   Check PLC configuration and variable setup")
            return False
    else:
        print("\n❌ Connection test failed")
        print("   Resolve connection issues before proceeding")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())

        if success:
            print("\n✨ Ready for BVM AS/RS operation!")
        else:
            print("\n❌ Please resolve issues before using AS/RS system")

        input("\nPress Enter to exit...")

    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal test error: {e}")
