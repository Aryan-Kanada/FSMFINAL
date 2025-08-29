# Create the specialized OMRON AS/RS control system

omron_asrs_system = '''
"""
OMRON Auto Rack35 AS/RS Control System
Specialized for OMRON NX102-9000 with 35-position storage rack
Uses OPC UA communication with LED indicators and push button controls
"""

import json
import threading
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import queue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASRSStatus(Enum):
    IDLE = "idle"
    STORING = "storing" 
    RETRIEVING = "retrieving"
    MONITORING = "monitoring"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"

class PositionStatus(Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"  
    RESERVED = "reserved"
    ERROR = "error"

class TaskType(Enum):
    STORE_ITEM = "store_item"
    RETRIEVE_ITEM = "retrieve_item"
    UPDATE_DISPLAY = "update_display"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class StoragePosition:
    """Individual storage position in the rack"""
    id: int
    name: str
    row: int
    column: int
    led_node: str
    pushbutton_node: str
    occupied: bool = False
    product_id: Optional[str] = None
    stored_at: Optional[datetime] = None
    status: PositionStatus = PositionStatus.EMPTY
    
    @property
    def position_id(self) -> str:
        return f"P{self.id:02d}"
    
    @property
    def grid_location(self) -> str:
        return f"R{self.row}C{self.column}"

@dataclass
class ASRSTask:
    """AS/RS operation task"""
    task_id: str
    task_type: TaskType
    position: Optional[StoragePosition] = None
    product_id: Optional[str] = None
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[str] = None

# OPC UA Client for OMRON communication
class OmronOPCClient:
    """OPC UA client for OMRON NX102-9000 communication"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False
        self.nodes_cache = {}
        self._lock = threading.Lock()
    
    def connect(self) -> bool:
        """Connect to OMRON OPC UA server"""
        try:
            # Try to import real OPC UA library
            try:
                from opcua import Client
                self.client = Client(self.config['endpoint'])
                self.client.connect()
                self.connected = True
                logger.info(f"✅ Connected to OMRON PLC at {self.config['endpoint']}")
                return True
                
            except ImportError:
                logger.warning("opcua package not found, using mock client for demonstration")
                self.client = MockOPCClient(self.config)
                self.connected = True
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to OMRON PLC: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from OPC UA server"""
        if self.client and hasattr(self.client, 'disconnect'):
            self.client.disconnect()
        self.connected = False
        logger.info("🔌 Disconnected from OMRON PLC")
    
    def get_node(self, node_id: str):
        """Get OPC UA node with caching"""
        with self._lock:
            if node_id not in self.nodes_cache:
                if hasattr(self.client, 'get_node'):
                    self.nodes_cache[node_id] = self.client.get_node(node_id)
                else:
                    self.nodes_cache[node_id] = MockNode(node_id)
            return self.nodes_cache[node_id]
    
    def read_value(self, node_id: str):
        """Read value from OPC UA node"""
        try:
            node = self.get_node(node_id)
            return node.get_value()
        except Exception as e:
            logger.error(f"❌ Error reading {node_id}: {e}")
            return None
    
    def write_value(self, node_id: str, value: Any) -> bool:
        """Write value to OPC UA node"""
        try:
            node = self.get_node(node_id)
            node.set_value(value)
            logger.debug(f"📝 Wrote {node_id} = {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Error writing {node_id}: {e}")
            return False

class MockOPCClient:
    """Mock OPC client for testing without hardware"""
    
    def __init__(self, config):
        self.config = config
        self.mock_values = {
            'ns=4;s=kill': False,  # Emergency kill switch
        }
        # Initialize all LEDs as OFF and push buttons as not pressed
        for i in range(1, 36):
            self.mock_values[f'ns=4;s=led{i}'] = False
            self.mock_values[f'ns=4;s=pb{i}'] = False
        logger.info("🔧 Using Mock OPC Client for OMRON PLC")
    
    def get_node(self, node_id: str):
        return MockNode(node_id, self.mock_values)

class MockNode:
    """Mock OPC UA node"""
    
    def __init__(self, node_id: str, mock_values: Dict = None):
        self.node_id = node_id
        self.mock_values = mock_values or {}
    
    def get_value(self):
        if self.mock_values and self.node_id in self.mock_values:
            return self.mock_values[self.node_id]
        # Simulate push button presses occasionally for demo
        if 'pb' in self.node_id:
            import random
            return random.random() < 0.1  # 10% chance of button press
        return False
    
    def set_value(self, value):
        if self.mock_values:
            self.mock_values[self.node_id] = value
        logger.debug(f"Mock set {self.node_id} = {value}")

class PositionManager:
    """Manages the 35 storage positions"""
    
    def __init__(self, config: Dict[str, Any], opc_client: OmronOPCClient):
        self.config = config
        self.opc_client = opc_client
        self.positions: Dict[int, StoragePosition] = {}
        self._initialize_positions()
        self._lock = threading.Lock()
    
    def _initialize_positions(self):
        """Initialize all 35 storage positions"""
        storage_positions = self.config['storage_positions']
        
        for pos_key, pos_config in storage_positions.items():
            position = StoragePosition(
                id=pos_config['id'],
                name=pos_config['name'],
                row=pos_config['row'],
                column=pos_config['column'],
                led_node=pos_config['led_node'],
                pushbutton_node=pos_config['pushbutton_node']
            )
            self.positions[position.id] = position
        
        logger.info(f"📦 Initialized {len(self.positions)} storage positions")
    
    def get_position(self, position_id: int) -> Optional[StoragePosition]:
        """Get position by ID"""
        return self.positions.get(position_id)
    
    def find_empty_position(self) -> Optional[StoragePosition]:
        """Find the first available empty position"""
        with self._lock:
            for position in self.positions.values():
                if not position.occupied:
                    return position
            return None
    
    def find_product(self, product_id: str) -> Optional[StoragePosition]:
        """Find position containing specific product"""
        with self._lock:
            for position in self.positions.values():
                if position.occupied and position.product_id == product_id:
                    return position
            return None
    
    def store_item(self, position_id: int, product_id: str) -> bool:
        """Store item in specified position"""
        with self._lock:
            position = self.positions.get(position_id)
            if not position:
                return False
            
            if position.occupied:
                logger.error(f"❌ Position {position_id} already occupied")
                return False
            
            # Update position data
            position.occupied = True
            position.product_id = product_id
            position.stored_at = datetime.now()
            position.status = PositionStatus.OCCUPIED
            
            # Turn on LED to indicate occupied
            if self.opc_client.write_value(position.led_node, True):
                logger.info(f"📦 Stored {product_id} at position {position_id}")
                return True
            else:
                # Rollback on LED write failure
                position.occupied = False
                position.product_id = None
                position.stored_at = None
                position.status = PositionStatus.EMPTY
                return False
    
    def retrieve_item(self, position_id: int) -> Optional[str]:
        """Retrieve item from specified position"""
        with self._lock:
            position = self.positions.get(position_id)
            if not position or not position.occupied:
                logger.error(f"❌ Position {position_id} is empty")
                return None
            
            product_id = position.product_id
            
            # Update position data
            position.occupied = False
            position.product_id = None
            position.stored_at = None
            position.status = PositionStatus.EMPTY
            
            # Turn off LED to indicate empty
            if self.opc_client.write_value(position.led_node, False):
                logger.info(f"📤 Retrieved {product_id} from position {position_id}")
                return product_id
            else:
                # Rollback on LED write failure
                position.occupied = True
                position.product_id = product_id
                position.status = PositionStatus.OCCUPIED
                return None
    
    def update_all_leds(self):
        """Update all LED states based on occupancy"""
        with self._lock:
            for position in self.positions.values():
                led_state = position.occupied
                self.opc_client.write_value(position.led_node, led_state)
    
    def monitor_pushbuttons(self) -> List[int]:
        """Check which push buttons are currently pressed"""
        pressed_buttons = []
        for position in self.positions.values():
            if self.opc_client.read_value(position.pushbutton_node):
                pressed_buttons.append(position.id)
        return pressed_buttons
    
    def get_occupancy_stats(self) -> Dict[str, Any]:
        """Get occupancy statistics"""
        with self._lock:
            occupied_count = sum(1 for pos in self.positions.values() if pos.occupied)
            total_count = len(self.positions)
            
            return {
                "total_positions": total_count,
                "occupied_positions": occupied_count,
                "empty_positions": total_count - occupied_count,
                "occupancy_percent": int((occupied_count / total_count) * 100),
                "grid_layout": f"{self.config['storage_rack']['layout']['rows']}×{self.config['storage_rack']['layout']['columns']}"
            }
    
    def get_grid_display(self) -> List[List[str]]:
        """Get visual grid representation of the rack"""
        rows = self.config['storage_rack']['layout']['rows']
        cols = self.config['storage_rack']['layout']['columns']
        
        grid = []
        for r in range(1, rows + 1):
            row = []
            for c in range(1, cols + 1):
                # Find position at this grid location
                pos_id = ((r - 1) * cols) + c
                if pos_id <= 35:  # Valid position
                    position = self.positions.get(pos_id)
                    if position and position.occupied:
                        row.append(f"[{pos_id:02d}]")  # Occupied
                    else:
                        row.append(f" {pos_id:02d} ")   # Empty
                else:
                    row.append("    ")  # No position
            grid.append(row)
        
        return grid

print("✅ OMRON AS/RS Core Classes Defined")
print("   - OmronOPCClient for OPC UA communication")
print("   - PositionManager for 35-position rack management")
print("   - StoragePosition with LED and push button control")
print("   - Visual grid display functionality")
'''

# Save the OMRON-specific core system
with open('omron_asrs_core.py', 'w') as f:
    f.write(omron_asrs_system)

print("✅ OMRON AS/RS Core System created: omron_asrs_core.py")