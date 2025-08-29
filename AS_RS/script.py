# 1. Create configuration using user's proven settings

import json

config_proven = {
    "system": {
        "name": "BVM Auto Rack35 AS/RS Control System",
        "version": "4.0",
        "plc_model": "OMRON NX102-9000",
        "description": "35-position AS/RS with proven asyncua connection"
    },
    "plc": {
        "ip": "10.10.14.104",
        "url": "opc.tcp://10.10.14.104:4840",
        "timeout": 10000,
        "retry_count": 3,
        "retry_delay": 2.0
    },
    "paths": {
        "known_path": ["0:Objects", "4:new_Controller_0"],
        "variables_path": ["0:Objects", "4:new_Controller_0", "4:GlobalVars"]
    },
    "rack": {
        "positions": 35,
        "layout": {"rows": 7, "columns": 5},
        "variables": {
            "leds": [f"led{i}" for i in range(1, 36)],
            "buttons": [f"pb{i}" for i in range(1, 36)],
            "emergency": "kill"
        }
    },
    "operation": {
        "scan_interval": 0.5,
        "command_timeout": 10.0,
        "auto_led_update": True,
        "button_debounce": 0.3,
        "max_retries": 3
    },
    "display": {
        "auto_refresh_grid": True,
        "refresh_interval": 30,
        "show_timestamps": True
    }
}

with open('asrs_config.json', 'w') as f:
    json.dump(config_proven, f, indent=2)

print("✅ 1. Configuration (proven asyncua): asrs_config.json")