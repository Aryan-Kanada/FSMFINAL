#!/usr/bin/env python3
"""
OMRON AS/RS Configuration Helper
"""

import json

def setup_configuration():
    """Interactive configuration setup"""
    print("🏗️ OMRON Auto Rack35 AS/RS Configuration Setup")
    print("=" * 50)

    # Get PLC IP
    plc_ip = input("\nPLC IP Address (default 10.10.14.113): ").strip()
    if not plc_ip:
        plc_ip = "10.10.14.113"

    endpoint = f"opc.tcp://{plc_ip}:4840"

    # Create basic configuration
    config = {
        "system": {
            "name": "Auto Rack35 AS/RS - OMRON NX102-9000",
            "plc_model": "OMRON NX102-9000"
        },
        "communication": {
            "protocol": "OPC_UA",
            "endpoint": endpoint,
            "namespace": 4,
            "timeout": 5.0
        },
        "storage_rack": {
            "total_positions": 35,
            "layout": {"rows": 7, "columns": 5}
        },
        "control_nodes": {
            "emergency_kill": "ns=4;s=kill"
        },
        "storage_positions": {}
    }

    # Generate positions
    for i in range(1, 36):
        config["storage_positions"][f"position_{i:02d}"] = {
            "id": i,
            "name": f"Position {i}",
            "led_node": f"ns=4;s=led{i}",
            "pushbutton_node": f"ns=4;s=pb{i}",
            "row": ((i - 1) // 5) + 1,
            "column": ((i - 1) % 5) + 1,
            "occupied": False
        }

    # Save configuration
    with open("omron_asrs_config.json", 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration created for PLC at {plc_ip}")
    print("\n🚀 Next steps:")
    print("1. python test_omron.py")
    print("2. python omron_asrs_app.py")

if __name__ == "__main__":
    setup_configuration()
