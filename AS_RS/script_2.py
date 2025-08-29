# 3. Create controller using proven asyncua pattern

controller_proven_code = '''"""
BVM AS/RS Controller - Using Proven Asyncua Pattern
Based on user's working connection and monitoring code
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from asrs_core import *

logger = logging.getLogger(__name__)

class ASRSController:
    """AS/RS controller using proven asyncua pattern"""
    
    def __init__(self, config_path: str = "asrs_config.json"):
        self.config = self._load_config(config_path)
        self.opc_client = ProvenAsyncOPCClient(self.config)
        self.position_manager = PositionManager(self.config)
        
        # System state
        self.status = SystemStatus.DISCONNECTED
        self.running = False
        self.initialized = False
        
        # Task management with asyncio
        self.task_queue = asyncio.Queue()
        self.completed_tasks = []
        self.failed_tasks = []
        self.active_task = None
        
        # Background tasks
        self.monitoring_task = None
        self.task_processor_task = None
        self.variable_monitor_task = None
        
        # System stats
        self.system_stats = {
            "start_time": None,
            "operations_completed": 0,
            "errors_encountered": 0,
            "uptime_seconds": 0
        }
        
        # Button state tracking for proven pattern
        self.last_button_states = {}
        self.last_button_time = {}
        self.button_press_handlers = []
        
        # Emergency handling
        self.emergency_callbacks = []
        self.last_emergency_state = False
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_sections = ['system', 'plc', 'rack', 'operation']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing config section: {section}")
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    async def initialize(self) -> bool:
        """Initialize using proven asyncua pattern"""
        try:
            logger.info("🔧 Initializing BVM AS/RS system (proven asyncua)...")
            self.status = SystemStatus.CONNECTING
            
            # Connect using proven pattern
            connection_success = await self.opc_client.connect()
            if not connection_success:
                logger.error("❌ Failed to connect to PLC")
                self.status = SystemStatus.ERROR
                return False
            
            # Verify system readiness
            await self._verify_system_readiness()
            
            self.status = SystemStatus.CONNECTED
            self.initialized = True
            self.system_stats["start_time"] = datetime.now()
            
            logger.info("✅ AS/RS system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.status = SystemStatus.ERROR
            return False
    
    async def _verify_system_readiness(self):
        """Verify system components using proven pattern"""
        logger.info("Verifying system readiness...")
        
        # Test LED access (first 3)
        led_test_count = 0
        for i in range(1, 4):
            state = await self.opc_client.read_led_state(i)
            if state is not None:
                led_test_count += 1
        
        # Test button access (first 3)
        button_test_count = 0
        for i in range(1, 4):
            state = await self.opc_client.read_button_state(i)
            if state is not None:
                button_test_count += 1
        
        # Test emergency kill
        kill_state = await self.opc_client.read_emergency_kill()
        
        logger.info(f"System readiness: {led_test_count} LEDs, {button_test_count} buttons accessible")
        
        if led_test_count == 0:
            logger.warning("⚠️ No LED nodes accessible")
        if button_test_count == 0:
            logger.warning("⚠️ No button nodes accessible")
        if kill_state is None:
            logger.warning("⚠️ Emergency kill not accessible")
    
    async def start(self):
        """Start the AS/RS system with proven asyncua tasks"""
        if self.running:
            logger.warning("System is already running")
            return
        
        if not self.initialized:
            logger.error("System not initialized")
            return
        
        logger.info("🚀 Starting AS/RS system...")
        self.running = True
        self.status = SystemStatus.MONITORING
        
        # Start background tasks using proven asyncio pattern
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.task_processor_task = asyncio.create_task(self._task_processing_loop())
        self.variable_monitor_task = asyncio.create_task(self._variable_monitoring_loop())
        
        # Initial LED sync
        await self._sync_all_leds()
        
        logger.info("✅ AS/RS system started successfully")
    
    async def stop(self):
        """Stop the AS/RS system gracefully"""
        if not self.running:
            return
        
        logger.info("⏹️ Stopping AS/RS system...")
        self.running = False
        
        # Cancel all background tasks
        tasks_to_cancel = [
            self.monitoring_task,
            self.task_processor_task,
            self.variable_monitor_task
        ]
        
        for task in tasks_to_cancel:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Emergency LED shutdown
        try:
            await self._emergency_led_shutdown()
        except:
            pass
        
        # Disconnect using proven pattern
        await self.opc_client.disconnect()
        
        self.status = SystemStatus.DISCONNECTED
        logger.info("✅ AS/RS system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop using proven pattern"""
        logger.info("Monitoring loop started")
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while self.running:
                try:
                    # Update system states
                    await self._update_system_states()
                    
                    # Check emergency stop
                    await self._check_emergency_stop()
                    
                    # Sync LEDs if enabled
                    if self.config['operation']['auto_led_update']:
                        await self._sync_leds()
                    
                    # Update statistics
                    self._update_statistics()
                    
                    consecutive_errors = 0
                    await asyncio.sleep(self.config['operation']['scan_interval'])
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Monitoring error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.critical("Too many monitoring errors - stopping")
                        self.status = SystemStatus.ERROR
                        break
                    
                    await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Fatal monitoring error: {e}")
            self.status = SystemStatus.ERROR
    
    async def _variable_monitoring_loop(self):
        """Variable monitoring using user's proven change detection pattern"""
        logger.info("Variable monitoring loop started")
        
        try:
            # Use proven variable monitoring pattern from user's code
            await self.opc_client.monitor_variable_changes(
                callback=self._handle_variable_change
            )
        except asyncio.CancelledError:
            logger.info("Variable monitoring cancelled")
        except Exception as e:
            logger.error(f"Variable monitoring error: {e}")
    
    async def _handle_variable_change(self, var_name: str, old_value: Any, new_value: Any):
        """Handle variable changes using proven pattern"""
        try:
            logger.debug(f"Variable changed: {var_name} {old_value} → {new_value}")
            
            # Handle button presses (proven pattern)
            if var_name.startswith('pb') and var_name[2:].isdigit():
                position_id = int(var_name[2:])
                
                # Detect button press (False → True transition)
                if not old_value and new_value:
                    await self._handle_button_press(position_id)
            
            # Handle emergency changes
            elif var_name.lower() in ['kill', 'emergency']:
                if not old_value and new_value:  # Emergency activated
                    logger.critical("🚨 EMERGENCY DETECTED via variable monitor!")
                    await self._handle_emergency_activation()
            
            # Update position states
            self._update_position_from_variable(var_name, new_value)
            
        except Exception as e:
            logger.error(f"Error handling variable change {var_name}: {e}")
    
    def _update_position_from_variable(self, var_name: str, value: Any):
        """Update position states from variable changes"""
        try:
            # Update LED states
            if var_name.startswith('led') and var_name[3:].isdigit():
                position_id = int(var_name[3:])
                position = self.position_manager.get_position(position_id)
                if position:
                    position.led_state = bool(value)
            
            # Update button states
            elif var_name.startswith('pb') and var_name[2:].isdigit():
                position_id = int(var_name[2:])
                position = self.position_manager.get_position(position_id)
                if position:
                    position.button_pressed = bool(value)
        
        except Exception as e:
            logger.debug(f"Error updating position from variable {var_name}: {e}")
    
    async def _update_system_states(self):
        """Update system states from PLC"""
        try:
            states = await self.opc_client.read_all_states()
            
            # Update position states
            for pos_id, position in self.position_manager.positions.items():
                if pos_id in states["leds"]:
                    actual_led_state = states["leds"][pos_id]
                    if actual_led_state is not None:
                        position.led_state = actual_led_state
                
                if pos_id in states["buttons"]:
                    button_state = states["buttons"][pos_id]
                    if button_state is not None:
                        position.button_pressed = button_state
                        
        except Exception as e:
            logger.debug(f"Error updating system states: {e}")
            self.system_stats["errors_encountered"] += 1
    
    async def _handle_button_press(self, position_id: int):
        """Handle button press with proven debouncing"""
        current_time = datetime.now().timestamp()
        debounce_time = self.config['operation']['button_debounce']
        
        # Check debounce
        last_press_time = self.last_button_time.get(position_id, 0)
        if current_time - last_press_time < debounce_time:
            return  # Too soon, ignore
        
        self.last_button_time[position_id] = current_time
        
        position = self.position_manager.get_position(position_id)
        if position:
            timestamp = datetime.now().strftime("%H:%M:%S")
            logger.info(f"🔘 [{timestamp}] Button {position_id} pressed")
            
            if position.status == PositionStatus.OCCUPIED:
                # Auto-retrieve
                task = ASRSTask(
                    id=f"AUTO_RETRIEVE_{position_id}_{datetime.now().strftime('%H%M%S')}",
                    type="retrieve",
                    position_id=position_id,
                    priority=1
                )
                
                success = await self.submit_task(task)
                if success:
                    logger.info(f"🔘 Auto-retrieval task created for position {position_id}")
            else:
                logger.info(f"🔘 Button {position_id} pressed - position empty")
            
            # Call registered handlers
            for handler in self.button_press_handlers:
                try:
                    await handler(position_id, position)
                except Exception as e:
                    logger.error(f"Button handler error: {e}")
    
    async def _check_emergency_stop(self):
        """Check emergency stop using proven pattern"""
        try:
            emergency_state = await self.opc_client.read_emergency_kill()
            
            if emergency_state is None:
                return
            
            # Check for emergency activation
            if emergency_state and not self.last_emergency_state:
                logger.critical("🚨 EMERGENCY STOP ACTIVATED!")
                await self._handle_emergency_activation()
            
            # Check for emergency deactivation
            elif not emergency_state and self.last_emergency_state:
                logger.info("✅ Emergency stop deactivated")
                await self._handle_emergency_deactivation()
            
            self.last_emergency_state = emergency_state
            
        except Exception as e:
            logger.error(f"Error checking emergency stop: {e}")
    
    async def _handle_emergency_activation(self):
        """Handle emergency activation"""
        self.status = SystemStatus.EMERGENCY
        
        # Turn off all LEDs immediately
        await self._emergency_led_shutdown()
        
        # Clear all pending tasks
        while not self.task_queue.empty():
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                task.status = "cancelled"
                task.result = "Emergency stop activated"
                task.completed_at = datetime.now()
                self.failed_tasks.append(task)
            except asyncio.TimeoutError:
                break
        
        # Cancel active task
        if self.active_task:
            self.active_task.status = "cancelled"
            self.active_task.result = "Emergency stop activated"
            self.active_task.completed_at = datetime.now()
            self.failed_tasks.append(self.active_task)
            self.active_task = None
        
        # Call emergency callbacks
        for callback in self.emergency_callbacks:
            try:
                await callback(True)
            except Exception as e:
                logger.error(f"Emergency callback error: {e}")
        
        # Stop the system
        await self.stop()
    
    async def _handle_emergency_deactivation(self):
        """Handle emergency deactivation"""
        if self.status == SystemStatus.EMERGENCY:
            self.status = SystemStatus.MONITORING
            
            for callback in self.emergency_callbacks:
                try:
                    await callback(False)
                except Exception as e:
                    logger.error(f"Emergency callback error: {e}")
    
    async def _emergency_led_shutdown(self):
        """Emergency LED shutdown using proven pattern"""
        logger.info("🚨 Emergency LED shutdown")
        
        # Turn off all LEDs using proven write pattern
        tasks = []
        for pos_id in range(1, self.config['rack']['positions'] + 1):
            tasks.append(self.opc_client.write_led_state(pos_id, False))
            if len(tasks) >= 5:  # Process in batches
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks.clear()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _sync_leds(self):
        """Sync LED states with proven pattern"""
        try:
            sync_tasks = []
            
            for pos_id, position in self.position_manager.positions.items():
                expected_state = position.status == PositionStatus.OCCUPIED
                
                if position.led_state != expected_state:
                    sync_tasks.append(self._sync_single_led(pos_id, expected_state))
                    
                    if len(sync_tasks) >= 5:  # Process in batches
                        await asyncio.gather(*sync_tasks, return_exceptions=True)
                        sync_tasks.clear()
            
            if sync_tasks:
                await asyncio.gather(*sync_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.debug(f"Error syncing LEDs: {e}")
    
    async def _sync_single_led(self, pos_id: int, expected_state: bool):
        """Sync single LED using proven pattern"""
        position = self.position_manager.get_position(pos_id)
        if position:
            success = await self.opc_client.write_led_state(pos_id, expected_state)
            if success:
                position.led_state = expected_state
    
    async def _sync_all_leds(self):
        """Force sync all LEDs using proven pattern"""
        logger.info("Synchronizing all LED states...")
        
        tasks = []
        for pos_id, position in self.position_manager.positions.items():
            expected_state = position.status == PositionStatus.OCCUPIED
            tasks.append(self.opc_client.write_led_state(pos_id, expected_state))
            
            if len(tasks) >= 10:  # Process in batches
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if not isinstance(result, Exception) and result:
                        batch_pos_id = pos_id - len(results) + i + 1
                        pos = self.position_manager.get_position(batch_pos_id)
                        if pos:
                            pos.led_state = expected_state
                tasks.clear()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("LED synchronization completed")
    
    def _update_statistics(self):
        """Update system statistics"""
        if self.system_stats["start_time"]:
            uptime = datetime.now() - self.system_stats["start_time"]
            self.system_stats["uptime_seconds"] = int(uptime.total_seconds())
    
    async def _task_processing_loop(self):
        """Task processing using proven asyncio pattern"""
        logger.info("Task processing loop started")
        
        try:
            while self.running:
                try:
                    # Wait for task
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    
                    if self.status == SystemStatus.EMERGENCY:
                        # Don't process during emergency
                        task.status = "cancelled"
                        task.result = "System in emergency state"
                        task.completed_at = datetime.now()
                        self.failed_tasks.append(task)
                        continue
                    
                    await self._execute_task(task)
                    
                except asyncio.TimeoutError:
                    continue  # No task available
                    
        except asyncio.CancelledError:
            logger.info("Task processing loop cancelled")
        except Exception as e:
            logger.error(f"Fatal task processing error: {e}")
    
    async def _execute_task(self, task: ASRSTask):
        """Execute task using proven pattern"""
        try:
            self.active_task = task
            task.started_at = datetime.now()
            task.status = "in_progress"
            
            logger.info(f"⚙️ Executing task {task.id}: {task.type}")
            
            # Execute based on task type
            success = False
            if task.type == "store":
                success = await self._execute_store_task(task)
            elif task.type == "retrieve":
                success = await self._execute_retrieve_task(task)
            elif task.type == "update_display":
                success = await self._execute_update_display_task(task)
            else:
                task.result = f"Unknown task type: {task.type}"
            
            # Complete the task
            task.completed_at = datetime.now()
            
            if success:
                task.status = "completed"
                self.completed_tasks.append(task)
                self.system_stats["operations_completed"] += 1
                logger.info(f"✅ Task {task.id} completed")
            else:
                task.status = "failed"
                self.failed_tasks.append(task)
                self.system_stats["errors_encountered"] += 1
                logger.warning(f"❌ Task {task.id} failed: {task.result}")
            
            # Trim task history
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-50:]
            if len(self.failed_tasks) > 50:
                self.failed_tasks = self.failed_tasks[-25:]
                
        except Exception as e:
            logger.error(f"Fatal error executing task {task.id}: {e}")
            task.status = "failed"
            task.result = f"Fatal execution error: {str(e)}"
            task.completed_at = datetime.now()
            self.failed_tasks.append(task)
            self.system_stats["errors_encountered"] += 1
            
        finally:
            self.active_task = None
    
    async def _execute_store_task(self, task: ASRSTask) -> bool:
        """Execute store operation using proven LED pattern"""
        try:
            # Determine target position
            if task.position_id:
                position = self.position_manager.get_position(task.position_id)
                if not position:
                    task.result = f"Invalid position ID: {task.position_id}"
                    return False
            else:
                position = self.position_manager.find_empty_position()
                if not position:
                    task.result = "No empty positions available"
                    return False
                task.position_id = position.id
            
            # Validate position
            if position.status != PositionStatus.EMPTY:
                task.result = f"Position {position.id} is not empty"
                return False
            
            # Store item
            success = self.position_manager.store_item(position.id, task.product_id)
            if not success:
                task.result = "Failed to store item"
                return False
            
            # Update LED using proven pattern
            led_success = await self.opc_client.write_led_state(position.id, True)
            if not led_success:
                logger.warning(f"Failed to turn on LED for position {position.id}")
            
            task.result = f"Successfully stored '{task.product_id}' in position {position.id}"
            return True
            
        except Exception as e:
            task.result = f"Store operation error: {str(e)}"
            return False
    
    async def _execute_retrieve_task(self, task: ASRSTask) -> bool:
        """Execute retrieve operation using proven pattern"""
        try:
            position = self.position_manager.get_position(task.position_id)
            if not position:
                task.result = f"Invalid position ID: {task.position_id}"
                return False
            
            if position.status != PositionStatus.OCCUPIED:
                task.result = f"Position {task.position_id} is empty"
                return False
            
            # Retrieve item
            product_id = self.position_manager.retrieve_item(task.position_id)
            if not product_id:
                task.result = "Failed to retrieve item"
                return False
            
            # Update LED using proven pattern
            led_success = await self.opc_client.write_led_state(task.position_id, False)
            if not led_success:
                logger.warning(f"Failed to turn off LED for position {task.position_id}")
            
            task.result = f"Successfully retrieved '{product_id}' from position {task.position_id}"
            return True
            
        except Exception as e:
            task.result = f"Retrieve operation error: {str(e)}"
            return False
    
    async def _execute_update_display_task(self, task: ASRSTask) -> bool:
        """Execute display update using proven pattern"""
        try:
            await self._sync_all_leds()
            task.result = "Successfully updated all LED displays"
            return True
            
        except Exception as e:
            task.result = f"Display update error: {str(e)}"
            return False
    
    async def submit_task(self, task: ASRSTask) -> bool:
        """Submit task using proven asyncio queue pattern"""
        try:
            await self.task_queue.put(task)
            logger.debug(f"Task {task.id} submitted")
            return True
        except Exception as e:
            logger.error(f"Failed to submit task {task.id}: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        opc_stats = self.opc_client.get_statistics()
        pos_stats = self.position_manager.get_statistics()
        
        return {
            "system_name": self.config['system']['name'],
            "version": self.config['system']['version'],
            "timestamp": datetime.now().isoformat(),
            "status": self.status.value,
            "uptime_seconds": self.system_stats["uptime_seconds"],
            "plc": {
                "ip": self.config['plc']['ip'],
                "url": self.config['plc']['url'],
                "connected": opc_stats["connected"],
                "reads": opc_stats["reads"],  
                "writes": opc_stats["writes"],
                "errors": opc_stats["errors"],
                "total_variables": opc_stats["total_variables"]
            },
            "rack": pos_stats,
            "tasks": {
                "queue_size": self.task_queue.qsize(),
                "active": self.active_task.id if self.active_task else None,
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "operations_total": self.system_stats["operations_completed"],
                "recent_completed": [
                    {"id": task.id, "type": task.type, "status": task.status, "result": task.result}
                    for task in self.completed_tasks[-5:]
                ],
                "recent_failed": [
                    {"id": task.id, "type": task.type, "status": task.status, "result": task.result}
                    for task in self.failed_tasks[-3:]
                ]
            },
            "emergency": {
                "active": self.last_emergency_state,
                "status": "ACTIVE" if self.last_emergency_state else "NORMAL"
            }
        }
    
    # Convenience methods
    async def store_item(self, product_id: str, position_id: Optional[int] = None) -> bool:
        """Store item with auto-generated task ID"""
        task = ASRSTask(
            id=f"STORE_{datetime.now().strftime('%H%M%S%f')[:-3]}",
            type="store",
            position_id=position_id,
            product_id=product_id
        )
        return await self.submit_task(task)
    
    async def retrieve_item(self, position_id: int) -> bool:
        """Retrieve item with auto-generated task ID"""
        task = ASRSTask(
            id=f"RETRIEVE_{position_id}_{datetime.now().strftime('%H%M%S%f')[:-3]}",
            type="retrieve",
            position_id=position_id
        )
        return await self.submit_task(task)
    
    async def update_display(self) -> bool:
        """Update all LED displays"""
        task = ASRSTask(
            id=f"UPDATE_{datetime.now().strftime('%H%M%S%f')[:-3]}",
            type="update_display"
        )
        return await self.submit_task(task)
    
    def add_button_press_handler(self, handler: Callable):
        """Add custom button press handler"""
        self.button_press_handlers.append(handler)
    
    def add_emergency_callback(self, callback: Callable):
        """Add emergency state change callback"""
        self.emergency_callbacks.append(callback)

print("✅ Controller (proven asyncua): asrs_controller.py")
'''

with open('asrs_controller.py', 'w') as f:
    f.write(controller_proven_code)

print("✅ 3. Controller (proven asyncua): asrs_controller.py")