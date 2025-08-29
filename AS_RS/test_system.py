"""
BVM AS/RS System Test
Test all components of the AS/RS system
"""

import asyncio
import sys
from asrs_controller import ASRSController

async def test_connection():
    """Test PLC connection"""
    print("🔗 Testing PLC Connection")
    print("-" * 30)

    controller = ASRSController()

    try:
        success = await controller.initialize()
        if success:
            print("   ✅ PLC connection successful")
            print(f"   ✅ Connected to {controller.config['plc']['url']}")
            await controller.stop()
            return True
        else:
            print("   ❌ PLC connection failed")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

async def test_variables():
    """Test variable access"""
    print("\n🔧 Testing Variable Access")
    print("-" * 30)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()

        # Test LED variables
        print("   Testing LED variables...")
        led_count = 0
        for i in range(1, 6):  # Test first 5 LEDs
            state = await controller.opc_client.read_led_state(i)
            if state is not None:
                led_count += 1
                print(f"   ✅ LED{i} = {state}")
            else:
                print(f"   ❌ LED{i} not accessible")

        # Test button variables
        print("   Testing button variables...")
        button_count = 0
        for i in range(1, 6):  # Test first 5 buttons
            state = await controller.opc_client.read_button_state(i)
            if state is not None:
                button_count += 1
                print(f"   ✅ PB{i} = {state}")
            else:
                print(f"   ❌ PB{i} not accessible")

        # Test emergency kill
        print("   Testing emergency kill...")
        kill_state = await controller.opc_client.read_emergency_kill()
        if kill_state is not None:
            print(f"   ✅ Emergency kill = {kill_state}")
        else:
            print(f"   ❌ Emergency kill not accessible")

        await controller.stop()

        print(f"\n   📊 Results: {led_count}/5 LEDs, {button_count}/5 buttons accessible")
        return led_count > 0 and button_count > 0

    except Exception as e:
        print(f"   ❌ Variable test error: {e}")
        await controller.stop()
        return False

async def test_led_control():
    """Test LED control"""
    print("\n💡 Testing LED Control")
    print("-" * 30)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()

        # Test writing to LED1
        print("   Testing LED1 control...")

        # Turn on LED1
        success = await controller.opc_client.write_led_state(1, True)
        if success:
            print("   ✅ LED1 turned ON")
            await asyncio.sleep(1)

            # Turn off LED1
            success = await controller.opc_client.write_led_state(1, False)
            if success:
                print("   ✅ LED1 turned OFF")
                await controller.stop()
                return True
            else:
                print("   ❌ Could not turn OFF LED1")
        else:
            print("   ❌ Could not turn ON LED1")

        await controller.stop()
        return False

    except Exception as e:
        print(f"   ❌ LED control test error: {e}")
        await controller.stop()
        return False

async def test_system_operations():
    """Test system operations"""
    print("\n⚙️ Testing System Operations")
    print("-" * 30)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()

        # Test position manager
        print("   Testing position manager...")
        stats = controller.position_manager.get_statistics()
        print(f"   ✅ {stats['total_positions']} positions initialized")

        # Test grid display
        print("   Testing grid display...")
        grid = controller.position_manager.get_grid_display()
        print(f"   ✅ Grid display: {len(grid)} rows")

        # Test task submission
        print("   Testing task submission...")
        success = await controller.update_display()
        if success:
            print("   ✅ Task submission working")
        else:
            print("   ❌ Task submission failed")

        # Wait a moment for task processing
        await asyncio.sleep(2)

        # Test system status
        print("   Testing system status...")
        status = controller.get_system_status()
        print(f"   ✅ System status: {status['status']}")

        await controller.stop()
        return True

    except Exception as e:
        print(f"   ❌ System operations test error: {e}")
        await controller.stop()
        return False

async def run_all_tests():
    """Run all system tests"""
    print("🧪 BVM AS/RS System Tests")
    print("=" * 40)
    print(f"Testing connection to PLC at 10.10.14.104")
    print()

    tests = [
        ("Connection Test", test_connection),
        ("Variable Access Test", test_variables),
        ("LED Control Test", test_led_control),
        ("System Operations Test", test_system_operations)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            results.append((test_name, False))

        await asyncio.sleep(0.5)  # Brief pause between tests

    # Display summary
    print("\n" + "="*40)
    print("📊 TEST RESULTS SUMMARY")
    print("="*40)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("   Your BVM AS/RS system is ready for operation")
        print("   Run: python asrs_app.py")
    else:
        print("\n⚠️ Some tests failed")
        if passed == 0:
            print("   - Check PLC connection and OPC UA server")
            print("   - Run: python discover_plc.py")
        elif passed < len(tests):
            print("   - Check variable configuration in PLC")
            print("   - Verify LED/button nodes exist")

    return passed == len(tests)

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
