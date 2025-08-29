# Create the complete new AS/RS system based on the working asyncua connection

# 1. Configuration file
asrs_config = {
    "system": {
        "name": "BVM Auto Rack35 AS/RS Control System",
        "version": "3.0",
        "plc_model": "OMRON NX102-9000",
        "description": "35-position AS/RS with asyncua connection"
    },
    "plc": {
        "ip": "10.10.14.104",
        "url": "opc.tcp://10.10.14.104:4840",
        "timeout": 10,
        "retry_count": 3
    },
    "paths": {
        "base_path": ["0:Objects", "4:new_Controller_0"],
        "variables_folder": "4:GlobalVars",
        "full_path": ["0:Objects", "4:new_Controller_0", "4:GlobalVars"]
    },
    "rack": {
        "positions": 35,
        "layout": {"rows": 7, "columns": 5},
        "variables": {
            "leds": ["led1", "led2", "led3", "led4", "led5", "led6", "led7", "led8", "led9", "led10",
                    "led11", "led12", "led13", "led14", "led15", "led16", "led17", "led18", "led19", "led20",
                    "led21", "led22", "led23", "led24", "led25", "led26", "led27", "led28", "led29", "led30",
                    "led31", "led32", "led33", "led34", "led35"],
            "buttons": ["pb1", "pb2", "pb3", "pb4", "pb5", "pb6", "pb7", "pb8", "pb9", "pb10",
                       "pb11", "pb12", "pb13", "pb14", "pb15", "pb16", "pb17", "pb18", "pb19", "pb20",
                       "pb21", "pb22", "pb23", "pb24", "pb25", "pb26", "pb27", "pb28", "pb29", "pb30",
                       "pb31", "pb32", "pb33", "pb34", "pb35"],
            "emergency": "kill"
        }
    },
    "operation": {
        "scan_interval": 0.5,
        "command_timeout": 5.0,
        "auto_led_update": True,
        "button_debounce": 0.2
    }
}

import json
with open('asrs_config.json', 'w') as f:
    json.dump(asrs_config, f, indent=2)

print("✅ Configuration file created: asrs_config.json")