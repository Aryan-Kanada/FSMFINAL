# OMRON Auto Rack35 AS/RS Control System

A specialized Python control system for the OMRON Auto Rack35 AS/RS (Automated Storage and Retrieval System) featuring 35 storage positions with individual LED indicators and push button controls via OPC UA communication.

## 🏗️ System Overview

This system provides complete automated control over your OMRON Auto Rack35 AS/RS, including:

- **35 Storage Positions**: Individual control and monitoring of each storage location
- **LED Status Indicators**: Visual feedback for each position (`led1-led35`)
- **Push Button Controls**: Manual operation capability (`pb1-pb35`) 
- **OPC UA Communication**: Direct connection to OMRON NX102-9000 PLC
- **Emergency Safety**: Emergency kill switch monitoring (`ns=4;s=kill`)
- **Visual Interface**: Real-time 7×5 grid display
- **Inventory Management**: Complete product tracking and location management

## 🎯 Your Specific Hardware Integration

Based on your OPC UA node specifications, this system controls:

```
OMRON NX102-9000 PLC Nodes:
├── LEDs: ns=4;s=led1 through ns=4;s=led35    (Position indicators)
├── Push Buttons: ns=4;s=pb1 through ns=4;s=pb35  (Manual controls)
└── Emergency Kill: ns=4;s=kill                (Safety shutdown)
```

The system maps these to a **7×5 grid layout** representing your physical rack structure.

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Network access to your OMRON NX102-9000 PLC
- OPC UA server enabled on the PLC

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install opcua
   ```

2. **Download the system files:**
   - `omron_asrs_core.py` - Core classes and OPC UA client
   - `omron_asrs_controller.py` - Main system coordinator
   - `omron_asrs_app.py` - Interactive control interface
   - `omron_asrs_config.json` - System configuration
   - `setup_omron.py` - Configuration helper
   - `test_omron.py` - System test suite

### Configuration

1. **Set up your PLC connection:**
   ```bash
   python setup_omron.py
   ```
   Enter your OMRON NX102-9000 IP address when prompted.

2. **Or manually edit `omron_asrs_config.json`:**
   ```json
   {
     "communication": {
       "protocol": "OPC_UA",
       "endpoint": "opc.tcp://YOUR_PLC_IP:4840",
       "namespace": 4,
       "timeout": 5.0
     }
   }
   ```

### Testing

1. **Test system connectivity:**
   ```bash
   python test_omron.py
   ```

2. **Verify OPC UA nodes are accessible:**
   - Emergency kill switch (`ns=4;s=kill`)
   - LED controls (`ns=4;s=led1`, `ns=4;s=led2`, etc.)
   - Push button status (`ns=4;s=pb1`, `ns=4;s=pb2`, etc.)

### Starting the System

```bash
python omron_asrs_app.py
```

## 🎮 Interactive Control Interface

Once running, you'll see a real-time grid display and command interface:

```
🏗️ OMRON AUTO RACK35 AS/RS CONTROL SYSTEM
================================================================================
   PLC: OMRON NX102-9000
   Positions: 35
   Layout: 7×5 grid
================================================================================

📦 STORAGE RACK LAYOUT - LIVE STATUS
============================================================
Occupancy: 8/35 (23%)
Legend: [##] = Occupied,  ##  = Empty

      C1    C2    C3    C4    C5  
 R1  [01]  02    03   [04]  05 
 R2   06   [07]  08    09   [10]
 R3   11    12   [13]  14    15 
 R4   16   [17]  18    19    20 
 R5   21    22    23   [24]  25 
 R6   26    27    28    29    30 
 R7   31    32    33    34    35 
============================================================

📖 AVAILABLE COMMANDS:
  [G] → Show Grid Display      [S] → Store Item
  [R] → Retrieve Item          [P] → Position Details
  [T] → System Status          [M] → Monitor Push Buttons
  [L] → List Stored Items      [U] → Update LED Display
  [E] → Emergency Status       [H] → Help
  [Q] → Quit System

Enter command:
```

## 📦 Storage Operations

### Store Item

**Auto-Assignment:**
```
[S] Store Item
Product ID: WIDGET-001
Storage options:
1. Auto-assign to first empty position
2. Specify position (1-35)

Select option (1 or 2): 1
✅ Storage task submitted for WIDGET-001
⏱️  Storing WIDGET-001... (2.3s)
✅ Item stored successfully
```

**Specific Position:**
```
[S] Store Item  
Product ID: PART-ABC
Storage options:
1. Auto-assign to first empty position
2. Specify position (1-35)

Select option (1 or 2): 2
Position (1-35): 15
✅ Storage task submitted: PART-ABC → Position 15
⏱️  Storing... (1.8s)
✅ Item stored successfully
```

### Retrieve Item

**By Position:**
```
[R] Retrieve Item
Retrieval options:
1. By Position (1-35)
2. By Product ID

Select option (1 or 2): 1
Position (1-35): 15
📦 Position 15 contains: PART-ABC
Retrieve this item? (y/N): y
✅ Retrieval task submitted for position 15
⏱️  Retrieving... (1.5s)
✅ Item retrieved successfully
```

**By Product ID:**
```
[R] Retrieve Item
Retrieval options:
1. By Position (1-35)
2. By Product ID

Select option (1 or 2): 2
Product ID: WIDGET-001
📍 Found WIDGET-001 at position 7
📅 Stored at: 2025-08-28 15:30:22
Retrieve this item? (y/N): y
✅ Retrieval task submitted for WIDGET-001
⏱️  Retrieving... (2.1s)
✅ Item retrieved successfully
```

## 🔘 Push Button Integration

Your physical push buttons provide automatic operation:

- **Empty Position**: Button press is logged, no automatic action
- **Occupied Position**: Button press triggers automatic item retrieval

**Real-time monitoring:**
```
[M] Monitor Push Buttons
🔘 PUSH BUTTON MONITORING
Press Ctrl+C to stop monitoring...
Push buttons will trigger automatic retrieval of items

🔘 Button 7 pressed - Auto-retrieving WIDGET-001
✅ Item WIDGET-001 retrieved automatically
🔘 Button 12 pressed - Position empty
```

## 💡 LED Control Features

The system automatically manages all 35 LED indicators:

- **OFF (False)**: Position is empty
- **ON (True)**: Position contains an item  
- **Synchronized**: LEDs update automatically with inventory changes
- **Manual Refresh**: Use `[U]` command to update all LEDs

## 📊 System Monitoring

### System Status Display

```
[T] System Status
📊 SYSTEM STATUS - Auto Rack35 AS/RS - OMRON NX102-9000
======================================================================
PLC Model: OMRON NX102-9000
Timestamp: 2025-08-28T16:45:30
System Status: MONITORING

🔌 COMMUNICATION:
   Protocol: OPC_UA
   Endpoint: opc.tcp://192.168.1.100:4840
   Connected: Yes

📦 STORAGE:
   Total Positions: 35
   Occupied: 8
   Available: 27
   Occupancy: 23%
   Layout: 7×5

📋 TASKS:
   Pending: 0
   Active: None
   Completed: 15

🚨 SAFETY:
   Emergency Stop: NORMAL
======================================================================
```

### Position Details

```
[P] Position Details
Position (1-35) or 'all': 15

📍 POSITION 15 DETAILS:
   Name: P15
   Grid Location: R3C5
   Status: OCCUPIED
   Occupied: Yes
   Product ID: PART-ABC
   Stored At: 2025-08-28 15:30:22
   LED Node: ns=4;s=led15
   Push Button: ns=4;s=pb15
```

### Inventory Tracking

```
[L] List Stored Items
📋 STORED ITEMS INVENTORY
Total Items: 8
Unique Products: 5

Product ID      Qty  Positions             Last Stored
---------------------------------------------------------------
WIDGET-001      2    P02, P20              2025-08-28 15:45
PART-ABC        1    P15                   2025-08-28 15:30
COMPONENT-X     3    P06, P13, P24         2025-08-28 14:20
GEAR-789        1    P04                   2025-08-28 13:15
SENSOR-456      1    P10                   2025-08-28 12:30
```

## 🚨 Safety Features

### Emergency Kill Switch Monitoring

The system continuously monitors your emergency kill switch:

```
[E] Emergency Status
🚨 EMERGENCY STATUS CHECK
✅ Emergency kill switch is NORMAL
   System is safe to operate
   System Status: MONITORING
```

**Emergency Response:**
- Immediate system shutdown when kill switch activated
- All LEDs turned off for safety
- Pending tasks cancelled
- System requires restart after emergency reset

### Safety Interlocks

- **Position Validation**: Prevents storing items in occupied positions
- **Range Checking**: Only allows positions 1-35
- **Status Verification**: Confirms item existence before retrieval
- **Communication Monitoring**: Handles OPC UA connection failures

## ⚙️ Configuration Options

### Communication Settings

```json
{
  "communication": {
    "protocol": "OPC_UA",
    "endpoint": "opc.tcp://192.168.1.100:4840",
    "namespace": 4,
    "timeout": 5.0,
    "retry_count": 3,
    "retry_delay": 1.0
  }
}
```

### Physical Layout

```json
{
  "storage_rack": {
    "total_positions": 35,
    "layout": {
      "rows": 7,
      "columns": 5,
      "description": "7×5 grid layout with 35 positions"
    }
  }
}
```

### Position Mapping

Each position is automatically configured:
```json
{
  "position_01": {
    "id": 1,
    "name": "Position 1",
    "led_node": "ns=4;s=led1",
    "pushbutton_node": "ns=4;s=pb1",
    "row": 1,
    "column": 1
  }
}
```

## 🛠️ Troubleshooting

### Connection Issues

**Problem:** `❌ Failed to connect to OMRON PLC`
**Solutions:**
- Verify PLC IP address in configuration
- Check network connectivity: `ping YOUR_PLC_IP`
- Ensure OPC UA server is enabled on OMRON NX102-9000
- Verify port 4840 is accessible (not blocked by firewall)
- Confirm PLC is powered on and running

### LED Control Problems

**Problem:** `⚠️ LED write failed`
**Solutions:**
- Confirm OPC UA node IDs are correct (`ns=4;s=led1`, etc.)
- Check PLC program has LED variables properly configured
- Verify write permissions on OPC UA server
- Test with OMRON OPC UA client software first

### Position Issues

**Problem:** `❌ Position 36 not found`
**Solutions:**
- System supports positions 1-35 only
- Check grid layout configuration matches physical rack
- Verify position calculations are correct

### Push Button Not Responding

**Problem:** `🔘 Button press not detected`
**Solutions:**
- Verify push button nodes (`ns=4;s=pb1`, etc.) exist in PLC
- Check button monitoring frequency in configuration
- Test button states with OPC UA client software
- Ensure buttons are properly wired and configured in PLC program

## 🏗️ System Architecture

```
OMRON AS/RS Control System
├── omron_asrs_app.py          # Interactive user interface
├── omron_asrs_controller.py   # Main system coordinator
├── omron_asrs_core.py         # Core classes & OPC UA client
├── omron_asrs_config.json     # System configuration
├── setup_omron.py             # Configuration helper
└── test_omron.py              # System test suite
```

### Core Components

- **OmronOPCClient**: Handles all OPC UA communication with NX102-9000
- **PositionManager**: Manages 35 storage positions and LED states
- **OmronASRSController**: Coordinates operations, tasks, and monitoring
- **OmronASRSApplication**: Provides interactive user interface

## 📈 Advanced Features

### Task System
- Asynchronous task processing
- Queue management for multiple operations
- Task status tracking and history
- Error handling and recovery

### Real-time Monitoring
- Continuous push button monitoring
- Emergency kill switch surveillance
- LED status synchronization
- System health tracking

### Inventory Management
- Product location tracking
- Storage timestamp logging
- Occupancy statistics
- Grid-based position mapping

## 🔄 Integration Possibilities

This system can be extended for:

### Enterprise Integration
- **ERP Systems**: Connect to SAP, Oracle, or other enterprise software
- **WMS Integration**: Link with warehouse management systems
- **Database Storage**: Persistent inventory and transaction logging
- **REST API**: Web service interface for external applications

### Additional Hardware
- **Barcode Scanners**: Automatic product identification
- **RFID Readers**: Enhanced tracking capabilities
- **Conveyor Integration**: Automated material handling
- **HMI Panels**: Industrial touch screen interfaces

### Communication Protocols
- **Modbus Integration**: Connect additional devices
- **Ethernet/IP**: Industrial networking protocols  
- **MQTT Publishing**: IoT and Industry 4.0 connectivity
- **Database Logging**: SQL Server, MySQL, PostgreSQL

## 📞 Support Information

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows/Linux with network access
- **Hardware**: OMRON NX102-9000 PLC with OPC UA server
- **Network**: TCP/IP connectivity (typically port 4840)

### File Dependencies
- `opcua` - Python OPC UA library (install via pip)
- Standard Python libraries (json, threading, time, etc.)

### Getting Help
1. Run `python test_omron.py` to diagnose connection issues
2. Check system logs for detailed error messages
3. Verify OPC UA connectivity with OMRON Sysmac Studio
4. Review configuration files for correct IP addresses

### Performance Optimization
- Use wired Ethernet for best reliability
- Configure OPC UA subscription rates appropriately  
- Monitor system resources during high-frequency operations
- Regular LED synchronization maintains visual accuracy

## 📝 License and Usage

This system was developed specifically for the OMRON Auto Rack35 AS/RS at BVM.

**Features:**
- Production-ready Python automation system
- Complete integration with existing OPC UA infrastructure
- Professional warehouse management capabilities
- Real-time monitoring and control interface

---

## 🎉 Ready for Operation!

Your OMRON Auto Rack35 AS/RS Control System is ready for professional warehouse automation.

**Quick Start Reminder:**
1. `python setup_omron.py` - Configure PLC IP
2. `python test_omron.py` - Test connectivity  
3. `python omron_asrs_app.py` - Start system

**System Capabilities:**
- 35-position automated storage and retrieval
- Individual LED control and push button monitoring
- Real-time inventory management with grid display
- Emergency safety integration
- Professional operator interface

*Transform your warehouse operations with intelligent automation! 🏭*