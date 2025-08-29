# Create the updated configuration for the actual OMRON OPC UA system

import json

omron_asrs_config = {
    "system": {
        "name": "Auto Rack35 AS/RS - OMRON NX102-9000",
        "type": "AUTOMATED_STORAGE_RETRIEVAL",
        "description": "35-position AS/RS with LED indicators and push button controls",
        "version": "2.0",
        "plc_model": "OMRON NX102-9000"
    },
    "communication": {
        "protocol": "OPC_UA",
        "endpoint": "opc.tcp://10.10.14.113:4840",  # Update with your PLC IP
        "namespace": 4,
        "timeout": 5.0,
        "retry_count": 3,
        "retry_delay": 1.0
    },
    "storage_rack": {
        "total_positions": 35,
        "layout": {
            "rows": 7,        # 7 rows of 5 positions each (7×5=35)
            "columns": 5,     # Or adjust based on your physical layout
            "description": "35-position storage rack with individual LED/PB control"
        },
        "positions": {
            # This will be automatically generated for positions 1-35
            "position_template": {
                "led_node": "ns=4;s=led{position}",
                "pushbutton_node": "ns=4;s=pb{position}",
                "description": "Storage position {position}"
            }
        }
    },
    "control_nodes": {
        "emergency_kill": "ns=4;s=kill",
        "system_status": "ns=4;s=system_status",  # Add if available
        "system_mode": "ns=4;s=system_mode",      # Add if available
        "alarm_status": "ns=4;s=alarm_status"     # Add if available
    },
    "operations": {
        "led_control": {
            "off": False,
            "on": True,
            "blink_pattern": "custom"  # If supported
        },
        "position_assignment": {
            "strategy": "SEQUENTIAL",  # SEQUENTIAL, RANDOM, OPTIMIZED
            "start_position": 1,
            "end_position": 35
        },
        "safety": {
            "emergency_stop_monitoring": True,
            "led_status_validation": True,
            "position_conflict_detection": True
        }
    },
    "visual_feedback": {
        "led_states": {
            "empty": {"value": False, "description": "Position empty"},
            "occupied": {"value": True, "description": "Position occupied"},
            "reserved": {"blink": True, "description": "Position reserved for incoming item"}
        },
        "status_display": {
            "show_position_map": True,
            "show_led_states": True,
            "show_occupancy_stats": True
        }
    }
}

# Generate specific position configurations
positions = {}
for i in range(1, 36):  # Positions 1-35
    positions[f"position_{i:02d}"] = {
        "id": i,
        "name": f"Position {i}",
        "led_node": f"ns=4;s=led{i}",
        "pushbutton_node": f"ns=4;s=pb{i}",
        "row": ((i - 1) // 5) + 1,      # Calculate row (1-7)
        "column": ((i - 1) % 5) + 1,    # Calculate column (1-5)
        "occupied": False,
        "product_id": None,
        "stored_at": None
    }

omron_asrs_config["storage_positions"] = positions

# Save the updated configuration
with open('omron_asrs_config.json', 'w') as f:
    json.dump(omron_asrs_config, f, indent=2)

print("✅ OMRON AS/RS Configuration created: omron_asrs_config.json")
print(f"\n🏗️ Auto Rack35 OMRON NX102-9000 Configuration:")
print(f"📋 Total Positions: {omron_asrs_config['storage_rack']['total_positions']}")
print(f"🔌 Protocol: {omron_asrs_config['communication']['protocol']}")
print(f"🏭 PLC Model: {omron_asrs_config['system']['plc_model']}")
print(f"📍 Layout: {omron_asrs_config['storage_rack']['layout']['rows']} rows × {omron_asrs_config['storage_rack']['layout']['columns']} columns")
print(f"💡 LED Control: led1-led35")
print(f"🔘 Push Buttons: pb1-pb35") 
print(f"🚨 Emergency Kill: {omron_asrs_config['control_nodes']['emergency_kill']}")