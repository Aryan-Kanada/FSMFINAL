"""
BVM AS/RS Main Controller
Orchestrates all AS/RS operations with async OPC UA communication
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import queue
import threading
from asrs_core import *

logger = logging.getLogger(__name__)

class ASRSController:
    """Main AS/RS system controller"""

    def __init__(self, config_path: str = "asrs_config.json"):
        self.config = self._load_config(config_path)
        self.opc_client = AsyncOPCClient(self.config)
        self.position_manager = PositionManager(self.config)

        self.status = SystemStatus.DISCONNECTED
        self.running = False
        self.monitoring_task = None
        self.task_queue = asyncio.Queue()
        self.completed_tasks = []
        self.active_task = None

        # Button state tracking for debouncing
        self.last_button_states = {}
        self.last_button_time = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {config_path}: {e}")
            raise

    async def initialize(self) -> bool:
        """Initialize the AS/RS system"""
        try:
            logger.info("Initializing BVM AS/RS system...")
            self.status = SystemStatus.CONNECTING

            # Connect to PLC
            if not await self.opc_client.connect():
                self.status = SystemStatus.ERROR
                return False

            self.status = SystemStatus.CONNECTED
            logger.info("AS/RS system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AS/RS system: {e}")
            self.status = SystemStatus.ERROR
            return False

    async def start(self):
        """Start the AS/RS system"""
        if self.running:
            logger.warning("AS/RS system is already running")
            return

        logger.info("Starting AS/RS system...")
        self.running = True
        self.status = SystemStatus.MONITORING

        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        # Start task processor
        asyncio.create_task(self._task_processing_loop())

        logger.info("AS/RS system started successfully")

    async def stop(self):
        """Stop the AS/RS system"""
        logger.info("Stopping AS/RS system...")
        self.running = False

        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Disconnect from PLC
        await self.opc_client.disconnect()

        self.status = SystemStatus.DISCONNECTED
        logger.info("AS/RS system stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Monitoring loop started")

        try:
            while self.running:
                await self._update_system_states()
                await self._check_button_presses()
                await self._check_emergency_stop()
                await self._sync_leds()

                await asyncio.sleep(self.config['operation']['scan_interval'])

        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.status = SystemStatus.ERROR

    async def _update_system_states(self):
        """Update all system states from PLC"""
        try:
            states = await self.opc_client.read_all_states()

            # Update position states
            for pos_id, position in self.position_manager.positions.items():
                if pos_id in states["leds"]:
                    # LED state from PLC might be different from our tracking
                    actual_led_state = states["leds"][pos_id]
                    if actual_led_state is not None:
                        position.led_state = actual_led_state

                if pos_id in states["buttons"]:
                    button_state = states["buttons"][pos_id]
                    if button_state is not None:
                        position.button_pressed = button_state

        except Exception as e:
            logger.error(f"Error updating system states: {e}")

    async def _check_button_presses(self):
        """Check for button presses and handle debouncing"""
        try:
            current_time = datetime.now().timestamp()
            debounce_time = self.config['operation']['button_debounce']

            for pos_id, position in self.position_manager.positions.items():
                # Check if button was pressed (transition from False to True)
                last_state = self.last_button_states.get(pos_id, False)
                current_state = position.button_pressed

                if current_state and not last_state:  # Button just pressed
                    last_press_time = self.last_button_time.get(pos_id, 0)

                    if current_time - last_press_time > debounce_time:
                        await self._handle_button_press(pos_id)
                        self.last_button_time[pos_id] = current_time

                self.last_button_states[pos_id] = current_state

        except Exception as e:
            logger.error(f"Error checking button presses: {e}")

    async def _handle_button_press(self, position_id: int):
        """Handle button press event"""
        position = self.position_manager.get_position(position_id)
        if position:
            logger.info(f"Button pressed: Position {position_id}")

            if position.status == PositionStatus.OCCUPIED:
                # Auto-retrieve item
                task = ASRSTask(
                    id=f"AUTO_RETRIEVE_{position_id}_{datetime.now().strftime('%H%M%S')}",
                    type="retrieve",
                    position_id=position_id
                )
                await self.submit_task(task)
            else:
                logger.info(f"Button pressed on empty position {position_id}")

    async def _check_emergency_stop(self):
        """Check emergency stop status"""
        try:
            emergency_state = await self.opc_client.read_emergency_kill()

            if emergency_state:
                logger.error("EMERGENCY STOP ACTIVATED!")
                self.status = SystemStatus.EMERGENCY
                # Turn off all LEDs for safety
                for pos_id in range(1, self.config['rack']['positions'] + 1):
                    await self.opc_client.write_led_state(pos_id, False)

                # Clear task queue
                while not self.task_queue.empty():
                    try:
                        task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                        task.status = "cancelled"
                        task.result = "Emergency stop activated"
                        self.completed_tasks.append(task)
                    except asyncio.TimeoutError:
                        break

                # Stop system
                await self.stop()

        except Exception as e:
            logger.error(f"Error checking emergency stop: {e}")

    async def _sync_leds(self):
        """Synchronize LED states with position occupancy"""
        if not self.config['operation']['auto_led_update']:
            return

        try:
            for pos_id, position in self.position_manager.positions.items():
                expected_state = position.status == PositionStatus.OCCUPIED

                if position.led_state != expected_state:
                    success = await self.opc_client.write_led_state(pos_id, expected_state)
                    if success:
                        position.led_state = expected_state

        except Exception as e:
            logger.error(f"Error syncing LEDs: {e}")

    async def _task_processing_loop(self):
        """Process tasks from the queue"""
        logger.info("Task processing loop started")

        try:
            while self.running:
                try:
                    # Wait for task with timeout
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    await self._execute_task(task)
                except asyncio.TimeoutError:
                    continue  # No task available, continue monitoring

        except Exception as e:
            logger.error(f"Error in task processing loop: {e}")

    async def _execute_task(self, task: ASRSTask):
        """Execute a task"""
        try:
            self.active_task = task
            task.started_at = datetime.now()
            task.status = "in_progress"

            logger.info(f"Executing task {task.id}: {task.type}")

            success = False
            if task.type == "store":
                success = await self._execute_store_task(task)
            elif task.type == "retrieve":
                success = await self._execute_retrieve_task(task)
            elif task.type == "update_display":
                success = await self._execute_update_display_task(task)
            else:
                task.result = f"Unknown task type: {task.type}"

            task.completed_at = datetime.now()
            task.status = "completed" if success else "failed"
            self.completed_tasks.append(task)

            logger.info(f"Task {task.id} {'completed' if success else 'failed'}")

        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            task.status = "failed"
            task.result = str(e)
            task.completed_at = datetime.now()

        finally:
            self.active_task = None

    async def _execute_store_task(self, task: ASRSTask) -> bool:
        """Execute store operation"""
        try:
            if task.position_id:
                position = self.position_manager.get_position(task.position_id)
            else:
                position = self.position_manager.find_empty_position()
                if position:
                    task.position_id = position.id

            if not position:
                task.result = "No empty position available"
                return False

            if position.status != PositionStatus.EMPTY:
                task.result = f"Position {position.id} is not empty"
                return False

            # Store item in position manager
            success = self.position_manager.store_item(position.id, task.product_id)
            if success:
                # Update LED
                await self.opc_client.write_led_state(position.id, True)
                task.result = f"Stored {task.product_id} in position {position.id}"
                return True
            else:
                task.result = "Failed to store item"
                return False

        except Exception as e:
            task.result = f"Store operation failed: {e}"
            return False

    async def _execute_retrieve_task(self, task: ASRSTask) -> bool:
        """Execute retrieve operation"""
        try:
            position = self.position_manager.get_position(task.position_id)
            if not position:
                task.result = f"Invalid position {task.position_id}"
                return False

            if position.status != PositionStatus.OCCUPIED:
                task.result = f"Position {task.position_id} is empty"
                return False

            # Retrieve item from position manager
            product_id = self.position_manager.retrieve_item(task.position_id)
            if product_id:
                # Update LED
                await self.opc_client.write_led_state(task.position_id, False)
                task.result = f"Retrieved {product_id} from position {task.position_id}"
                return True
            else:
                task.result = "Failed to retrieve item"
                return False

        except Exception as e:
            task.result = f"Retrieve operation failed: {e}"
            return False

    async def _execute_update_display_task(self, task: ASRSTask) -> bool:
        """Execute display update operation"""
        try:
            # Update all LEDs to match position states
            for pos_id, position in self.position_manager.positions.items():
                expected_state = position.status == PositionStatus.OCCUPIED
                await self.opc_client.write_led_state(pos_id, expected_state)

            task.result = "Display updated successfully"
            return True

        except Exception as e:
            task.result = f"Display update failed: {e}"
            return False

    async def submit_task(self, task: ASRSTask) -> bool:
        """Submit task to the queue"""
        try:
            await self.task_queue.put(task)
            logger.info(f"Task {task.id} submitted")
            return True
        except Exception as e:
            logger.error(f"Failed to submit task {task.id}: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_name": self.config['system']['name'],
            "version": self.config['system']['version'],
            "timestamp": datetime.now().isoformat(),
            "status": self.status.value,
            "plc": {
                "ip": self.config['plc']['ip'],
                "connected": self.opc_client.connected,
                "url": self.config['plc']['url']
            },
            "rack": self.position_manager.get_statistics(),
            "tasks": {
                "queue_size": self.task_queue.qsize(),
                "active": self.active_task.id if self.active_task else None,
                "completed": len(self.completed_tasks),
                "recent": [
                    {"id": task.id, "type": task.type, "status": task.status}
                    for task in self.completed_tasks[-5:]
                ]
            }
        }

    # Convenience methods for external use
    async def store_item(self, product_id: str, position_id: Optional[int] = None) -> bool:
        """Store item in rack"""
        task = ASRSTask(
            id=f"STORE_{datetime.now().strftime('%H%M%S')}",
            type="store",
            position_id=position_id,
            product_id=product_id
        )
        return await self.submit_task(task)

    async def retrieve_item(self, position_id: int) -> bool:
        """Retrieve item from position"""
        task = ASRSTask(
            id=f"RETRIEVE_{position_id}_{datetime.now().strftime('%H%M%S')}",
            type="retrieve",
            position_id=position_id
        )
        return await self.submit_task(task)

    async def update_display(self) -> bool:
        """Update all LED displays"""
        task = ASRSTask(
            id=f"UPDATE_{datetime.now().strftime('%H%M%S')}",
            type="update_display"
        )
        return await self.submit_task(task)

print("✅ AS/RS Controller created")
