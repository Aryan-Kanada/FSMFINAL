# 2. Create core system using user's proven asyncua pattern

core_proven_code = '''"""
BVM AS/RS Core System - Using Proven Asyncua Connection
Based on user's working plc_monitor.py and new.py pattern
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from asyncua import Client, ua

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    MONITORING = "monitoring"
    STORING = "storing"
    RETRIEVING = "retrieving"
    ERROR = "error"
    EMERGENCY = "emergency"

class PositionStatus(Enum):
    """Position status enumeration"""
    EMPTY = "empty"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    ERROR = "error"

@dataclass
class StoragePosition:
    """Storage position in the AS/RS rack"""
    id: int
    row: int
    column: int
    status: PositionStatus = PositionStatus.EMPTY
    product_id: Optional[str] = None
    stored_at: Optional[datetime] = None
    led_state: bool = False
    button_pressed: bool = False
    last_activity: Optional[datetime] = None
    
    @property
    def position_name(self) -> str:
        return f"P{self.id:02d}"
    
    @property
    def grid_location(self) -> str:
        return f"R{self.row}C{self.column}"
    
    @property
    def is_available(self) -> bool:
        return self.status == PositionStatus.EMPTY

@dataclass
class ASRSTask:
    """AS/RS operation task"""
    id: str
    type: str
    position_id: Optional[int] = None
    product_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[str] = None
    priority: int = 5

class ProvenAsyncOPCClient:
    """Async OPC UA client using user's proven connection pattern"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False
        
        # Node references - using proven pattern
        self.variables_folder = None
        self.variable_nodes = {}  # Store all nodes by name
        self.led_nodes = {}
        self.button_nodes = {}
        self.kill_node = None
        
        # Statistics
        self.read_count = 0
        self.write_count = 0
        self.error_count = 0
        
        # Connection details from user's working code
        self.plc_url = self.config['plc']['url']
        self.variables_path = self.config['paths']['variables_path']
        
    async def connect(self) -> bool:
        """Connect using user's proven pattern from new.py"""
        try:
            logger.info(f"Attempting to connect to PLC at {self.plc_url}...")
            
            # Use user's proven async context manager pattern
            self.client = Client(url=self.plc_url)
            await self.client.connect()
            
            self.connected = True
            logger.info("Successfully connected to the PLC!")
            
            # Initialize variables using proven navigation pattern
            await self._initialize_variables_proven_way()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from PLC"""
        if self.client and self.connected:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from PLC")
            except Exception as e:
                logger.warning(f"Disconnect warning: {e}")
    
    async def _initialize_variables_proven_way(self):
        """Initialize variables using user's proven navigation pattern"""
        try:
            logger.info("Initializing variables using proven path navigation...")
            
            # Use user's exact pattern from new.py
            # PATH_TO_VARIABLES = ["0:Objects", "4:new_Controller_0", "4:GlobalVars"]
            current_node = self.client.get_node(ua.ObjectIds.ObjectsFolder)
            
            # Navigate using user's proven method
            for part in self.variables_path[1:]:  # Skip "0:Objects"
                try:
                    current_node = await current_node.get_child(part)
                    logger.debug(f"Successfully navigated to: {part}")
                except ua.UaError as e:
                    logger.error(f"Could not find path part '{part}': {e}")
                    raise Exception(f"Navigation failed at '{part}'")
            
            self.variables_folder = current_node
            
            # Get all variables using proven pattern
            variables_to_monitor = await self.variables_folder.get_children()
            if not variables_to_monitor:
                logger.error("Found the folder, but it contains no variables")
                return False
            
            logger.info(f"Found {len(variables_to_monitor)} variables in GlobalVars")
            
            # Store all variable nodes by name (user's pattern)
            for var_node in variables_to_monitor:
                try:
                    browse_name = await var_node.read_browse_name()
                    var_name = browse_name.Name
                    self.variable_nodes[var_name] = var_node
                    logger.debug(f"Registered variable: {var_name}")
                except Exception as e:
                    logger.warning(f"Could not read browse name for variable: {e}")
            
            # Categorize variables for AS/RS system
            await self._categorize_variables()
            
            # Report initialization results
            total_vars = len(self.variable_nodes)
            logger.info(f"✅ Initialized {total_vars} variable nodes:")
            logger.info(f"   LEDs: {len(self.led_nodes)}/35")
            logger.info(f"   Buttons: {len(self.button_nodes)}/35") 
            logger.info(f"   Emergency: {'Yes' if self.kill_node else 'No'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize variables: {e}")
            raise
    
    async def _categorize_variables(self):
        """Categorize variables for AS/RS system"""
        self.led_nodes.clear()
        self.button_nodes.clear()
        self.kill_node = None
        
        for var_name, var_node in self.variable_nodes.items():
            try:
                # LED variables (led1, led2, ..., led35)
                if var_name.startswith('led') and var_name[3:].isdigit():
                    led_num = int(var_name[3:])
                    if 1 <= led_num <= 35:
                        self.led_nodes[led_num] = var_node
                        if led_num <= 3:  # Log first few
                            logger.debug(f"✅ LED{led_num}: {var_name}")
                
                # Button variables (pb1, pb2, ..., pb35)
                elif var_name.startswith('pb') and var_name[2:].isdigit():
                    btn_num = int(var_name[2:])
                    if 1 <= btn_num <= 35:
                        self.button_nodes[btn_num] = var_node
                        if btn_num <= 3:  # Log first few
                            logger.debug(f"✅ PB{btn_num}: {var_name}")
                
                # Emergency kill switch
                elif var_name.lower() in ['kill', 'emergency', 'estop']:
                    self.kill_node = var_node
                    logger.debug(f"✅ Emergency: {var_name}")
                    
            except Exception as e:
                logger.debug(f"Could not categorize variable {var_name}: {e}")
    
    async def read_led_state(self, position_id: int) -> Optional[bool]:
        """Read LED state using proven get_value() pattern"""
        try:
            if position_id in self.led_nodes:
                value = await self.led_nodes[position_id].get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading LED{position_id}: {e}")
        return None
    
    async def write_led_state(self, position_id: int, state: bool) -> bool:
        """Write LED state using proven set_value() pattern"""
        try:
            if position_id in self.led_nodes:
                await self.led_nodes[position_id].set_value(state)
                self.write_count += 1
                logger.debug(f"LED{position_id} → {state}")
                return True
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error writing LED{position_id}: {e}")
        return False
    
    async def read_button_state(self, position_id: int) -> Optional[bool]:
        """Read button state using proven pattern"""
        try:
            if position_id in self.button_nodes:
                value = await self.button_nodes[position_id].get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading PB{position_id}: {e}")
        return None
    
    async def read_emergency_kill(self) -> Optional[bool]:
        """Read emergency kill switch"""
        try:
            if self.kill_node:
                value = await self.kill_node.get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading emergency kill: {e}")
        return None
    
    async def read_all_states(self) -> Dict[str, Any]:
        """Read all system states efficiently"""
        states = {
            "leds": {},
            "buttons": {},
            "emergency_kill": False,
            "timestamp": datetime.now().isoformat(),
            "connection_quality": "good" if self.error_count < 10 else "poor"
        }
        
        try:
            # Read LEDs efficiently
            for pos_id in list(self.led_nodes.keys())[:10]:  # Read first 10 to avoid overwhelming
                led_state = await self.read_led_state(pos_id)
                if led_state is not None:
                    states["leds"][pos_id] = led_state
            
            # Read buttons efficiently  
            for pos_id in list(self.button_nodes.keys())[:10]:  # Read first 10
                button_state = await self.read_button_state(pos_id)
                if button_state is not None:
                    states["buttons"][pos_id] = button_state
            
            # Read emergency kill
            kill_state = await self.read_emergency_kill()
            if kill_state is not None:
                states["emergency_kill"] = kill_state
            
        except Exception as e:
            logger.error(f"Error reading system states: {e}")
            self.error_count += 1
        
        return states
    
    async def monitor_variable_changes(self, callback=None):
        """Monitor all variables for changes using user's proven pattern"""
        if not self.variable_nodes:
            logger.error("No variables to monitor")
            return
        
        logger.info(f"Starting variable monitoring on {len(self.variable_nodes)} variables...")
        
        # Read initial states (user's pattern)
        initial_states = {}
        for var_name, var_node in self.variable_nodes.items():
            try:
                value = await var_node.get_value()
                initial_states[var_name] = value
            except Exception as e:
                logger.warning(f"Could not read initial value for '{var_name}': {e}")
        
        logger.info("Initial state recorded. Monitoring for changes...")
        
        # Continuous monitoring (user's pattern)
        try:
            while self.connected:
                for var_name, var_node in self.variable_nodes.items():
                    if var_name not in initial_states:
                        continue
                    
                    try:
                        new_value = await var_node.get_value()
                        old_value = initial_states[var_name]
                        
                        if new_value != old_value:
                            logger.info(f"*** CHANGE DETECTED! ***")
                            logger.info(f"   Variable: '{var_name}'")
                            logger.info(f"   Old Value: {old_value}")
                            logger.info(f"   New Value: {new_value}")
                            
                            # Update state and call callback
                            initial_states[var_name] = new_value
                            
                            if callback:
                                await callback(var_name, old_value, new_value)
                            
                    except Exception as e:
                        logger.debug(f"Error reading variable '{var_name}': {e}")
                        if var_name in initial_states:
                            del initial_states[var_name]
                
                await asyncio.sleep(self.config['operation']['scan_interval'])
                
        except asyncio.CancelledError:
            logger.info("Variable monitoring cancelled")
        except Exception as e:
            logger.error(f"Variable monitoring error: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "connected": self.connected,
            "reads": self.read_count,
            "writes": self.write_count,
            "errors": self.error_count,
            "total_variables": len(self.variable_nodes),
            "led_nodes": len(self.led_nodes),
            "button_nodes": len(self.button_nodes),
            "emergency_node": self.kill_node is not None
        }

class PositionManager:
    """Enhanced position manager with statistics and validation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.positions: Dict[int, StoragePosition] = {}
        self.operation_history = []
        self._initialize_positions()
    
    def _initialize_positions(self):
        """Initialize all storage positions"""
        layout = self.config['rack']['layout']
        
        for i in range(1, self.config['rack']['positions'] + 1):
            row = ((i - 1) // layout['columns']) + 1
            column = ((i - 1) % layout['columns']) + 1
            
            self.positions[i] = StoragePosition(
                id=i,
                row=row,
                column=column,
                last_activity=datetime.now()
            )
        
        logger.info(f"Initialized {len(self.positions)} storage positions ({layout['rows']}×{layout['columns']})")
    
    def get_position(self, position_id: int) -> Optional[StoragePosition]:
        """Get position by ID with validation"""
        if 1 <= position_id <= self.config['rack']['positions']:
            return self.positions.get(position_id)
        return None
    
    def find_empty_position(self) -> Optional[StoragePosition]:
        """Find first available empty position"""
        for position in sorted(self.positions.values(), key=lambda p: p.id):
            if position.is_available:
                return position
        return None
    
    def find_product_position(self, product_id: str) -> Optional[StoragePosition]:
        """Find position containing specific product"""
        for position in self.positions.values():
            if position.product_id == product_id and position.status == PositionStatus.OCCUPIED:
                return position
        return None
    
    def find_product_positions(self, product_id: str) -> List[StoragePosition]:
        """Find all positions containing specific product"""
        return [
            position for position in self.positions.values()
            if position.product_id == product_id and position.status == PositionStatus.OCCUPIED
        ]
    
    def store_item(self, position_id: int, product_id: str) -> bool:
        """Store item with validation and logging"""
        position = self.get_position(position_id)
        
        if not position:
            logger.warning(f"Invalid position ID: {position_id}")
            return False
            
        if not position.is_available:
            logger.warning(f"Position {position_id} is not empty")
            return False
        
        # Store the item
        position.status = PositionStatus.OCCUPIED
        position.product_id = product_id
        position.stored_at = datetime.now()
        position.last_activity = datetime.now()
        position.led_state = True
        
        # Record operation
        self.operation_history.append({
            "type": "store",
            "position_id": position_id,
            "product_id": product_id,
            "timestamp": datetime.now()
        })
        
        logger.info(f"📦 Stored {product_id} in position {position_id}")
        return True
    
    def retrieve_item(self, position_id: int) -> Optional[str]:
        """Retrieve item with validation and logging"""
        position = self.get_position(position_id)
        
        if not position:
            logger.warning(f"Invalid position ID: {position_id}")
            return None
            
        if position.status != PositionStatus.OCCUPIED:
            logger.warning(f"Position {position_id} is empty")
            return None
        
        # Retrieve the item
        product_id = position.product_id
        position.status = PositionStatus.EMPTY
        position.product_id = None
        position.stored_at = None
        position.last_activity = datetime.now()
        position.led_state = False
        
        # Record operation
        self.operation_history.append({
            "type": "retrieve",
            "position_id": position_id,
            "product_id": product_id,
            "timestamp": datetime.now()
        })
        
        logger.info(f"📤 Retrieved {product_id} from position {position_id}")
        return product_id
    
    def get_grid_display(self) -> List[List[str]]:
        """Get visual grid representation"""
        layout = self.config['rack']['layout']
        grid = []
        
        for r in range(1, layout['rows'] + 1):
            row = []
            for c in range(1, layout['columns'] + 1):
                pos_id = ((r - 1) * layout['columns']) + c
                
                if pos_id <= self.config['rack']['positions']:
                    position = self.positions.get(pos_id)
                    if position and position.status == PositionStatus.OCCUPIED:
                        row.append(f"[{pos_id:02d}]")  # Occupied
                    else:
                        row.append(f" {pos_id:02d} ")   # Empty
                else:
                    row.append("    ")  # No position
            grid.append(row)
        
        return grid
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        total = len(self.positions)
        occupied = sum(1 for p in self.positions.values() if p.status == PositionStatus.OCCUPIED)
        
        # Product statistics
        products = {}
        for position in self.positions.values():
            if position.product_id:
                if position.product_id not in products:
                    products[position.product_id] = 0
                products[position.product_id] += 1
        
        # Recent activity
        recent_ops = sorted(self.operation_history[-10:], key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "total_positions": total,
            "occupied_positions": occupied,
            "empty_positions": total - occupied,
            "occupancy_percent": int((occupied / total) * 100) if total > 0 else 0,
            "layout": f"{self.config['rack']['layout']['rows']}×{self.config['rack']['layout']['columns']}",
            "unique_products": len(products),
            "total_operations": len(self.operation_history),
            "recent_activity": [
                {
                    "type": op["type"],
                    "position_id": op["position_id"],
                    "product_id": op["product_id"],
                    "timestamp": op["timestamp"].isoformat()
                } for op in recent_ops
            ]
        }
    
    def get_inventory_report(self) -> Dict[str, Any]:
        """Get detailed inventory report"""
        occupied_positions = [
            {
                "position_id": pos.id,
                "position_name": pos.position_name,
                "grid_location": pos.grid_location,
                "product_id": pos.product_id,
                "stored_at": pos.stored_at.isoformat() if pos.stored_at else None,
                "duration": (datetime.now() - pos.stored_at).total_seconds() / 3600 if pos.stored_at else 0
            }
            for pos in self.positions.values()
            if pos.status == PositionStatus.OCCUPIED
        ]
        
        return {
            "occupied_positions": sorted(occupied_positions, key=lambda x: x["position_id"]),
            "summary": self.get_statistics()
        }

print("✅ Core system (proven asyncua): asrs_core.py")
'''

with open('asrs_core.py', 'w') as f:
    f.write(core_proven_code)

print("✅ 2. Core system (proven asyncua): asrs_core.py")