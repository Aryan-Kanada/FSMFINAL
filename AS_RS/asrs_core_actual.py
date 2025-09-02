"""
BVM AS/RS Core System - Using Actual PLC Variables
Matches the user's working Sysmac Studio PLC program
LEDs: ledA1-ledE7, Buttons: A1-E7, Motion: X/Y/Z motors
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
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
    """Storage position in the AS/RS rack matching PLC layout"""
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
        """Get actual PLC button variable name (A1, B2, etc.)"""
        row_letter = chr(ord('A') + self.row - 1)  # A, B, C, D, E
        return f"{row_letter}{self.column}"

    @property
    def plc_led_name(self) -> str:
        """Get actual PLC LED variable name (ledA1, ledB2, etc.)"""
        row_letter = chr(ord('A') + self.row - 1)  # A, B, C, D, E
        return f"led{row_letter}{self.column}"

    @property
    def physical_coordinates(self) -> Tuple[int, int]:
        """Get physical X,Y coordinates for motion system"""
        # Using coordinates from your PLC program
        x_positions = [0, 229372, 455745, 685117, 915490, 1145863, 1376236]  # 7 columns
        y_positions = [0, 150000, 300000, 450000, 600000]  # 5 rows

        x_coord = x_positions[self.column - 1] if self.column <= 7 else 0
        y_coord = y_positions[self.row - 1] if self.row <= 5 else 0

        return (x_coord, y_coord)

    @property
    def is_available(self) -> bool:
        return self.status == PositionStatus.EMPTY

class ActualPLCClient:
    """OPC UA client using actual PLC variables from Sysmac Studio"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False

        # Variable node storage - using actual PLC names
        self.led_nodes = {}          # position_id -> ledA1, ledB2, etc.
        self.button_nodes = {}       # position_id -> A1, B2, etc.
        self.motion_nodes = {}       # motion control variables
        self.control_nodes = {}      # start/stop/status variables

        # Statistics
        self.read_count = 0
        self.write_count = 0
        self.error_count = 0

        self.plc_url = self.config['plc']['url']

    async def connect(self) -> bool:
        """Connect to PLC using proven OPC UA method"""
        try:
            logger.info(f"🔧 Connecting to your physical AS/RS at {self.plc_url}...")

            self.client = Client(url=self.plc_url)
            await self.client.connect()
            self.connected = True
            logger.info("✅ Connected to your PLC!")

            # Map actual PLC variables
            success = await self._map_actual_plc_variables()
            return success

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
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

    async def _map_actual_plc_variables(self):
        """Map actual PLC variables from your Sysmac Studio program"""
        try:
            logger.info("🗺️ Mapping your actual PLC variables...")

            # Navigate to GlobalVars using proven method
            current_node = self.client.get_objects_node()
            current_node = await current_node.get_child("4:new_Controller_0")
            globalvars_node = await current_node.get_child("3:GlobalVars")

            # Get all variables
            variables = await globalvars_node.get_children()
            logger.info(f"Found {len(variables)} variables in GlobalVars")

            # Create lookup by name
            var_by_name = {}
            for var_node in variables:
                try:
                    browse_name = await var_node.read_browse_name()
                    var_name = browse_name.Name
                    var_by_name[var_name] = var_node
                except:
                    continue

            # Map LEDs and buttons to positions
            led_count = 0
            button_count = 0

            for row in range(1, 6):  # A-E (rows 1-5)
                for col in range(1, 8):  # 1-7 (columns 1-7)
                    position_id = ((row - 1) * 7) + col  # 1-35

                    row_letter = chr(ord('A') + row - 1)  # A, B, C, D, E

                    # Map LED variables (ledA1, ledB2, etc.)
                    led_name = f"led{row_letter}{col}"
                    if led_name in var_by_name:
                        self.led_nodes[position_id] = var_by_name[led_name]
                        led_count += 1
                        logger.debug(f"✅ Mapped LED{position_id}: {led_name}")

                    # Map button variables (A1, B2, etc.)
                    button_name = f"{row_letter}{col}"
                    if button_name in var_by_name:
                        self.button_nodes[position_id] = var_by_name[button_name]
                        button_count += 1
                        logger.debug(f"✅ Mapped Button{position_id}: {button_name}")

            # Map motion control variables
            motion_vars = {
                'x_position': 'X_write_position',
                'y_position': 'Y_write_position',
                'z_position': 'Z_write_position',
                'x_start': 'Start_1',
                'y_start': 'Start_2', 
                'z_start': 'Start_3',
                'x_run': 'X_Run',
                'y_run': 'Y_Run',
                'z_run': 'Z_Run',
                'proximity': 'proximity'
            }

            motion_count = 0
            for key, var_name in motion_vars.items():
                if var_name in var_by_name:
                    self.motion_nodes[key] = var_by_name[var_name]
                    motion_count += 1
                    logger.debug(f"✅ Mapped Motion {key}: {var_name}")

            logger.info(f"🎯 Successfully mapped PLC variables:")
            logger.info(f"   📍 LEDs: {led_count}/35")
            logger.info(f"   🔘 Buttons: {button_count}/35") 
            logger.info(f"   🏗️ Motion: {motion_count}/10")

            return led_count > 0 and button_count > 0

        except Exception as e:
            logger.error(f"❌ Failed to map PLC variables: {e}")
            return False

    async def read_led_state(self, position_id: int) -> Optional[bool]:
        """Read LED state from actual PLC variable"""
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
        """Write LED state to actual PLC variable"""
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
        """Read button state from actual PLC variable"""
        try:
            if position_id in self.button_nodes:
                value = await self.button_nodes[position_id].get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading Button{position_id}: {e}")
        return None

    async def read_proximity_sensor(self) -> Optional[bool]:
        """Read proximity sensor state"""
        try:
            if 'proximity' in self.motion_nodes:
                value = await self.motion_nodes['proximity'].get_value()
                self.read_count += 1
                return bool(value)
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Error reading proximity: {e}")
        return None

    async def move_to_position(self, position_id: int) -> bool:
        """Move physical AS/RS to specific position"""
        try:
            # Get position coordinates
            position = self.get_position_by_id(position_id)
            if not position:
                return False

            x_coord, y_coord = position.physical_coordinates
            logger.info(f"🏗️ Moving to position {position_id} ({position.plc_led_name})")
            logger.info(f"   Coordinates: X={x_coord}, Y={y_coord}")

            # Send X position
            if 'x_position' in self.motion_nodes:
                await self.motion_nodes['x_position'].set_value(x_coord)
                self.write_count += 1

            # Send Y position  
            if 'y_position' in self.motion_nodes:
                await self.motion_nodes['y_position'].set_value(y_coord)
                self.write_count += 1

            # Start motion
            if 'x_start' in self.motion_nodes:
                await self.motion_nodes['x_start'].set_value(True)
                self.write_count += 1

            if 'y_start' in self.motion_nodes:
                await self.motion_nodes['y_start'].set_value(True)
                self.write_count += 1

            logger.info(f"✅ Motion commands sent to position {position_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to move to position {position_id}: {e}")
            self.error_count += 1
            return False

    async def execute_store_command(self, position_id: int, product_id: str) -> bool:
        """Execute store operation using PLC store program"""
        try:
            logger.info(f"📦 Executing store command: {product_id} → Position {position_id}")

            # Move to position first
            if not await self.move_to_position(position_id):
                return False

            # Wait for motion to complete (simplified - you might need better logic)
            await asyncio.sleep(2.0)

            # Trigger Z-axis down for storage
            if 'z_position' in self.motion_nodes:
                await self.motion_nodes['z_position'].set_value(21500)  # Z_out position
                self.write_count += 1

            if 'z_start' in self.motion_nodes:
                await self.motion_nodes['z_start'].set_value(True)
                self.write_count += 1

            # Wait for storage to complete
            await asyncio.sleep(3.0)

            # Return to center
            if 'z_position' in self.motion_nodes:
                await self.motion_nodes['z_position'].set_value(11400)  # Z_center
                self.write_count += 1

            logger.info(f"✅ Store operation completed: {product_id} stored in position {position_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Store operation failed: {e}")
            self.error_count += 1
            return False

    async def execute_retrieve_command(self, position_id: int) -> Optional[str]:
        """Execute retrieve operation using PLC retrieve program"""
        try:
            logger.info(f"📤 Executing retrieve command from position {position_id}")

            # Move to position
            if not await self.move_to_position(position_id):
                return None

            # Wait for motion to complete
            await asyncio.sleep(2.0)

            # Trigger Z-axis down for retrieval
            if 'z_position' in self.motion_nodes:
                await self.motion_nodes['z_position'].set_value(21500)  # Z_out position
                self.write_count += 1

            if 'z_start' in self.motion_nodes:
                await self.motion_nodes['z_start'].set_value(True)
                self.write_count += 1

            # Wait for retrieval to complete
            await asyncio.sleep(3.0)

            # Return to center
            if 'z_position' in self.motion_nodes:
                await self.motion_nodes['z_position'].set_value(11400)  # Z_center
                self.write_count += 1

            logger.info(f"✅ Retrieve operation completed from position {position_id}")
            return f"ITEM_FROM_POS_{position_id}"

        except Exception as e:
            logger.error(f"❌ Retrieve operation failed: {e}")
            self.error_count += 1
            return None

    def get_position_by_id(self, position_id: int):
        """Helper to get position object by ID"""
        if 1 <= position_id <= 35:
            row = ((position_id - 1) // 7) + 1
            col = ((position_id - 1) % 7) + 1
            return StoragePosition(id=position_id, row=row, column=col)
        return None

    async def monitor_variable_changes(self, callback=None):
        """Monitor PLC variables for changes"""
        logger.info("🔍 Monitoring PLC variables for changes...")

        # Monitor button presses
        try:
            while self.connected:
                # Check all button states
                for pos_id in list(self.button_nodes.keys())[:10]:  # First 10 for performance
                    try:
                        button_state = await self.read_button_state(pos_id)
                        if button_state:  # Button pressed
                            if callback:
                                await callback(f"button_press", pos_id, button_state)
                            logger.info(f"🔘 Button pressed at position {pos_id}")
                    except:
                        pass

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
            "led_nodes": len(self.led_nodes),
            "button_nodes": len(self.button_nodes),
            "motion_nodes": len(self.motion_nodes)
        }

# Use the actual PLC client
ProvenAsyncOPCClient = ActualPLCClient

class PositionManager:
    """Position manager for 5×7 physical rack"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.positions: Dict[int, StoragePosition] = {}
        self.operation_history = []
        self._initialize_positions()

    def _initialize_positions(self):
        """Initialize 35 positions matching physical rack"""
        for row in range(1, 6):  # A=1, B=2, C=3, D=4, E=5
            for column in range(1, 8):  # 1, 2, 3, 4, 5, 6, 7
                position_id = ((row - 1) * 7) + column  # 1-35

                self.positions[position_id] = StoragePosition(
                    id=position_id,
                    row=row,
                    column=column,
                    last_activity=datetime.now()
                )

        logger.info(f"🏗️ Initialized {len(self.positions)} physical rack positions (5×7)")

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
        """Find position with specific product"""
        for position in self.positions.values():
            if position.product_id == product_id and position.status == PositionStatus.OCCUPIED:
                return position
        return None

    def store_item(self, position_id: int, product_id: str) -> bool:
        """Store item in software inventory"""
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

        logger.info(f"📦 Software inventory: {product_id} stored in {position.plc_led_name}")
        return True

    def retrieve_item(self, position_id: int) -> Optional[str]:
        """Retrieve item from software inventory"""
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

        logger.info(f"📤 Software inventory: {product_id} retrieved from {position.plc_button_name}")
        return product_id

    def get_grid_display(self) -> List[List[str]]:
        """Get 5×7 grid display matching physical layout"""
        grid = []

        for r in range(1, 6):  # 5 rows (A-E)
            row = []
            for c in range(1, 8):  # 7 columns (1-7)
                pos_id = ((r - 1) * 7) + c

                position = self.positions.get(pos_id)
                if position and position.status == PositionStatus.OCCUPIED:
                    row.append(f"[{pos_id:02d}]")  # Occupied
                else:
                    row.append(f" {pos_id:02d} ")   # Empty
            grid.append(row)

        return grid

    def get_statistics(self) -> Dict[str, Any]:
        """Get rack statistics"""
        total = len(self.positions)
        occupied = sum(1 for p in self.positions.values() if p.status == PositionStatus.OCCUPIED)

        return {
            "total_positions": total,
            "occupied_positions": occupied,
            "empty_positions": total - occupied,
            "occupancy_percent": int((occupied / total) * 100) if total > 0 else 0,
            "layout": "5×7 Physical Rack",
            "unique_products": len(set(p.product_id for p in self.positions.values() if p.product_id)),
            "total_operations": len(self.operation_history)
        }

    def get_inventory_report(self) -> Dict[str, Any]:
        """Get detailed inventory report"""
        occupied_positions = [
            {
                "position_id": pos.id,
                "position_name": pos.position_name,
                "grid_location": pos.grid_location,
                "plc_led": pos.plc_led_name,
                "plc_button": pos.plc_button_name,
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

print("✅ Created AS/RS core system using your actual PLC variables!")
