"""
BVM AS/RS Core System
Async OPC UA communication with OMRON NX102-9000 PLC
Based on working asyncua connection pattern
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from asyncua import Client
from asyncua.ua import UaError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    MONITORING = "monitoring"
    STORING = "storing"
    RETRIEVING = "retrieving"
    ERROR = "error"
    EMERGENCY = "emergency"

class PositionStatus(Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    ERROR = "error"

@dataclass
class StoragePosition:
    """Storage position in the rack"""
    id: int
    row: int
    column: int
    status: PositionStatus = PositionStatus.EMPTY
    product_id: Optional[str] = None
    stored_at: Optional[datetime] = None
    led_state: bool = False
    button_pressed: bool = False

    @property
    def position_name(self) -> str:
        return f"P{self.id:02d}"

    @property
    def grid_location(self) -> str:
        return f"R{self.row}C{self.column}"

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

class AsyncOPCClient:
    """Async OPC UA client for OMRON PLC communication"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False
        self.variables_node = None
        self.led_nodes = {}
        self.button_nodes = {}
        self.kill_node = None

    async def connect(self) -> bool:
        """Connect to PLC and initialize variable nodes"""
        try:
            logger.info(f"Connecting to PLC at {self.config['plc']['url']}...")

            self.client = Client(url=self.config['plc']['url'])
            self.client.set_session_timeout(self.config['plc']['timeout'] * 1000)

            await self.client.connect()
            self.connected = True
            logger.info("Successfully connected to PLC!")

            # Navigate to variables folder using proven path
            await self._initialize_variable_nodes()

            return True

        except Exception as e:
            logger.error(f"Failed to connect to PLC: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from PLC"""
        if self.client and self.connected:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from PLC")
            except:
                pass

    async def _initialize_variable_nodes(self):
        """Initialize variable nodes using the proven path navigation"""
        try:
            # Navigate to variables folder
            current_node = self.client.get_objects_node()

            # Follow the known path: Objects -> new_Controller_0 -> GlobalVars
            for part in self.config['paths']['base_path'][1:]:  # Skip "0:Objects"
                current_node = await current_node.get_child(part)

            # Try to get GlobalVars folder
            try:
                self.variables_node = await current_node.get_child(self.config['paths']['variables_folder'])
                logger.info("Found GlobalVars folder")
            except:
                # If GlobalVars doesn't exist, list available children
                logger.warning("GlobalVars folder not found. Available folders:")
                children = await current_node.get_children()
                for child in children:
                    browse_name = await child.read_browse_name()
                    logger.info(f"  - {browse_name.Name}")

                # Use the current node as variables node for now
                self.variables_node = current_node

            # Initialize LED nodes
            for i, led_name in enumerate(self.config['rack']['variables']['leds'], 1):
                try:
                    node = await self.variables_node.get_child(f"4:{led_name}")
                    self.led_nodes[i] = node
                    logger.debug(f"Initialized LED node: {led_name}")
                except Exception as e:
                    logger.warning(f"Could not find LED node {led_name}: {e}")

            # Initialize button nodes
            for i, button_name in enumerate(self.config['rack']['variables']['buttons'], 1):
                try:
                    node = await self.variables_node.get_child(f"4:{button_name}")
                    self.button_nodes[i] = node
                    logger.debug(f"Initialized button node: {button_name}")
                except Exception as e:
                    logger.warning(f"Could not find button node {button_name}: {e}")

            # Initialize emergency kill node
            try:
                self.kill_node = await self.variables_node.get_child(f"4:{self.config['rack']['variables']['emergency']}")
                logger.debug("Initialized emergency kill node")
            except Exception as e:
                logger.warning(f"Could not find emergency kill node: {e}")

            logger.info(f"Initialized {len(self.led_nodes)} LED nodes, {len(self.button_nodes)} button nodes")

        except Exception as e:
            logger.error(f"Failed to initialize variable nodes: {e}")
            raise

    async def read_led_state(self, position_id: int) -> Optional[bool]:
        """Read LED state for position"""
        try:
            if position_id in self.led_nodes:
                value = await self.led_nodes[position_id].read_value()
                return bool(value)
        except Exception as e:
            logger.error(f"Error reading LED{position_id}: {e}")
        return None

    async def write_led_state(self, position_id: int, state: bool) -> bool:
        """Write LED state for position"""
        try:
            if position_id in self.led_nodes:
                await self.led_nodes[position_id].write_value(state)
                logger.debug(f"LED{position_id} set to {state}")
                return True
        except Exception as e:
            logger.error(f"Error writing LED{position_id}: {e}")
        return False

    async def read_button_state(self, position_id: int) -> Optional[bool]:
        """Read button state for position"""
        try:
            if position_id in self.button_nodes:
                value = await self.button_nodes[position_id].read_value()
                return bool(value)
        except Exception as e:
            logger.error(f"Error reading button{position_id}: {e}")
        return None

    async def read_emergency_kill(self) -> Optional[bool]:
        """Read emergency kill switch state"""
        try:
            if self.kill_node:
                value = await self.kill_node.read_value()
                return bool(value)
        except Exception as e:
            logger.error(f"Error reading emergency kill: {e}")
        return None

    async def read_all_states(self) -> Dict[str, Any]:
        """Read all system states"""
        states = {
            "leds": {},
            "buttons": {},
            "emergency_kill": False,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Read all LEDs
            for pos_id in self.led_nodes:
                states["leds"][pos_id] = await self.read_led_state(pos_id)

            # Read all buttons
            for pos_id in self.button_nodes:
                states["buttons"][pos_id] = await self.read_button_state(pos_id)

            # Read emergency kill
            states["emergency_kill"] = await self.read_emergency_kill()

        except Exception as e:
            logger.error(f"Error reading all states: {e}")

        return states

class PositionManager:
    """Manages storage positions and inventory"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.positions: Dict[int, StoragePosition] = {}
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
                column=column
            )

        logger.info(f"Initialized {len(self.positions)} storage positions")

    def get_position(self, position_id: int) -> Optional[StoragePosition]:
        """Get position by ID"""
        return self.positions.get(position_id)

    def find_empty_position(self) -> Optional[StoragePosition]:
        """Find first available empty position"""
        for position in self.positions.values():
            if position.status == PositionStatus.EMPTY:
                return position
        return None

    def find_product_position(self, product_id: str) -> Optional[StoragePosition]:
        """Find position containing specific product"""
        for position in self.positions.values():
            if position.product_id == product_id:
                return position
        return None

    def store_item(self, position_id: int, product_id: str) -> bool:
        """Store item in position"""
        position = self.positions.get(position_id)
        if position and position.status == PositionStatus.EMPTY:
            position.status = PositionStatus.OCCUPIED
            position.product_id = product_id
            position.stored_at = datetime.now()
            position.led_state = True
            return True
        return False

    def retrieve_item(self, position_id: int) -> Optional[str]:
        """Retrieve item from position"""
        position = self.positions.get(position_id)
        if position and position.status == PositionStatus.OCCUPIED:
            product_id = position.product_id
            position.status = PositionStatus.EMPTY
            position.product_id = None
            position.stored_at = None
            position.led_state = False
            return product_id
        return None

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
        """Get occupancy statistics"""
        total = len(self.positions)
        occupied = sum(1 for p in self.positions.values() if p.status == PositionStatus.OCCUPIED)

        return {
            "total_positions": total,
            "occupied_positions": occupied,
            "empty_positions": total - occupied,
            "occupancy_percent": int((occupied / total) * 100),
            "layout": f"{self.config['rack']['layout']['rows']}×{self.config['rack']['layout']['columns']}"
        }

print("✅ Core AS/RS system created")
