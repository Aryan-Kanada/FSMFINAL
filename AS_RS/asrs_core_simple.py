"""
BVM AS/RS Core System - Simple Working Version
Uses your exact discovered variable names: A1/A1S, B1/B1S, etc.
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
    def plc_button_name(self) -> str:
        """Get PLC button variable name (A1, B2, etc.)"""
        row_letter = chr(ord('A') + self.row - 1)  # A, B, C, D, E
        return f"{row_letter}{self.column}"

    @property
    def plc_led_name(self) -> str:
        """Get PLC LED variable name (A1S, B2S, etc.)"""
        return f"{self.plc_button_name}S"

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

class SimpleWorkingOPCClient:
    """Simple working OPC UA client using discovered pattern"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False

        # Simple variable storage
        self.led_nodes = {}       # position_id -> node
        self.button_nodes = {}    # position_id -> node
        self.home_node = None

        # Statistics
        self.read_count = 0
        self.write_count = 0
        self.error_count = 0

        self.plc_url = self.config['plc']['url']

    async def connect(self) -> bool:
        """Connect and find variables using simple proven method"""
        try:
            logger.info(f"Attempting to connect to PLC at {self.plc_url}...")

            self.client = Client(url=self.plc_url)
            await self.client.connect()
            self.connected = True
            logger.info("Successfully connected to the PLC!")

            # Find variables using proven simple method
            success = await self._find_variables_simple()
            return success

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

    async def _find_variables_simple(self):
        """Find variables using the proven simple method"""
        try:
            logger.info("Finding variables using simple proven method...")

            # Use exact same pattern as working explorer
            current_node = self.client.get_objects_node()
            current_node = await current_node.get_child("4:new_Controller_0")
            globalvars_node = await current_node.get_child("3:GlobalVars")

            variables = await globalvars_node.get_children()
            logger.info(f"Found {len(variables)} variables in GlobalVars")

            if not variables:
                logger.error("No variables found!")
                return False

            # Create lookup by name
            var_by_name = {}
            for var_node in variables:
                try:
                    browse_name = await var_node.read_browse_name()
                    var_name = browse_name.Name
                    var_by_name[var_name] = var_node
                except:
                    continue

            # Map to position IDs using discovered pattern
            led_count = 0
            button_count = 0

            # Generate all expected variable names
            for row in range(1, 6):  # A-E (rows 1-5)
                for col in range(1, 8):  # 1-7 (columns 1-7)
                    position_id = ((row - 1) * 7) + col  # 1-35

                    row_letter = chr(ord('A') + row - 1)  # A, B, C, D, E
                    button_name = f"{row_letter}{col}"    # A1, B2, etc.
                    led_name = f"{button_name}S"          # A1S, B2S, etc.

                    # Look for button
                    if button_name in var_by_name:
                        self.button_nodes[position_id] = var_by_name[button_name]
                        button_count += 1

                    # Look for LED
                    if led_name in var_by_name:
                        self.led_nodes[position_id] = var_by_name[led_name]
                        led_count += 1

            # Look for Home (emergency)
            if "Home" in var_by_name:
                self.home_node = var_by_name["Home"]

            logger.info(f"✅ Mapped variables:")
            logger.info(f"   LEDs: {led_count}/35")
            logger.info(f"   Buttons: {button_count}/35") 
            logger.info(f"   Emergency: {'Yes' if self.home_node else 'No'}")

            return led_count > 0 and button_count > 0

        except Exception as e:
            logger.error(f"Failed to find variables: {e}")
            return False

    async def read_led_state(self, position_id: int) -> Optional[bool]:
        """Read LED state"""
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
        """Write LED state"""
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
        """Read button state"""
        try:
            if position_id in self.button_nodes:
                value = await self.button_nodes[position_id].get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading Button{position_id}: {e}")
        return None

    async def read_emergency_kill(self) -> Optional[bool]:
        """Read emergency Home switch"""
        try:
            if self.home_node:
                value = await self.home_node.get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading Home: {e}")
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
            # Read first 10 LEDs
            for pos_id in list(self.led_nodes.keys())[:10]:
                led_state = await self.read_led_state(pos_id)
                if led_state is not None:
                    states["leds"][pos_id] = led_state

            # Read first 10 buttons  
            for pos_id in list(self.button_nodes.keys())[:10]:
                button_state = await self.read_button_state(pos_id)
                if button_state is not None:
                    states["buttons"][pos_id] = button_state

            # Read emergency
            home_state = await self.read_emergency_kill()
            if home_state is not None:
                states["emergency_kill"] = home_state

        except Exception as e:
            logger.error(f"Error reading system states: {e}")
            self.error_count += 1

        return states

    async def monitor_variable_changes(self, callback=None):
        """Simple variable monitoring"""
        logger.info("Variable monitoring not implemented in simple version")
        # Just sleep to avoid CPU usage
        try:
            while self.connected:
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            logger.info("Variable monitoring cancelled")

    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "connected": self.connected,
            "reads": self.read_count,
            "writes": self.write_count,
            "errors": self.error_count,
            "total_variables": 71,  # We know there are 71
            "led_nodes": len(self.led_nodes),
            "button_nodes": len(self.button_nodes),
            "emergency_node": self.home_node is not None
        }

# Use the simple client instead of the complex one
ProvenAsyncOPCClient = SimpleWorkingOPCClient

class PositionManager:
    """Position manager with 5x7 grid"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.positions: Dict[int, StoragePosition] = {}
        self.operation_history = []
        self._initialize_positions()

    def _initialize_positions(self):
        """Initialize 35 positions (5×7 grid)"""
        for row in range(1, 6):  # A=1, B=2, C=3, D=4, E=5
            for column in range(1, 8):  # 1, 2, 3, 4, 5, 6, 7
                position_id = ((row - 1) * 7) + column  # 1-35

                self.positions[position_id] = StoragePosition(
                    id=position_id,
                    row=row,
                    column=column,
                    last_activity=datetime.now()
                )

        logger.info(f"Initialized {len(self.positions)} storage positions (5×7 grid)")

    def get_position(self, position_id: int) -> Optional[StoragePosition]:
        """Get position by ID"""
        if 1 <= position_id <= 35:
            return self.positions.get(position_id)
        return None

    def find_empty_position(self) -> Optional[StoragePosition]:
        """Find first empty position"""
        for position in sorted(self.positions.values(), key=lambda p: p.id):
            if position.is_available:
                return position
        return None

    def find_product_position(self, product_id: str) -> Optional[StoragePosition]:
        """Find position with product"""
        for position in self.positions.values():
            if position.product_id == product_id and position.status == PositionStatus.OCCUPIED:
                return position
        return None

    def find_product_positions(self, product_id: str) -> List[StoragePosition]:
        """Find all positions with product"""
        return [
            position for position in self.positions.values()
            if position.product_id == product_id and position.status == PositionStatus.OCCUPIED
        ]

    def store_item(self, position_id: int, product_id: str) -> bool:
        """Store item"""
        position = self.get_position(position_id)

        if not position or not position.is_available:
            return False

        position.status = PositionStatus.OCCUPIED
        position.product_id = product_id
        position.stored_at = datetime.now()
        position.last_activity = datetime.now()
        position.led_state = True

        self.operation_history.append({
            "type": "store",
            "position_id": position_id,
            "product_id": product_id,
            "timestamp": datetime.now()
        })

        logger.info(f"📦 Stored {product_id} in position {position_id}")
        return True

    def retrieve_item(self, position_id: int) -> Optional[str]:
        """Retrieve item"""
        position = self.get_position(position_id)

        if not position or position.status != PositionStatus.OCCUPIED:
            return None

        product_id = position.product_id
        position.status = PositionStatus.EMPTY
        position.product_id = None
        position.stored_at = None
        position.last_activity = datetime.now()
        position.led_state = False

        self.operation_history.append({
            "type": "retrieve",
            "position_id": position_id,
            "product_id": product_id,
            "timestamp": datetime.now()
        })

        logger.info(f"📤 Retrieved {product_id} from position {position_id}")
        return product_id

    def get_grid_display(self) -> List[List[str]]:
        """Get 5×7 grid display"""
        grid = []

        for r in range(1, 6):  # 5 rows
            row = []
            for c in range(1, 8):  # 7 columns
                pos_id = ((r - 1) * 7) + c

                position = self.positions.get(pos_id)
                if position and position.status == PositionStatus.OCCUPIED:
                    row.append(f"[{pos_id:02d}]")
                else:
                    row.append(f" {pos_id:02d} ")
            grid.append(row)

        return grid

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        total = len(self.positions)
        occupied = sum(1 for p in self.positions.values() if p.status == PositionStatus.OCCUPIED)

        return {
            "total_positions": total,
            "occupied_positions": occupied,
            "empty_positions": total - occupied,
            "occupancy_percent": int((occupied / total) * 100) if total > 0 else 0,
            "layout": "5×7",
            "unique_products": len(set(p.product_id for p in self.positions.values() if p.product_id)),
            "total_operations": len(self.operation_history)
        }

    def get_inventory_report(self) -> Dict[str, Any]:
        """Get inventory report"""
        occupied_positions = [
            {
                "position_id": pos.id,
                "position_name": pos.position_name,
                "grid_location": pos.grid_location,
                "plc_names": f"{pos.plc_button_name}/{pos.plc_led_name}",
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

print("✅ Simple working core system created")
