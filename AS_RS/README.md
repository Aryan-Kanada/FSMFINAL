# BVM Auto Rack35 AS/RS Control System

A complete Python control system for the **BVM Auto Rack35 AS/RS** (Automated Storage and Retrieval System) with 35 storage positions, LED indicators, and push button controls via **async OPC UA** communication.

## 🏗️ System Overview

This system provides professional automated warehouse control for your OMRON NX102-9000 PLC:

- **35 Storage Positions** - Complete inventory management with 7×5 grid layout
- **LED Status Indicators** - Visual feedback for each position (`led1-led35`)
- **Push Button Controls** - Manual operation and auto-retrieval (`pb1-pb35`)
- **Emergency Safety** - Kill switch monitoring (`kill`)
- **Async OPC UA Communication** - High-performance real-time communication
- **Interactive Interface** - Professional operator control system
- **Real-time Monitoring** - Live system status and inventory tracking

## 🎯 Your BVM Setup

**PLC Information:**
- **Model**: OMRON NX102-9000
- **IP Address**: `10.10.14.104`
- **OPC UA Endpoint**: `opc.tcp://10.10.14.104:4840`

**Variable Structure:**
```
PLC Path: Objects → new_Controller_0 → GlobalVars
├── led1-led35    (Position indicators)
├── pb1-pb35      (Push button inputs)
└── kill          (Emergency stop)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install asyncua

# Or use requirements file
pip install -r requirements.txt
```

### 2. Setup System

```bash
# Run setup script (recommended)
python setup.py

# Or manual setup
python discover_plc.py    # Discover PLC variables
python test_system.py     # Test system
```

### 3. Run AS/RS System

```bash
python asrs_app.py
```

## 📁 Complete File Structure

Your AS/RS system includes these files:

```
📁 BVM_AS_RS_System/
├── asrs_config.json      # System configuration
├── asrs_core.py          # Core classes and OPC UA client
├── asrs_controller.py    # Main system controller
├── asrs_app.py           # Interactive control application
├── discover_plc.py       # PLC variable discovery
├── test_system.py        # System testing suite
├── setup.py              # Setup and installation
├── requirements.txt      # Python dependencies
└── README.md             # This documentation
```

## 🎮 Interactive Control Interface

Once running, you'll see a professional control interface:

```
🏗️ BVM AUTO RACK35 AS/RS CONTROL SYSTEM
================================================================================
   PLC: OMRON NX102-9000 at 10.10.14.104
   Positions: 35
   Layout: 7×5 grid
   Version: 3.0
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
  [T] → System Status          [L] → List Stored Items
  [U] → Update LED Display     [M] → Monitor Buttons
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
⏱️  Storing... (2.3s)
✅ Operation completed
```

**Specific Position:**
```
Select option (1 or 2): 2
Position (1-35): 15
✅ Storage task submitted: WIDGET-001 → Position 15
⏱️  Storing... (1.8s)
✅ Operation completed
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
📦 Position 15 contains: WIDGET-001
Retrieve this item? (y/N): y
✅ Retrieval task submitted for position 15
⏱️  Retrieving... (1.5s)
✅ Operation completed
```

**By Product ID:**
```
Select option (1 or 2): 2
Product ID: WIDGET-001
📍 Found WIDGET-001 at position 7
📅 Stored at: 2025-08-29 14:30:22
Retrieve this item? (y/N): y
✅ Retrieval task submitted for WIDGET-001
⏱️  Retrieving... (2.1s)
✅ Operation completed
```

## 🔘 Push Button Integration

Your physical push buttons provide automatic operation:

**Real-time Button Monitoring:**
```
[M] Monitor Push Buttons
🔘 BUTTON MONITORING MODE
Press Ctrl+C to stop monitoring...

🔘 [14:32:15] Button 7 pressed - Auto-retrieving WIDGET-001
🔘 [14:32:45] Button 12 pressed - Position empty
🔘 [14:33:20] Button 3 pressed - Auto-retrieving PART-ABC
```

**Automatic Retrieval:**
- **Occupied Position**: Button press triggers automatic item retrieval
- **Empty Position**: Button press is logged but no action taken
- **Debouncing**: Prevents multiple triggers from single press

## 💡 LED Control Features

The system automatically manages all 35 LED indicators:

- **OFF**: Position is empty
- **ON**: Position contains an item
- **Auto-Sync**: LEDs automatically update with inventory changes
- **Manual Update**: Use `[U]` command to refresh all LEDs
- **Safety**: All LEDs turn OFF during emergency stop

## 📊 System Monitoring

### System Status Display

```
[T] System Status
📊 SYSTEM STATUS - BVM Auto Rack35 AS/RS Control System
======================================================================
Version: 3.0
Timestamp: 2025-08-29T16:45:30
System Status: MONITORING

🔌 PLC CONNECTION:
   IP Address: 10.10.14.104
   URL: opc.tcp://10.10.14.104:4840
   Connected: Yes

📦 STORAGE RACK:
   Total Positions: 35
   Occupied: 8
   Available: 27
   Occupancy: 23%
   Layout: 7×5

📋 TASKS:
   Queue Size: 0
   Active: None
   Completed: 25

🔄 Recent Tasks:
   STORE_143022: store - completed
   RETRIEVE_7_143115: retrieve - completed
   UPDATE_143200: update_display - completed
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
   LED State: ON
   Product ID: WIDGET-001
   Stored At: 2025-08-29 14:30:22
```

### Inventory Tracking

```
[L] List Stored Items
📋 STORED ITEMS INVENTORY
Total Items: 8
Unique Products: 5

Product ID      Qty  Positions             Last Stored
---------------------------------------------------------------
WIDGET-001      2    P07, P15              08-29 14:30
PART-ABC        1    P03                   08-29 14:15
COMPONENT-X     3    P01, P12, P24         08-29 13:45
GEAR-789        1    P09                   08-29 13:20
SENSOR-456      1    P18                   08-29 12:55
```

## 🚨 Safety Features

### Emergency Kill Switch

```
[E] Emergency Status
🚨 EMERGENCY STATUS
✅ Emergency status is NORMAL
   System status: MONITORING
```

**Emergency Response:**
- Immediate system shutdown when kill switch activated
- All LEDs turned OFF for safety
- All pending tasks cancelled
- System requires restart after emergency reset

### Safety Interlocks

- **Position Validation**: Prevents storing items in occupied positions
- **Range Checking**: Only allows positions 1-35
- **Status Verification**: Confirms item existence before retrieval
- **Communication Monitoring**: Handles OPC UA connection failures gracefully

## ⚙️ Configuration

### Main Configuration (`asrs_config.json`)

```json
{
  "system": {
    "name": "BVM Auto Rack35 AS/RS Control System",
    "version": "3.0",
    "plc_model": "OMRON NX102-9000"
  },
  "plc": {
    "ip": "10.10.14.104",
    "url": "opc.tcp://10.10.14.104:4840",
    "timeout": 10
  },
  "paths": {
    "base_path": ["0:Objects", "4:new_Controller_0"],
    "variables_folder": "4:GlobalVars"
  },
  "rack": {
    "positions": 35,
    "layout": {"rows": 7, "columns": 5}
  },
  "operation": {
    "scan_interval": 0.5,
    "auto_led_update": true,
    "button_debounce": 0.2
  }
}
```

### Customization Options

**PLC Settings:**
```json
"plc": {
  "ip": "10.10.14.104",        # Your PLC IP
  "timeout": 10,               # Connection timeout
  "retry_count": 3             # Connection retries
}
```

**Operation Settings:**
```json
"operation": {
  "scan_interval": 0.5,        # Status update frequency (seconds)
  "auto_led_update": true,     # Automatic LED synchronization
  "button_debounce": 0.2       # Button press debounce time
}
```

## 🛠️ System Testing & Diagnostics

### Discovery Tool

```bash
python discover_plc.py
```

**Output:**
```
🔍 Connecting to PLC at opc.tcp://10.10.14.104:4840...
✅ Successfully connected to PLC!

📁 Navigating through PLC structure...
   ✅ Found: 4:new_Controller_0

📂 Contents of 'new_Controller_0' folder:
============================================================
   📁 GlobalVars (namespace: 4)
      👆 This looks like the variables folder!

🔍 Exploring variables folder...

💡 LED Variables (35):
   ✅ led1
   ✅ led2
   ... and 33 more

🔘 Button Variables (35):
   ✅ pb1
   ✅ pb2
   ... and 33 more

🔧 Other Variables (1):
   📝 kill (EMERGENCY)

🧪 Testing variable access...
   ✅ led1 = False
   ✅ pb1 = False
   ✅ kill = False

🎉 Discovery completed!
   Variables are ready for AS/RS system
```

### System Test Suite

```bash
python test_system.py
```

**Test Results:**
```
🧪 BVM AS/RS System Tests
========================================
Testing connection to PLC at 10.10.14.104

🔗 Testing PLC Connection
   ✅ PLC connection successful
   ✅ Connected to opc.tcp://10.10.14.104:4840

🔧 Testing Variable Access
   ✅ LED1 = False
   ✅ LED2 = False
   ✅ PB1 = False
   ✅ PB2 = False
   ✅ Emergency kill = False
   📊 Results: 5/5 LEDs, 5/5 buttons accessible

💡 Testing LED Control
   ✅ LED1 turned ON
   ✅ LED1 turned OFF

⚙️ Testing System Operations
   ✅ 35 positions initialized
   ✅ Grid display: 7 rows
   ✅ Task submission working
   ✅ System status: monitoring

========================================
📊 TEST RESULTS SUMMARY
========================================
Connection Test          : ✅ PASS
Variable Access Test     : ✅ PASS
LED Control Test         : ✅ PASS
System Operations Test   : ✅ PASS

Overall: 4/4 tests passed

🎉 ALL TESTS PASSED!
   Your BVM AS/RS system is ready for operation
   Run: python asrs_app.py
```

## 🚨 Troubleshooting

### Connection Issues

**Problem:** `Connection failed` or `PLC not responding`

**Solutions:**
1. **Check PLC Power:** Ensure OMRON NX102-9000 is powered on
2. **Verify Network:** Can you ping `10.10.14.104`?
3. **OPC UA Server:** Is OPC UA server enabled in Sysmac Studio?
4. **Firewall:** Check Windows firewall on port 4840

```bash
# Test connectivity
ping 10.10.14.104

# Discover PLC structure
python discover_plc.py

# Run diagnostics
python test_system.py
```

### Variable Access Issues

**Problem:** `Could not find LED node` or `Variable not accessible`

**Solutions:**
1. **Run Discovery:** `python discover_plc.py` to find actual variable names
2. **Check Sysmac Studio:** Ensure variables are set to "Publish Only"
3. **Verify Names:** Variables must be exactly `led1`, `led2`, `pb1`, `pb2`, etc.
4. **Namespace:** Check if namespace index is correct (should be 4)

### LED Control Problems

**Problem:** `Error writing LED` or LEDs not updating

**Solutions:**
1. **Write Permissions:** Verify OPC UA server allows writes
2. **Variable Configuration:** Check variables are BOOL type in PLC
3. **Connection Quality:** Ensure stable network connection
4. **Manual Test:** Use `[U]` command to update all LEDs

### Emergency Stop Issues

**Problem:** System stuck in emergency state

**Solutions:**
1. **Check Kill Switch:** Verify physical emergency switch is reset
2. **Read Kill Variable:** Use discovery tool to check `kill` variable value
3. **Restart System:** Exit and restart `python asrs_app.py`
4. **PLC Reset:** May need to reset PLC in Sysmac Studio

## 📈 Advanced Features

### Async Programming

The system uses **async/await** patterns for high-performance operation:

```python
# Example async operation
async def store_multiple_items(items):
    for item in items:
        await controller.store_item(item['product_id'], item['position'])
        await asyncio.sleep(0.1)  # Brief pause between operations
```

### Real-time Monitoring

- **500ms scan cycle** for system status updates
- **Debounced button detection** prevents false triggers
- **Automatic LED synchronization** keeps display accurate
- **Task queue management** handles multiple operations

### Integration Ready

The system can be extended for:

- **REST API Interface** - Web service for external systems
- **Database Integration** - Store inventory in SQL databases
- **Barcode Scanning** - Automatic product identification
- **ERP Integration** - Connect to enterprise systems
- **MQTT Publishing** - IoT and Industry 4.0 connectivity

## 💻 System Requirements

### Software Requirements
- **Python 3.7+** (Python 3.8+ recommended)
- **asyncua library** (automatically installed)
- **Windows or Linux** with network access to PLC

### Hardware Requirements
- **OMRON NX102-9000 PLC** with OPC UA server enabled
- **Network connection** to PLC (Ethernet recommended)
- **35-position storage rack** with LED and button I/O

### Network Requirements
- **TCP/IP connectivity** to PLC on port 4840
- **Same network subnet** as PLC (10.10.14.x)
- **Firewall exceptions** for OPC UA port 4840

## 📞 Support & Maintenance

### Regular Maintenance
- **Monitor system logs** for communication errors
- **Check LED synchronization** periodically with `[U]` command
- **Verify emergency systems** with `[E]` command
- **Test button functionality** with `[M]` monitoring mode

### Performance Optimization
- **Adjust scan interval** in config for different update rates
- **Monitor task queue** to prevent bottlenecks
- **Use wired Ethernet** for best communication reliability
- **Regular system testing** with `python test_system.py`

### Getting Help
1. **Run diagnostics:** `python test_system.py`
2. **Check discovery:** `python discover_plc.py`
3. **Review logs:** Check console output for error messages
4. **Test connectivity:** Basic ping test to PLC

---

## 🎉 Ready for Professional Operation!

Your **BVM Auto Rack35 AS/RS Control System** provides:

✅ **Professional warehouse automation** with 35-position inventory management  
✅ **Real-time LED status indicators** for visual feedback  
✅ **Push button integration** with auto-retrieval capability  
✅ **Emergency safety systems** with kill switch monitoring  
✅ **High-performance async communication** with OMRON PLC  
✅ **Interactive operator interface** for complete system control  
✅ **Comprehensive testing** and diagnostic tools  
✅ **Production-ready reliability** for continuous operation  

**Start your automated warehouse operations today!** 🏭✨

```bash
python asrs_app.py
```