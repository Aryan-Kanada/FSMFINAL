# Running OMRON AS/RS Control System with Sysmac Studio

## Complete Setup Guide for OMRON NX102-9000 with OPC UA

This guide shows you how to configure your OMRON NX102-9000 PLC in Sysmac Studio to work with the Python AS/RS Control System.

---

## 📋 Prerequisites

- **Hardware**: OMRON NX102-9000 PLC (firmware version 1.30 or later)
- **Software**: Sysmac Studio (version 1.31 or later recommended)
- **Network**: Ethernet connection between PC and PLC
- **Python Environment**: Your AS/RS control system files

---

## 🔧 Step 1: Configure PLC Network Settings

### 1.1 Set PLC IP Address
1. Open **Sysmac Studio**
2. Create new project or open existing project
3. Select **OMRON NX102-9000** as your controller
4. In **Multiview Explorer**, navigate to:
   ```
   Configurations and Setup → Controller Setup → Built-in EtherNet/IP Port Settings
   ```
5. Set IP address (example):
   - **IP Address**: `192.168.1.100` (or your preferred IP)
   - **Subnet Mask**: `255.255.255.0`
   - **Default Gateway**: `192.168.1.1` (if needed)

### 1.2 Set PC IP Address
Your PC must be on the same network as the PLC:
- **PC IP**: `192.168.1.50` (different from PLC)
- **Subnet Mask**: `255.255.255.0`

---

## 📦 Step 2: Create Global Variables for AS/RS

### 2.1 Create LED Variables (led1-led35)
1. In **Multiview Explorer**, go to:
   ```
   Programming → Data → Global Variables
   ```
2. Create variables for each LED:

   | Name | Data Type | Network Publish | Initial Value |
   |------|-----------|-----------------|---------------|
   | led1 | BOOL      | Publish Only    | FALSE         |
   | led2 | BOOL      | Publish Only    | FALSE         |
   | ...  | ...       | ...             | ...           |
   | led35| BOOL      | Publish Only    | FALSE         |

### 2.2 Create Push Button Variables (pb1-pb35)
3. Create variables for each push button:

   | Name | Data Type | Network Publish | Initial Value |
   |------|-----------|-----------------|---------------|
   | pb1  | BOOL      | Publish Only    | FALSE         |
   | pb2  | BOOL      | Publish Only    | FALSE         |
   | ...  | ...       | ...             | ...           |
   | pb35 | BOOL      | Publish Only    | FALSE         |

### 2.3 Create Emergency Kill Variable
4. Create emergency kill switch variable:

   | Name | Data Type | Network Publish | Initial Value |
   |------|-----------|-----------------|---------------|
   | kill | BOOL      | Publish Only    | FALSE         |

**Important**: Set **Network Publish** to **"Publish Only"** for all variables to make them accessible via OPC UA.

---

## ⚙️ Step 3: Enable OPC UA Server

### 3.1 Configure OPC UA Server Settings
1. In **Multiview Explorer**, navigate to:
   ```
   Configurations and Setup → OPC UA Settings → OPC UA Server Settings
   ```
2. Configure server settings:
   - **Server Function Setting**: Select **"Use"** to enable OPC UA Server
   - **Port Number**: Keep default **4840** (standard OPC UA port)
   - **Event Log Recording**: Enable if you want logging
   - **Endpoint Address**: Will be `opc.tcp://[PLC_IP]:4840`

### 3.2 Transfer Settings to PLC
1. Go **Online** with the controller:
   ```
   Controller → Online → Connect
   ```
2. Transfer the program and settings:
   ```
   Controller → Transfer → To Controller
   ```
3. **Important**: Reset the controller after transfer:
   - Put controller in **Program Mode**
   - Go to: `Controller → Reset`
   - Wait for PLC to reboot

---

## 🛡️ Step 4: Generate OPC UA Server Certificate

### 4.1 Create Server Certificate
1. Ensure you're **Online** with the controller
2. In **Multiview Explorer**, right-click:
   ```
   Configurations and Setup → OPC UA Settings → OPC UA Server Settings
   ```
3. Select **"Server Certificate"**
4. In the certificate dialog:
   - Enter certificate details (organization, country, etc.)
   - Set **Validity Period** (e.g., 10 years)
   - Click **"Regenerate Certificate"**
   - Click **"OK"** to create certificate

### 4.2 Verify Server Status
1. Right-click **OPC UA Server Settings**
2. Select **"Server Status"**
3. Confirm server is **"Running"**
4. Note the **Endpoint URL**: `opc.tcp://192.168.1.100:4840`

---

## 🐍 Step 5: Configure Python AS/RS System

### 5.1 Update Configuration File
Edit your `omron_asrs_config.json` file:

```json
{
  "system": {
    "name": "Auto Rack35 AS/RS - OMRON NX102-9000",
    "plc_model": "OMRON NX102-9000"
  },
  "communication": {
    "protocol": "OPC_UA",
    "endpoint": "opc.tcp://192.168.1.100:4840",
    "namespace": 4,
    "timeout": 5.0,
    "retry_count": 3
  },
  "control_nodes": {
    "emergency_kill": "ns=4;s=kill"
  }
}
```

### 5.2 Install Python Dependencies
```bash
pip install opcua
```

---

## 🧪 Step 6: Test the Connection

### 6.1 Test with Python System
```bash
# Test OPC UA connectivity
python test_omron.py
```

Expected output:
```
🧪 OMRON AS/RS System Test
===================================
1. Testing system initialization...
   ✅ System initialized successfully
2. Testing OPC UA nodes...
   Emergency kill: False
   LED1 status: False
✅ All tests completed successfully!
```

### 6.2 Test with UA Expert (Optional)
1. Download **UA Expert** (free OPC UA client)
2. Add server connection: `opc.tcp://192.168.1.100:4840`
3. Connect and browse to: `NX102 → GlobalVars`
4. You should see all your led1-led35, pb1-pb35, and kill variables

---

## 🎮 Step 7: Run the AS/RS Control System

### 7.1 Start the Python Application
```bash
python omron_asrs_app.py
```

### 7.2 Verify Grid Display
You should see the 7×5 grid layout with real-time LED status:

```
📦 STORAGE RACK LAYOUT - LIVE STATUS
============================================================
Occupancy: 0/35 (0%)
Legend: [##] = Occupied,  ##  = Empty

      C1    C2    C3    C4    C5  
 R1   01    02    03    04    05 
 R2   06    07    08    09    10 
 R3   11    12    13    14    15 
 R4   16    17    18    19    20 
 R5   21    22    23    24    25 
 R6   26    27    28    29    30 
 R7   31    32    33    34    35 
============================================================
```

---

## 🔧 Step 8: Program Logic in Sysmac Studio

### 8.1 Create Program for LED Control
1. Go to: `Programming → POUs → Programs`
2. Create a new **Structured Text (ST)** program:

```st
PROGRAM LED_Control
VAR
    // Local variables if needed
END_VAR

// Example: LED control based on storage status
// This would be connected to your physical storage sensors
// For now, you can manually test by setting values

// Emergency kill logic
IF kill THEN
    led1 := FALSE;
    led2 := FALSE;
    // ... turn off all LEDs for safety
    led35 := FALSE;
END_IF;

// Push button handling could be added here
// Example: IF pb1 AND led1 THEN trigger_retrieval := TRUE; END_IF;

END_PROGRAM
```

### 8.2 Assign Program to Task
1. Go to: `Configurations and Setup → Task Settings`
2. Assign your program to the **Primary Task**
3. Transfer to controller

---

## 🎯 Step 9: Test Full System Operation

### 9.1 Store an Item
1. In Python application, press **[S]**
2. Enter product ID: `TEST-001`
3. Choose auto-assign or specific position
4. Watch LED turn ON in both Sysmac Studio and Python interface

### 9.2 Retrieve an Item
1. Press **[R]** in Python application
2. Select by position or product ID
3. Watch LED turn OFF when item is retrieved

### 9.3 Monitor Push Buttons
1. In Sysmac Studio, manually set `pb1 := TRUE`
2. Python system should detect and log the button press
3. If position 1 is occupied, it should trigger auto-retrieval

---

## 🚨 Troubleshooting

### Connection Issues
**Problem**: `Failed to connect to OMRON PLC`
- Verify IP addresses and network connectivity
- Ping the PLC: `ping 192.168.1.100`
- Check if OPC UA server is running in Sysmac Studio
- Ensure port 4840 is not blocked by firewall

### Variable Access Issues  
**Problem**: `Cannot read ns=4;s=led1`
- Verify variables are set to **"Publish Only"**
- Check variable names match exactly (case-sensitive)
- Ensure controller is online and program is running

### Certificate Issues
**Problem**: `Bad certificate untrusted`
- Regenerate server certificate in Sysmac Studio
- For testing, you can disable security in OPC UA client

---

## 📊 Monitoring in Sysmac Studio

### Watch Table
1. Create a **Watch Table** to monitor variables:
   - `led1` through `led35`
   - `pb1` through `pb35` 
   - `kill`
2. You'll see real-time values change as the Python system operates

### Cross-Reference
Use **Cross-Reference** to see which programs use your OPC UA variables.

---

## ✅ System Integration Checklist

- [ ] PLC network settings configured
- [ ] Global variables created (led1-led35, pb1-pb35, kill)
- [ ] Variables set to "Publish Only"
- [ ] OPC UA server enabled and running
- [ ] Server certificate generated
- [ ] Python configuration updated with correct IP
- [ ] Connection tested successfully
- [ ] LED control verified
- [ ] Push button monitoring working
- [ ] Emergency kill switch functional

---

## 🎉 Success!

Your OMRON AS/RS Control System is now fully integrated with Sysmac Studio! The Python application can:

- ✅ Read/write all 35 LED indicators
- ✅ Monitor all 35 push button states  
- ✅ Monitor emergency kill switch
- ✅ Provide real-time visual feedback
- ✅ Execute automated storage/retrieval operations

The system provides professional warehouse automation with complete integration between your OMRON PLC and Python control software.