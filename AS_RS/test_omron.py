#!/usr/bin/env python3
"""
OMRON AS/RS System Test Script
Verifies OPC UA communication and basic functionality
"""

def test_omron_system():
    """Test OMRON AS/RS functionality"""
    print("🧪 OMRON AS/RS System Test")
    print("=" * 35)

    try:
        from omron_asrs_controller import OmronASRSController

        # Initialize controller
        controller = OmronASRSController('omron_asrs_config.json')

        # Test initialization
        print("1. Testing system initialization...")
        if controller.initialize():
            print("   ✅ System initialized successfully")
        else:
            print("   ❌ System initialization failed")
            return False

        controller.start()
        print("   ✅ System started")

        # Test basic functionality
        print("2. Testing OPC UA nodes...")
        kill_status = controller.opc_client.read_value('ns=4;s=kill')
        print(f"   Emergency kill: {kill_status}")

        led1_status = controller.opc_client.read_value('ns=4;s=led1') 
        print(f"   LED1 status: {led1_status}")

        print("3. Testing position management...")
        stats = controller.position_manager.get_occupancy_stats()
        print(f"   Total positions: {stats['total_positions']}")
        print(f"   Current occupancy: {stats['occupancy_percent']}%")

        print("\n🎉 BASIC TESTS PASSED!")
        print("\nNext steps:")
        print("1. Update IP address in omron_asrs_config.json")
        print("2. Run: python omron_asrs_app.py")

        controller.stop()
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_omron_system()
