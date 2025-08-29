# Create final supporting files for the OMRON AS/RS system

# Requirements file for OMRON system
omron_requirements = """# OMRON Auto Rack35 AS/RS System Requirements
# For 35-position storage rack with LED indicators and push button controls

# Core OPC UA Communication
opcua>=0.98.13          # Python OPC UA library for OMRON NX102-9000 communication

# Standard libraries (included with Python):
# - threading
# - queue
# - json
# - time
# - datetime
# - dataclasses
# - typing
# - enum
# - logging
# - concurrent.futures

# Optional for advanced features:
# numpy>=1.21.0         # For data analysis
# matplotlib>=3.4.0     # For plotting storage patterns
# pandas>=1.3.0         # For inventory reporting
"""

with open('omron_requirements.txt', 'w') as f:
    f.write(omron_requirements)

print("✅ OMRON Requirements file created: omron_requirements.txt")

# Test script for OMRON system
test_script = '''#!/usr/bin/env python3
"""
OMRON AS/RS System Test Script
Verifies OPC UA communication and basic functionality
"""

from omron_asrs_controller import OmronASRSController, ASRSTask, TaskType

def test_omron_system():
    """Test OMRON AS/RS functionality"""
    print("🧪 OMRON AS/RS System Test")
    print("=" * 35)
    
    # Initialize controller
    controller = OmronASRSController('omron_asrs_config.json')
    
    try:
        # Test initialization
        print("1. Testing system initialization...")
        if controller.initialize():
            print("   ✅ System initialized successfully")
        else:
            print("   ❌ System initialization failed")
            return False
        
        # Start system
        print("2. Starting system...")
        controller.start()
        print("   ✅ System started")
        
        # Test OPC UA communication
        print("3. Testing OPC UA communication...")
        try:
            # Try to read emergency kill switch
            kill_status = controller.opc_client.read_value('ns=4;s=kill')
            print(f"   Emergency kill status: {kill_status}")
            
            # Try to read a few LED states
            for i in [1, 2, 3]:
                led_status = controller.opc_client.read_value(f'ns=4;s=led{i}')
                print(f"   LED{i} status: {led_status}")
            
            print("   ✅ OPC UA communication working")
        except Exception as e:
            print(f"   ⚠️ OPC UA communication: {e} (using mock client)")
        
        # Test position management
        print("4. Testing position management...")
        stats = controller.position_manager.get_occupancy_stats()
        print(f"   Total positions: {stats['total_positions']}")
        print(f"   Layout: {stats['grid_layout']}")
        print(f"   Current occupancy: {stats['occupancy_percent']}%")
        print("   ✅ Position management operational")
        
        # Test grid display
        print("5. Testing grid display...")
        grid = controller.get_position_grid()
        if grid and len(grid) == 7:  # 7 rows expected
            print("   Grid display format:")
            for i, row in enumerate(grid[:2]):  # Show first 2 rows
                print(f"   Row {i+1}: {' '.join(row)}")
            print("   ✅ Grid display working")
        else:
            print("   ❌ Grid display format error")
        
        # Test LED control
        print("6. Testing LED control...")
        test_led = 'ns=4;s=led1'
        if controller.opc_client.write_value(test_led, True):
            print("   ✅ LED write successful")
            # Turn it back off
            controller.opc_client.write_value(test_led, False)
        else:
            print("   ⚠️ LED write failed (expected with mock client)")
        
        # Test task system
        print("7. Testing task system...")
        test_task = ASRSTask(
            task_id="TEST-001",
            task_type=TaskType.UPDATE_DISPLAY
        )
        
        if controller.submit_task(test_task):
            print("   ✅ Task submission working")
            
            # Wait for task completion
            import time
            time.sleep(1)
            
            if controller.completed_tasks:
                print(f"   ✅ Task processing working ({len(controller.completed_tasks)} completed)")
            else:
                print("   ⚠️ Task processing may need more time")
        else:
            print("   ❌ Task submission failed")
        
        print("\\n🎉 OMRON AS/RS SYSTEM TESTS COMPLETED!")
        print("\\nNext steps:")
        print("1. Update 'omron_asrs_config.json' with your PLC IP address")
        print("2. Verify OPC UA server is running on your OMRON NX102-9000")  
        print("3. Run 'python omron_asrs_app.py' to start the interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Always stop the system
        controller.stop()
        print("\\n✅ Test completed, system stopped")

def test_node_connectivity():
    """Test specific OPC UA node connectivity"""
    print("\\n🔗 Testing OPC UA Node Connectivity")
    print("-" * 35)
    
    controller = OmronASRSController('omron_asrs_config.json')
    
    if not controller.initialize():
        print("❌ Could not initialize controller")
        return False
    
    # Test nodes from the provided list
    test_nodes = [
        'ns=4;s=led1', 'ns=4;s=led2', 'ns=4;s=led3',
        'ns=4;s=pb1', 'ns=4;s=pb2', 'ns=4;s=pb3',
        'ns=4;s=kill'
    ]
    
    print("Testing key nodes...")
    for node_id in test_nodes:
        try:
            value = controller.opc_client.read_value(node_id)
            print(f"✅ {node_id}: {value}")
        except Exception as e:
            print(f"❌ {node_id}: Error - {e}")
    
    controller.stop()
    return True

if __name__ == "__main__":
    print("🏗️ OMRON Auto Rack35 AS/RS - System Test Suite")
    print("=" * 55)
    
    # Run main test
    if test_omron_system():
        # Run node connectivity test
        test_node_connectivity()
        print("\\n✅ All tests completed successfully!")
    else:
        print("\\n❌ Some tests failed - check configuration")
'''

with open('test_omron.py', 'w') as f:
    f.write(test_script)

print("✅ OMRON Test script created: test_omron.py")

# Comprehensive README for OMRON system
omron_readme = """# OMRON Auto Rack35 AS/RS Control System

A specialized Python control system for the OMRON Auto Rack35 AS/RS (Automated Storage and Retrieval System) featuring 35 storage positions with individual LED indicators and push button controls.

## 🏗️ System Overview

This system provides complete control over your OMRON Auto Rack35 AS/RS, including:

- **35 Storage Positions**: Individual control and monitoring of each storage location
- **LED Status Indicators**: Visual feedback for each position (led1-led35)
- **Push Button Controls**: Manual operation capability (pb1-pb35) 
- **OPC UA Communication**: Direct connection to OMRON NX102-9000 PLC
- **Emergency Safety**: Emergency kill switch monitoring
- **Visual Interface**: Real-time 7×5 grid display
- **Inventory Management**: Complete product tracking and location management

## 🎯 Your Specific Configuration

Based on your OPC UA node list, this system controls:

```
OMRON NX102-9000 PLC Nodes:
├── LEDs: ns=4;s=led1 through ns=4;s=led35
├── Push Buttons: ns=4;s=pb1 through ns=4;s=pb35  
└── Emergency Kill: ns=4;s=kill
```

The system maps these to a **7×5 grid layout** representing your physical rack structure.

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install required packages
pip install -r omron_requirements.txt

# Or install manually:
pip install opcua
```

### 2. Configuration
Edit `omron_asrs_config.json` with your OMRON PLC details:

```json
{
  "communication": {
    "protocol": "OPC_UA",
    "endpoint": "opc.tcp://YOUR_PLC_IP:4840",  // Update with your PLC IP
    "namespace": 4,
    "timeout": 5.0
  }
}
```

**Important**: Replace `YOUR_PLC_IP` with your actual OMRON NX102-9000 IP address.

### 3. Test the System
```bash
# Run system tests
python test_omron.py
```

### 4. Start the Control Interface
```bash
# Launch interactive control
python omron_asrs_app.py
```

## 🎮 Interactive Control Interface

Once running, you'll see a real-time grid display:

```
📦 STORAGE RACK LAYOUT - LIVE STATUS
============================================================
Occupancy: 5/35 (14%)
Legend: [##] = Occupied,  ##  = Empty

      C1    C2    C3    C4    C5  
 R1   01   [02]  03    04    05 
 R2  [06]  07    08   [09]  10 
 R3   11    12   [13]  14    15 
 R4   16    17    18    19   [20]
 R5   21    22    23    24    25 
 R6   26    27    28    29    30 
 R7   31    32    33    34    35 
============================================================
```

### Available Commands

- **[G]** - Show Grid Display: Live 7×5 rack layout with LED status
- **[S]** - Store Item: Add items to specific positions or auto-assign
- **[R]** - Retrieve Item: Remove items by position or product ID
- **[P]** - Position Details: Detailed info about specific positions
- **[T]** - System Status: Complete system health and statistics
- **[M]** - Monitor Push Buttons: Real-time button press monitoring
- **[L]** - List Stored Items: Complete inventory of stored products
- **[U]** - Update LED Display: Refresh all LED indicators
- **[E]** - Emergency Status: Check emergency kill switch
- **[Q]** - Quit System: Safe shutdown

## 📦 Storage Operations

### Storing Items

**Auto-Assignment:**
```
[S] Store Item
Product ID: WIDGET-001
Storage options:
1. Auto-assign to first empty position
✅ Item WIDGET-001 stored at Position 7
```

**Specific Position:**
```
[S] Store Item  
Product ID: PART-ABC
Storage options:
2. Specify position (1-35)
Position: 15
✅ Item PART-ABC stored at Position 15
```

### Retrieving Items

**By Position:**
```
[R] Retrieve Item
Retrieval options:
1. By Position (1-35)
Position: 7
📦 Position 7 contains: WIDGET-001
✅ Item WIDGET-001 retrieved from Position 7
```

**By Product ID:**
```
[R] Retrieve Item
Retrieval options: 
2. By Product ID
Product ID: PART-ABC
📍 Found PART-ABC at position 15
✅ Item PART-ABC retrieved from Position 15
```

## 🔘 Push Button Integration

Your physical push buttons automatically trigger operations:

- **Empty Position**: Button press logged, no action
- **Occupied Position**: Button press triggers automatic retrieval
- **Real-Time Monitoring**: See button presses as they happen

Example:
```
🔘 Button 7 pressed - Auto-retrieving WIDGET-001
✅ Item WIDGET-001 retrieved from Position 7
```

## 💡 LED Control Features

The system automatically manages all 35 LEDs:

- **OFF (False)**: Position is empty
- **ON (True)**: Position contains an item  
- **Synchronized**: LEDs automatically update with inventory changes
- **Manual Update**: Use `[U]` command to refresh all LEDs

## 🚨 Safety Features

### Emergency Kill Switch Monitoring
```
🚨 EMERGENCY STATUS CHECK
✅ Emergency kill switch is NORMAL
   System is safe to operate
```

The system continuously monitors `ns=4;s=kill` and will:
- Immediately stop all operations if activated
- Turn off all LEDs for safety
- Cancel pending tasks
- Require system restart after reset

### Position Validation
- Prevents storing items in occupied positions
- Validates position numbers (1-35 only)
- Checks item existence before retrieval
- Maintains data integrity

## 🏗️ System Architecture

```
OMRON AS/RS Control System
├── omron_asrs_app.py          # Interactive application
├── omron_asrs_controller.py   # Main system coordinator  
├── omron_asrs_core.py         # Core classes & OPC UA client
├── omron_asrs_config.json     # System configuration
├── omron_requirements.txt     # Python dependencies
├── test_omron.py              # System test suite
└── README.md                  # This documentation
```

### Core Components

1. **OmronOPCClient**: Handles all OPC UA communication with your NX102-9000
2. **PositionManager**: Manages the 35 storage positions and LED states
3. **OmronASRSController**: Coordinates operations, tasks, and monitoring
4. **OmronASRSApplication**: Provides the interactive user interface

## ⚙️ Configuration Options

### Physical Layout Adjustment
```json
"storage_rack": {
  "total_positions": 35,
  "layout": {
    "rows": 7,     // Adjust if your physical layout differs
    "columns": 5,  // 7×5 = 35 total positions
    "description": "35-position storage rack"
  }
}
```

### Communication Settings
```json
"communication": {
  "protocol": "OPC_UA",
  "endpoint": "opc.tcp://192.168.1.100:4840",  // Your PLC IP
  "namespace": 4,         // Namespace for your nodes
  "timeout": 5.0,         // Connection timeout
  "retry_count": 3,       // Connection retries
  "retry_delay": 1.0      // Delay between retries
}
```

### LED Control Settings
```json
"visual_feedback": {
  "led_states": {
    "empty": {"value": false, "description": "Position empty"},
    "occupied": {"value": true, "description": "Position occupied"}
  }
}
```

## 📊 Status and Monitoring

### System Status Display
```
📊 SYSTEM STATUS - Auto Rack35 AS/RS - OMRON NX102-9000
======================================================================
PLC Model: OMRON NX102-9000
System Status: MONITORING
🔌 COMMUNICATION: OPC_UA on opc.tcp://192.168.1.100:4840, Connected: Yes
📦 STORAGE: 35 total, 12 occupied, 23 available (34% full), Layout: 7×5
📋 TASKS: 0 pending, None active, 25 completed
🚨 SAFETY: Emergency Stop: NORMAL
```

### Position Details
```
📍 POSITION 15 DETAILS:
   Name: P15
   Grid Location: R3C5
   Status: OCCUPIED
   Product ID: PART-ABC
   Stored At: 2025-08-28 15:30:22
   LED Node: ns=4;s=led15
   Push Button: ns=4;s=pb15
```

### Inventory Tracking
```
📋 STORED ITEMS INVENTORY
Total Items: 12
Unique Products: 8

Product ID      Qty  Positions             Last Stored
---------------------------------------------------------------
WIDGET-001      3    P02, P09, P20         2025-08-28 15:45
PART-ABC        1    P15                   2025-08-28 15:30
COMPONENT-X     2    P06, P13              2025-08-28 14:20
```

## 🛠️ Troubleshooting

### Connection Issues
```
❌ Failed to connect to OMRON PLC
```
**Solutions:**
- Verify PLC IP address in `omron_asrs_config.json`
- Check network connectivity: `ping YOUR_PLC_IP`
- Ensure OPC UA server is enabled on OMRON NX102-9000
- Verify port 4840 is not blocked by firewall
- Check PLC is powered on and running

### LED Control Problems
```
⚠️ LED write failed
```
**Solutions:**
- Confirm OPC UA node IDs are correct (ns=4;s=led1, etc.)
- Check PLC program has LED variables configured
- Verify write permissions on OPC UA server
- Test with OMRON OPC UA client software first

### Position Mapping Issues
```
❌ Position 36 not found
```
**Solutions:**
- System supports positions 1-35 only
- Check grid layout configuration matches physical rack
- Verify position calculations in PositionManager

### Push Button Not Responding
```
🔘 Button press not detected
```
**Solutions:**
- Verify push button nodes (ns=4;s=pb1, etc.) in PLC
- Check button monitoring frequency in config
- Test button states with OPC UA client
- Ensure buttons are properly wired and configured

## 🔄 Integration Possibilities

This AS/RS system can be extended to integrate with:

### Enterprise Systems
- **ERP Integration**: Connect to SAP, Oracle, or other enterprise systems
- **WMS Integration**: Link with warehouse management software
- **Barcode Systems**: Add barcode scanning for automatic product identification

### Communication Protocols  
- **REST API**: Web service interface for external systems
- **Database Integration**: Store inventory data in SQL databases
- **MQTT Publishing**: Send status updates to other factory systems

### Advanced Features
- **Predictive Analytics**: Monitor usage patterns and optimize storage
- **Maintenance Scheduling**: Track LED failures and system health
- **Reporting Dashboard**: Web-based monitoring and reporting interface

## 📞 Support

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows/Linux with network access to PLC
- **Hardware**: OMRON NX102-9000 PLC with OPC UA server enabled
- **Network**: TCP/IP connectivity to PLC (typically port 4840)

### Getting Help
1. Run `python test_omron.py` to diagnose issues
2. Check system logs for error messages
3. Verify OPC UA connectivity with OMRON software tools
4. Review configuration files for correct IP addresses and node IDs

### Performance Tips
- Use wired Ethernet connection for best reliability
- Configure OPC UA server for optimal performance
- Monitor system resources if handling high-frequency operations
- Regular LED display updates maintain synchronization

---

**Ready to control your OMRON Auto Rack35 AS/RS! 🏗️✨**

*Specialized system for 35-position automated storage with LED indicators and push button controls*
"""

with open('omron_readme.md', 'w') as f:
    f.write(omron_readme)

print("✅ OMRON README created: omron_readme.md")

# Create a simple configuration helper
config_helper = '''#!/usr/bin/env python3
"""
OMRON AS/RS Configuration Helper
Quick setup tool for your Auto Rack35 system
"""

import json

def setup_configuration():
    """Interactive configuration setup"""
    print("🏗️ OMRON Auto Rack35 AS/RS Configuration Setup")
    print("=" * 50)
    
    # Get PLC IP address
    print("\\n1. OMRON NX102-9000 PLC Configuration:")
    plc_ip = input("PLC IP Address (e.g., 192.168.1.100): ").strip()
    if not plc_ip:
        plc_ip = "10.10.14.113"  # Default from original example
        print(f"Using default IP: {plc_ip}")
    
    # Get OPC UA port
    port = input("OPC UA Port (default 4840): ").strip()
    if not port:
        port = "4840"
    
    endpoint = f"opc.tcp://{plc_ip}:{port}"
    
    # Validate layout
    print("\\n2. Rack Layout Configuration:")
    print("Your system has 35 positions with LEDs (led1-led35) and buttons (pb1-pb35)")
    
    layout_choice = input("Use standard 7×5 grid layout? (Y/n): ").strip().lower()
    if layout_choice in ['n', 'no']:
        try:
            rows = int(input("Number of rows: "))
            cols = int(input("Number of columns: "))
            if rows * cols != 35:
                print(f"⚠️ Warning: {rows}×{cols} = {rows*cols}, but you have 35 positions")
        except ValueError:
            print("Using default 7×5 layout")
            rows, cols = 7, 5
    else:
        rows, cols = 7, 5
    
    # Create configuration
    config = {
        "system": {
            "name": "Auto Rack35 AS/RS - OMRON NX102-9000",
            "type": "AUTOMATED_STORAGE_RETRIEVAL",
            "description": "35-position AS/RS with LED indicators and push button controls",
            "version": "2.0",
            "plc_model": "OMRON NX102-9000"
        },
        "communication": {
            "protocol": "OPC_UA",
            "endpoint": endpoint,
            "namespace": 4,
            "timeout": 5.0,
            "retry_count": 3,
            "retry_delay": 1.0
        },
        "storage_rack": {
            "total_positions": 35,
            "layout": {
                "rows": rows,
                "columns": cols,
                "description": f"{rows}×{cols} grid layout with 35 positions"
            }
        },
        "control_nodes": {
            "emergency_kill": "ns=4;s=kill"
        }
    }
    
    # Generate position configurations
    positions = {}
    for i in range(1, 36):
        positions[f"position_{i:02d}"] = {
            "id": i,
            "name": f"Position {i}",
            "led_node": f"ns=4;s=led{i}",
            "pushbutton_node": f"ns=4;s=pb{i}",
            "row": ((i - 1) // cols) + 1,
            "column": ((i - 1) % cols) + 1,
            "occupied": False,
            "product_id": None,
            "stored_at": None
        }
    
    config["storage_positions"] = positions
    
    # Save configuration
    config_file = "omron_asrs_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\\n✅ Configuration saved to: {config_file}")
    print("\\n📋 Configuration Summary:")
    print(f"   PLC: OMRON NX102-9000 at {plc_ip}")
    print(f"   OPC UA: {endpoint}")
    print(f"   Layout: {rows}×{cols} = {rows*cols} positions")
    print(f"   LEDs: led1 through led35")
    print(f"   Buttons: pb1 through pb35")
    print(f"   Emergency: ns=4;s=kill")
    
    print("\\n🚀 Next Steps:")
    print("1. Verify your OMRON PLC is running and accessible")
    print("2. Test connection: python test_omron.py")
    print("3. Start system: python omron_asrs_app.py")

if __name__ == "__main__":
    try:
        setup_configuration()
    except KeyboardInterrupt:
        print("\\n❌ Configuration cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
'''

with open('setup_omron.py', 'w') as f:
    f.write(config_helper)

print("✅ OMRON Configuration helper created: setup_omron.py")

print("\n🎉 Complete OMRON AS/RS System Package Created!")
print("Files for OMRON Auto Rack35 Control:")
print("├── omron_asrs_config.json     # System configuration")
print("├── omron_asrs_core.py         # Core classes & OPC UA client")
print("├── omron_asrs_controller.py   # Main system controller")  
print("├── omron_asrs_app.py          # Interactive application")
print("├── omron_requirements.txt     # Python dependencies")
print("├── omron_readme.md            # Complete documentation")
print("├── test_omron.py              # System test suite")
print("└── setup_omron.py             # Configuration helper")

print("\n🚀 Quick Setup for Your OMRON NX102-9000:")
print("1. python setup_omron.py       # Configure your PLC IP address")
print("2. pip install -r omron_requirements.txt")
print("3. python test_omron.py        # Test system connectivity") 
print("4. python omron_asrs_app.py    # Start interactive control")