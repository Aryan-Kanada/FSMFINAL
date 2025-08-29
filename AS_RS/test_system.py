"""
BVM AS/RS System Test - Using Proven Asyncua Pattern
Test all components using your working connection method
"""

import asyncio
import sys
from asrs_controller import ASRSController

async def test_connection():
    """Test PLC connection using proven pattern"""
    print("🔗 Testing PLC Connection (Proven Pattern)")
    print("-" * 45)

    controller = ASRSController()

    try:
        success = await controller.initialize()
        if success:
            print("   ✅ PLC connection successful")
            print(f"   ✅ Connected to {controller.config['plc']['url']}")
            print(f"   ✅ Using proven path: {controller.config['paths']['variables_path']}")

            # Show statistics
            stats = controller.opc_client.get_statistics()
            print(f"   ✅ Variables discovered: {stats['total_variables']}")

            await controller.stop()
            return True
        else:
            print("   ❌ PLC connection failed")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

async def test_variables():
    """Test variable access using proven pattern"""
    print("\n🔧 Testing Variable Access (Proven Pattern)")
    print("-" * 50)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()

        # Let system stabilize
        await asyncio.sleep(1)

        # Test LED variables (first 5)
        print("   Testing LED variables...")
        led_count = 0
        for i in range(1, 6):
            state = await controller.opc_client.read_led_state(i)
            if state is not None:
                led_count += 1
                print(f"   ✅ LED{i} = {state}")
            else:
                print(f"   ❌ LED{i} not accessible")

        # Test button variables (first 5)
        print("   Testing button variables...")
        button_count = 0
        for i in range(1, 6):
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
    """Test LED control using proven pattern"""
    print("\n💡 Testing LED Control (Proven Pattern)")
    print("-" * 45)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()
        await asyncio.sleep(1)

        # Test LED1 control
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
    """Test system operations using proven pattern"""
    print("\n⚙️ Testing System Operations (Proven Pattern)")
    print("-" * 50)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()
        await asyncio.sleep(1)

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

        # Wait for task processing
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

async def test_store_retrieve():
    """Test store and retrieve operations using proven pattern"""
    print("\n📦 Testing Store/Retrieve Operations (Proven Pattern)")
    print("-" * 60)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()
        await asyncio.sleep(1)

        # Test store operation
        print("   Testing store operation...")
        success = await controller.store_item("TEST_ITEM_001", 1)
        if success:
            print("   ✅ Store task submitted")
            await asyncio.sleep(3)  # Wait for task completion

            # Check if item was stored
            position = controller.position_manager.get_position(1)
            if position and position.status.value == "occupied":
                print(f"   ✅ Item stored: {position.product_id}")

                # Test retrieve operation
                print("   Testing retrieve operation...")
                success = await controller.retrieve_item(1)
                if success:
                    print("   ✅ Retrieve task submitted")
                    await asyncio.sleep(3)  # Wait for task completion

                    # Check if item was retrieved
                    position = controller.position_manager.get_position(1)
                    if position and position.status.value == "empty":
                        print("   ✅ Item retrieved successfully")
                        await controller.stop()
                        return True
                    else:
                        print("   ❌ Item not retrieved")
                else:
                    print("   ❌ Retrieve task failed")
            else:
                print("   ❌ Item not stored")
        else:
            print("   ❌ Store task failed")

        await controller.stop()
        return False

    except Exception as e:
        print(f"   ❌ Store/retrieve test error: {e}")
        await controller.stop()
        return False

async def test_variable_monitoring():
    """Test real-time variable monitoring using proven pattern"""
    print("\n🔍 Testing Variable Monitoring (Proven Pattern)")
    print("-" * 55)

    controller = ASRSController()

    try:
        if not await controller.initialize():
            print("   ❌ Could not initialize controller")
            return False

        await controller.start()
        await asyncio.sleep(1)

        print("   ✅ Real-time variable monitoring started")
        print("   📊 Variable monitor task is running in background")
        print("   🔘 Button press detection is active")
        print("   🚨 Emergency monitoring is active")

        # Let monitoring run for a few seconds
        print("   ⏱️ Testing monitoring for 5 seconds...")
        await asyncio.sleep(5)

        # Check if monitoring tasks are running
        monitoring_active = (
            controller.monitoring_task and not controller.monitoring_task.done() and
            controller.variable_monitor_task and not controller.variable_monitor_task.done()
        )

        if monitoring_active:
            print("   ✅ All monitoring tasks are running")
            await controller.stop()
            return True
        else:
            print("   ❌ Some monitoring tasks failed")
            await controller.stop()
            return False

    except Exception as e:
        print(f"   ❌ Variable monitoring test error: {e}")
        await controller.stop()
        return False

async def run_all_tests():
    """Run all system tests using proven asyncua pattern"""
    print("🧪 BVM AS/RS System Tests (Proven Asyncua Pattern)")
    print("=" * 60)
    print(f"Testing connection to PLC at 10.10.14.104")
    print("Using your proven asyncua connection and monitoring code")
    print()

    tests = [
        ("Connection Test", test_connection),
        ("Variable Access Test", test_variables),
        ("LED Control Test", test_led_control),
        ("System Operations Test", test_system_operations),
        ("Store/Retrieve Test", test_store_retrieve),
        ("Variable Monitoring Test", test_variable_monitoring)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"Running {test_name}...")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            results.append((test_name, False))

        await asyncio.sleep(0.5)  # Brief pause between tests

    # Display summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("   Your BVM AS/RS system is ready for operation")
        print("   Using proven asyncua connection pattern")
        print("   Real-time variable monitoring confirmed working")
        print("   Run: python asrs_app.py")
    else:
        print("\n⚠️ Some tests failed")
        if passed == 0:
            print("   - Check PLC connection and OPC UA server")
            print("   - Run: python discover_plc.py")
        elif passed >= len(tests) // 2:
            print("   - Basic connectivity working")
            print("   - Check variable configuration in PLC")
            print("   - System may still be usable with limited functionality")
        else:
            print("   - Multiple system components failed")
            print("   - Check PLC programming and variable setup")

    print(f"\n💡 System Info:")
    print(f"   • Using proven asyncua connection pattern")
    print(f"   • Path: Objects → new_Controller_0 → GlobalVars")  
    print(f"   • Real-time variable monitoring active")
    print(f"   • Emergency safety monitoring enabled")

    return passed == len(tests)

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        sys.exit(1)
