
"""
OMRON AS/RS Main Controller
Coordinates 35-position storage operations, LED control, and push button monitoring
"""

from omron_asrs_core import *
from concurrent.futures import ThreadPoolExecutor

class OmronASRSController:
    """Main controller for OMRON Auto Rack35 AS/RS system"""

    def __init__(self, config_path: str = 'omron_asrs_config.json'):
        self.config = self._load_config(config_path)
        self.opc_client = OmronOPCClient(self.config['communication'])
        self.position_manager = PositionManager(self.config, self.opc_client)

        self.status = ASRSStatus.IDLE
        self.task_queue = queue.Queue()
        self.active_task: Optional[ASRSTask] = None
        self.completed_tasks: List[ASRSTask] = []

        self._running = False
        self._monitoring_thread = None
        self._task_processor_thread = None
        self._executor = ThreadPoolExecutor(max_workers=3)

        logger.info(f"🏭 OMRON AS/RS Controller initialized: {self.config['system']['name']}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file: {e}")
            raise

    def initialize(self) -> bool:
        """Initialize the AS/RS system"""
        try:
            logger.info("🔧 Initializing OMRON AS/RS system...")

            # Connect to OPC UA server
            if not self.opc_client.connect():
                logger.error("❌ Failed to connect to OMRON PLC")
                return False

            # Test emergency kill switch access
            kill_status = self.opc_client.read_value(self.config['control_nodes']['emergency_kill'])
            if kill_status is None:
                logger.warning("⚠️ Could not read emergency kill switch")
            else:
                logger.info(f"🚨 Emergency kill status: {'ACTIVE' if kill_status else 'NORMAL'}")

            # Initialize all LEDs to match current occupancy
            self.position_manager.update_all_leds()

            logger.info("✅ OMRON AS/RS system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing OMRON AS/RS system: {e}")
            return False

    def start(self):
        """Start the AS/RS system operations"""
        if self._running:
            logger.warning("⚠️ AS/RS system is already running")
            return

        logger.info("🚀 Starting OMRON AS/RS system...")
        self._running = True

        # Start monitoring thread for push buttons and emergency stop
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()

        # Start task processor thread
        self._task_processor_thread = threading.Thread(target=self._task_processing_loop, daemon=True)
        self._task_processor_thread.start()

        self.status = ASRSStatus.MONITORING
        logger.info("✅ OMRON AS/RS system started successfully")

    def stop(self):
        """Stop the AS/RS system"""
        logger.info("⏹️ Stopping OMRON AS/RS system...")
        self._running = False

        # Wait for threads to finish
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=3)
        if self._task_processor_thread:
            self._task_processor_thread.join(timeout=3)

        # Disconnect OPC UA
        self.opc_client.disconnect()

        # Shutdown executor
        self._executor.shutdown(wait=True)

        self.status = ASRSStatus.IDLE
        logger.info("✅ OMRON AS/RS system stopped")

    def _monitoring_loop(self):
        """Background monitoring loop for push buttons and emergency stop"""
        logger.info("🔄 Monitoring loop started")

        while self._running:
            try:
                # Check emergency kill switch
                kill_status = self.opc_client.read_value(self.config['control_nodes']['emergency_kill'])
                if kill_status:
                    logger.error("🚨 EMERGENCY KILL ACTIVATED!")
                    self.status = ASRSStatus.EMERGENCY_STOP
                    self._handle_emergency_stop()
                    break

                # Check push button presses
                pressed_buttons = self.position_manager.monitor_pushbuttons()
                if pressed_buttons:
                    for pos_id in pressed_buttons:
                        self._handle_pushbutton_press(pos_id)

                time.sleep(0.5)  # Check every 500ms

            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(1)

        logger.info("⏹️ Monitoring loop stopped")

    def _task_processing_loop(self):
        """Main task processing loop"""
        logger.info("🔄 Task processing loop started")

        while self._running:
            try:
                # Get task from queue with timeout
                try:
                    task = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue

                # Process task
                self._execute_task(task)

            except Exception as e:
                logger.error(f"❌ Error in task processing loop: {e}")
                time.sleep(1)

        logger.info("⏹️ Task processing loop stopped")

    def _handle_emergency_stop(self):
        """Handle emergency stop condition"""
        # Turn off all LEDs as safety measure
        for position in self.position_manager.positions.values():
            self.opc_client.write_value(position.led_node, False)

        # Cancel any pending tasks
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                task.status = "cancelled"
                task.result = "Emergency stop activated"
                self.completed_tasks.append(task)
            except queue.Empty:
                break

        logger.info("🚨 Emergency stop procedures completed")

    def _handle_pushbutton_press(self, position_id: int):
        """Handle push button press event"""
        position = self.position_manager.get_position(position_id)
        if position:
            if position.occupied:
                logger.info(f"🔘 Button pressed: Position {position_id} - Retrieving {position.product_id}")
                # Auto-retrieve item when button is pressed on occupied position
                task = ASRSTask(
                    task_id=f"AUTO-RETRIEVE-{position_id}",
                    task_type=TaskType.RETRIEVE_ITEM,
                    position=position
                )
                self.submit_task(task)
            else:
                logger.info(f"🔘 Button pressed: Position {position_id} - Empty position")

    def submit_task(self, task: ASRSTask) -> bool:
        """Submit a task to the AS/RS system"""
        try:
            self.task_queue.put(task)
            logger.info(f"📋 Task {task.task_id} submitted: {task.task_type.value}")
            return True
        except Exception as e:
            logger.error(f"❌ Error submitting task: {e}")
            return False

    def _execute_task(self, task: ASRSTask):
        """Execute a specific task"""
        try:
            self.active_task = task
            task.started_at = datetime.now()
            task.status = "in_progress"

            logger.info(f"🔄 Executing task {task.task_id}: {task.task_type.value}")

            if task.task_type == TaskType.STORE_ITEM:
                success = self._execute_store_task(task)

            elif task.task_type == TaskType.RETRIEVE_ITEM:
                success = self._execute_retrieve_task(task)

            elif task.task_type == TaskType.UPDATE_DISPLAY:
                success = self._execute_display_update(task)

            else:
                logger.error(f"❌ Unknown task type: {task.task_type}")
                success = False

            # Update task completion
            task.completed_at = datetime.now()
            task.status = "completed" if success else "failed"
            self.completed_tasks.append(task)
            self.active_task = None

            if success:
                logger.info(f"✅ Task {task.task_id} completed successfully")
            else:
                logger.error(f"❌ Task {task.task_id} failed")

        except Exception as e:
            logger.error(f"❌ Error executing task {task.task_id}: {e}")
            task.status = "failed"
            task.completed_at = datetime.now()
            task.result = str(e)
            self.active_task = None

    def _execute_store_task(self, task: ASRSTask) -> bool:
        """Execute a storage operation"""
        try:
            self.status = ASRSStatus.STORING

            # Find empty position if not specified
            if not task.position:
                task.position = self.position_manager.find_empty_position()
                if not task.position:
                    task.result = "No empty positions available"
                    return False

            # Check if position is actually empty
            if task.position.occupied:
                task.result = f"Position {task.position.id} is already occupied"
                return False

            # Store the item
            if self.position_manager.store_item(task.position.id, task.product_id):
                task.result = f"Stored {task.product_id} in position {task.position.id}"
                self.status = ASRSStatus.MONITORING
                return True
            else:
                task.result = "Failed to store item"
                return False

        except Exception as e:
            logger.error(f"❌ Error in store task: {e}")
            task.result = str(e)
            return False
        finally:
            self.status = ASRSStatus.MONITORING

    def _execute_retrieve_task(self, task: ASRSTask) -> bool:
        """Execute a retrieval operation"""
        try:
            self.status = ASRSStatus.RETRIEVING

            if not task.position:
                task.result = "No position specified for retrieval"
                return False

            # Check if position is actually occupied
            if not task.position.occupied:
                task.result = f"Position {task.position.id} is empty"
                return False

            # Retrieve the item
            retrieved_product = self.position_manager.retrieve_item(task.position.id)
            if retrieved_product:
                task.result = f"Retrieved {retrieved_product} from position {task.position.id}"
                self.status = ASRSStatus.MONITORING
                return True
            else:
                task.result = "Failed to retrieve item"
                return False

        except Exception as e:
            logger.error(f"❌ Error in retrieve task: {e}")
            task.result = str(e)
            return False
        finally:
            self.status = ASRSStatus.MONITORING

    def _execute_display_update(self, task: ASRSTask) -> bool:
        """Execute a display update operation"""
        try:
            # Update all LED states to match current occupancy
            self.position_manager.update_all_leds()
            task.result = "Display updated successfully"
            return True
        except Exception as e:
            logger.error(f"❌ Error updating display: {e}")
            task.result = str(e)
            return False

    def store_item_at_position(self, position_id: int, product_id: str) -> bool:
        """Store item at specific position"""
        position = self.position_manager.get_position(position_id)
        if not position:
            logger.error(f"❌ Invalid position ID: {position_id}")
            return False

        task = ASRSTask(
            task_id=f"STORE-P{position_id:02d}-{datetime.now().strftime('%H%M%S')}",
            task_type=TaskType.STORE_ITEM,
            position=position,
            product_id=product_id
        )

        return self.submit_task(task)

    def store_item_auto_position(self, product_id: str) -> bool:
        """Store item in first available position"""
        empty_position = self.position_manager.find_empty_position()
        if not empty_position:
            logger.error("❌ No empty positions available")
            return False

        return self.store_item_at_position(empty_position.id, product_id)

    def retrieve_item_from_position(self, position_id: int) -> bool:
        """Retrieve item from specific position"""
        position = self.position_manager.get_position(position_id)
        if not position:
            logger.error(f"❌ Invalid position ID: {position_id}")
            return False

        if not position.occupied:
            logger.error(f"❌ Position {position_id} is empty")
            return False

        task = ASRSTask(
            task_id=f"RETRIEVE-P{position_id:02d}-{datetime.now().strftime('%H%M%S')}",
            task_type=TaskType.RETRIEVE_ITEM,
            position=position
        )

        return self.submit_task(task)

    def retrieve_item_by_product(self, product_id: str) -> bool:
        """Retrieve item by product ID"""
        position = self.position_manager.find_product(product_id)
        if not position:
            logger.error(f"❌ Product {product_id} not found")
            return False

        return self.retrieve_item_from_position(position.id)

    def update_display(self) -> bool:
        """Update all LED displays"""
        task = ASRSTask(
            task_id=f"UPDATE-DISPLAY-{datetime.now().strftime('%H%M%S')}",
            task_type=TaskType.UPDATE_DISPLAY
        )

        return self.submit_task(task)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        occupancy_stats = self.position_manager.get_occupancy_stats()

        # Get recent activity
        recent_tasks = self.completed_tasks[-10:] if self.completed_tasks else []

        return {
            "system_name": self.config['system']['name'],
            "plc_model": self.config['system']['plc_model'],
            "timestamp": datetime.now().isoformat(),
            "status": self.status.value,
            "communication": {
                "protocol": self.config['communication']['protocol'],
                "endpoint": self.config['communication']['endpoint'],
                "connected": self.opc_client.connected
            },
            "storage": occupancy_stats,
            "tasks": {
                "pending": self.task_queue.qsize(),
                "active": self.active_task.task_id if self.active_task else None,
                "completed": len(self.completed_tasks),
                "recent": [{"id": t.task_id, "type": t.task_type.value, "status": t.status} for t in recent_tasks]
            },
            "safety": {
                "emergency_stop": self.opc_client.read_value(self.config['control_nodes']['emergency_kill']) or False
            }
        }

    def get_position_grid(self) -> List[List[str]]:
        """Get visual grid representation"""
        return self.position_manager.get_grid_display()

    def get_position_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all positions"""
        details = []
        for position in self.position_manager.positions.values():
            details.append({
                "id": position.id,
                "name": position.position_id,
                "grid_location": position.grid_location,
                "status": position.status.value,
                "occupied": position.occupied,
                "product_id": position.product_id,
                "stored_at": position.stored_at.isoformat() if position.stored_at else None,
                "led_node": position.led_node,
                "pushbutton_node": position.pushbutton_node
            })
        return details

print("✅ OMRON AS/RS Controller created")
print("   - 35-position storage management")  
print("   - OPC UA LED and push button control")
print("   - Real-time monitoring and task processing")
print("   - Emergency stop handling")
print("   - Visual grid display")
