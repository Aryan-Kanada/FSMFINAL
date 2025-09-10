"""
Configuration file for ASRS PLC Connection
Based on Omron NX-series PLC with Sysmac Studio
"""

# PLC Connection Settings
PLC_IP = "192.168.1.100"
PLC_PORT = 4840
CONNECTION_TIMEOUT = 10  # seconds
RETRY_COUNT = 3

# OPC UA Node IDs based on your PLC variables
PLC_VARIABLES = {
    # Motor Controls
    "motor1": "ns=4;s=motor1",
    "motor2": "ns=4;s=motor2", 
    "motor3": "ns=4;s=motor3",

    # Position Controls
    "X_write_position": "ns=4;s=X_write_position",
    "Y_write_position": "ns=4;s=Y_write_position",
    "Z_write_position": "ns=4;s=Z_write_position",

    # Position References
    "X_table_pose": "ns=4;s=X_table_pose",
    "Y_table_pose": "ns=4;s=Y_table_pose",
    "Z_center": "ns=4;s=Z_center",
    "Z_out": "ns=4;s=Z_out",

    # Status Variables
    "proximity": "ns=4;s=proximity",
    "X_Run": "ns=4;s=X_Run",
    "Y_Run": "ns=4;s=Y_Run",
    "Z_Run": "ns=4;s=Z_Run",

    # Step Controls
    "Pos1": "ns=4;s=Pos1",
    "Pos2": "ns=4;s=Pos2",
    "Stp1": "ns=4;s=Stp1",
    "Stp2": "ns=4;s=Stp2",
    "Stp3": "ns=4;s=Stp3",
    "Stp4": "ns=4;s=Stp4",
    "Stp5": "ns=4;s=Stp5",
    "Stp6": "ns=4;s=Stp6",
    "Stp7": "ns=4;s=Stp7",
    "Stp8": "ns=4;s=Stp8",

    # Start/Stop Controls
    "Start_1": "ns=4;s=Start_1",
    "Start_2": "ns=4;s=Start_2", 
    "Start_3": "ns=4;s=Start_3",
    "Stop_1": "ns=4;s=Stop_1",
    "Stop_2": "ns=4;s=Stop_2",
    "Stop_3": "ns=4;s=Stop_3",

    # LED Indicators
    "green_light": "ns=4;s=green_light",
    "red_light": "ns=4;s=red_light",
    "orange_light": "ns=4;s=orange_light",
    "horn": "ns=4;s=horn",

    # LED Arrays (A1-A7, B1-B7, C1-C7, D1-D7)
    "ledA1": "ns=4;s=ledA1",
    "ledA2": "ns=4;s=ledA2", 
    "ledA3": "ns=4;s=ledA3",
    "ledA4": "ns=4;s=ledA4",
    "ledA5": "ns=4;s=ledA5",
    "ledA6": "ns=4;s=ledA6",
    "ledA7": "ns=4;s=ledA7",

    "ledB1": "ns=4;s=ledB1",
    "ledB2": "ns=4;s=ledB2",
    "ledB3": "ns=4;s=ledB3", 
    "ledB4": "ns=4;s=ledB4",
    "ledB5": "ns=4;s=ledB5",
    "ledB6": "ns=4;s=ledB6",
    "ledB7": "ns=4;s=ledB7",

    # Position Coordinates (based on PLC values)
    "x1": "ns=4;s=x1",          # 0
    "x2": "ns=4;s=x2",          # 229372  
    "x3": "ns=4;s=x3",          # 455745
    "x4": "ns=4;s=x4",          # 685117
    "x5": "ns=4;s=x5",          # 915490

    "y1": "ns=4;s=y1",          # 0
    "y2": "ns=4;s=y2",          # 150000
    "y3": "ns=4;s=y3",          # 300000
    "y4": "ns=4;s=y4",          # 450000
    "y5": "ns=4;s=y5",          # 600000
    "y6": "ns=4;s=y6",          # 750000
    "y7": "ns=4;s=y7",          # 900000
}

# Position Values (from your PLC)
POSITION_VALUES = {
    "X_TABLE_POSE": 520000,
    "Y_TABLE_POSE": 320000,
    "Z_CENTER": 11400,
    "Z_OUT": 21500,
    "Y_UP": 31250,
    "Y_DOWN": 250000,

    # Position coordinates
    "X_POSITIONS": [0, 229372, 455745, 685117, 915490],
    "Y_POSITIONS": [0, 150000, 300000, 450000, 600000, 750000, 900000],
}

# Timing configurations
STEP_DELAYS = {
    "stp1_delay": 1.0,  # seconds
    "stp2_delay": 2.0,
    "stp3_delay": 1.0,
    "stp4_delay": 1.0,
    "stp5_delay": 1.0,
    "stp6_delay": 1.0,
    "stp7_delay": 5.0,
    "stp8_delay": 1.0,
}

# Modbus settings (from your communication setup)
MODBUS_SETTINGS = {
    "RETRY_COUNT": 2,
    "TIMEOUT_MS": 100,
    "SEND_DELAY": 0,
    "X_AXIS_SLAVE_ID": 1,
    "Y_AXIS_SLAVE_ID": 2, 
    "Z_AXIS_SLAVE_ID": 3,
    "READ_ADDRESS": 294,
    "WRITE_ADDRESS": 294,
    "STATUS_ADDRESS": 2577,
}
