"""
BVM AS/RS Interactive Application - Using Proven Asyncua Pattern
Based on user's working asyncua connection and monitoring code
"""

import asyncio
import sys
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from asrs_controller import ASRSController, ASRSTask

# Configure application logging
logging.getLogger('asyncua').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class ASRSApplication:
    """Interactive AS/RS application using proven asyncua pattern"""

    def __init__(self, config_path: str = "asrs_config.json"):
        self.controller = ASRSController(config_path)
        self.running = False
        self.last_grid_update = 0
        self.command_history = []
        self.display_settings = {
            "auto_refresh": True,
            "show_help": True,
            "compact_mode": False
        }

        # Performance tracking
        self.session_start = datetime.now()
        self.commands_executed = 0

    async def initialize(self) -> bool:
        """Initialize using proven asyncua pattern"""
        print("\n🔧 Initializing BVM AS/RS Application (Proven Asyncua)...")
        print("   Using your proven connection pattern...")

        try:
            success = await self.controller.initialize()
            if success:
                print("✅ BVM AS/RS Application initialized successfully")
                print(f"   Connected to PLC at {self.controller.config['plc']['ip']}")
                return True
            else:
                print("❌ Failed to initialize AS/RS controller")
                print("   Check PLC connection and configuration")
                return False

        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False

    async def start(self):
        """Start using proven pattern"""
        if not self.running:
            await self.controller.start()
            self.running = True
            print("🚀 BVM AS/RS Application started")

    async def stop(self):
        """Stop using proven pattern"""
        if self.running:
            self.running = False
            await self.controller.stop()
            print("⏹️ BVM AS/RS Application stopped")

    def display_header(self):
        """Display enhanced application header"""
        config = self.controller.config
        status = self.controller.get_system_status()

        print("\n" + "="*80)
        print("   🏗️ BVM AUTO RACK35 AS/RS CONTROL SYSTEM")
        print("   " + "=" * 50)
        print(f"   PLC: {config['system']['plc_model']} at {config['plc']['ip']}")
        print(f"   Status: {status['status'].upper()}")
        print(f"   Positions: {config['rack']['positions']} ({config['rack']['layout']['rows']}×{config['rack']['layout']['columns']} grid)")
        print(f"   Version: {config['system']['version']} (Proven Asyncua)")

        # Show connection quality
        if status['plc']['connected']:
            print(f"   Connection: ✅ CONNECTED (Variables:{status['plc']['total_variables']} R:{status['plc']['reads']} W:{status['plc']['writes']})")
        else:
            print(f"   Connection: ❌ DISCONNECTED")

        print("="*80)

    def show_commands(self):
        """Display available commands"""
        print("\n📖 AVAILABLE COMMANDS:")
        print("   [G] → Show Grid Display        [S] → Store Item")
        print("   [R] → Retrieve Item            [P] → Position Details")  
        print("   [T] → System Status            [L] → List Stored Items")
        print("   [U] → Update LED Display       [M] → Monitor Buttons")
        print("   [E] → Emergency Status         [I] → System Info")
        print("   [C] → Clear Screen             [H] → Help")
        print("   [Q] → Quit System")

        if self.display_settings["show_help"]:
            print("\n💡 Tips:")
            print("   • Using your proven asyncua connection pattern")
            print("   • Real-time variable monitoring active")
            print("   • Emergency stop monitoring enabled")

        print("-" * 65)

    def display_grid(self, force_update: bool = False):
        """Display rack grid layout"""
        if not force_update and time.time() - self.last_grid_update < 5:
            return

        grid = self.controller.position_manager.get_grid_display()
        stats = self.controller.position_manager.get_statistics()

        print("\n" + "="*65)
        print("   📦 STORAGE RACK LAYOUT - LIVE STATUS")
        print("="*65)
        print(f"Occupancy: {stats['occupied_positions']}/{stats['total_positions']} ({stats['occupancy_percent']}%)")
        print("Legend: [##] = Occupied,  ##  = Empty")

        if stats['unique_products'] > 0:
            print(f"Products: {stats['unique_products']} unique items stored")

        print()

        # Display column headers
        print("    ", end="")
        cols = int(stats['layout'].split('×')[1])
        for col in range(1, cols + 1):
            print(f"  C{col}  ", end="")
        print()

        # Display grid with row headers
        for i, row in enumerate(grid):
            print(f" R{i+1} ", end="")
            for cell in row:
                print(f" {cell} ", end="")
            print()

        print("="*65)

        # Show recent activity
        recent_activity = stats.get('recent_activity', [])
        if recent_activity:
            print("\n🔄 Recent Activity:")
            for activity in recent_activity[:3]:
                timestamp = datetime.fromisoformat(activity['timestamp']).strftime("%H:%M:%S")
                print(f"   [{timestamp}] {activity['type']} - Position {activity['position_id']} - {activity['product_id']}")

        self.last_grid_update = time.time()

    async def store_item_interface(self):
        """Interactive store item interface using proven pattern"""
        print("\n📦 STORE ITEM IN RACK")
        print("-" * 25)

        try:
            # Get product ID
            while True:
                product_id = input("Product ID (or 'back' to return): ").strip()
                if product_id.lower() == 'back':
                    return
                if product_id:
                    break
                print("❌ Product ID cannot be empty")

            # Check if product exists
            existing_positions = self.controller.position_manager.find_product_positions(product_id)
            if existing_positions:
                print(f"\n⚠️ Product {product_id} already stored in {len(existing_positions)} position(s):")
                for pos in existing_positions:
                    print(f"   Position {pos.id} ({pos.grid_location})")

                confirm = input("Store another copy? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("❌ Storage cancelled")
                    return

            # Storage options
            empty_position = self.controller.position_manager.find_empty_position()
            if not empty_position:
                print("❌ No empty positions available!")
                return

            print(f"\nStorage options:")
            print("1. Auto-assign to first empty position")
            print("2. Specify position (1-35)")

            choice = input("Select option (1 or 2): ").strip()

            if choice == "1":
                print(f"\n⏱️ Storing {product_id} in position {empty_position.id}...")
                success = await self.controller.store_item(product_id)

                if success:
                    print(f"✅ Storage task submitted for {product_id}")
                    await self._wait_for_task_completion("storing", product_id)
                else:
                    print("❌ Failed to submit storage task")

            elif choice == "2":
                try:
                    position_id = int(input("Position (1-35): "))

                    if not (1 <= position_id <= 35):
                        print("❌ Position must be between 1 and 35")
                        return

                    position = self.controller.position_manager.get_position(position_id)
                    if not position or not position.is_available:
                        print(f"❌ Position {position_id} is not available")
                        return

                    print(f"\n⏱️ Storing {product_id} in position {position_id}...")
                    success = await self.controller.store_item(product_id, position_id)

                    if success:
                        print(f"✅ Storage task submitted: {product_id} → Position {position_id}")
                        await self._wait_for_task_completion("storing", product_id)
                    else:
                        print("❌ Failed to submit storage task")

                except ValueError:
                    print("❌ Invalid position number")
            else:
                print("❌ Invalid option")

        except KeyboardInterrupt:
            print("\n❌ Storage cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    async def retrieve_item_interface(self):
        """Interactive retrieve item interface using proven pattern"""
        print("\n📤 RETRIEVE ITEM FROM RACK")
        print("-" * 27)

        try:
            # Show occupied positions
            occupied = [p for p in self.controller.position_manager.positions.values() 
                       if p.status.value == "occupied"]

            if not occupied:
                print("📭 No items currently stored in the rack")
                return

            print(f"📦 {len(occupied)} items currently stored")

            print("\nRetrieval options:")
            print("1. By Position (1-35)")
            print("2. By Product ID")
            print("3. Show all stored items first")

            choice = input("Select option (1, 2, or 3): ").strip()

            if choice == "3":
                self.show_stored_items_summary()
                choice = input("\nNow select retrieval method (1 or 2): ").strip()

            if choice == "1":
                await self._retrieve_by_position()
            elif choice == "2":
                await self._retrieve_by_product_id()
            else:
                print("❌ Invalid option")

        except KeyboardInterrupt:
            print("\n❌ Retrieval cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    async def _retrieve_by_position(self):
        """Retrieve item by position using proven pattern"""
        try:
            position_id = int(input("Position (1-35): "))

            if not (1 <= position_id <= 35):
                print("❌ Position must be between 1 and 35")
                return

            position = self.controller.position_manager.get_position(position_id)
            if not position or position.status.value == "empty":
                print(f"❌ Position {position_id} is empty")
                return

            # Show item details
            print(f"\n📦 Position {position_id} ({position.grid_location}) contains:")
            print(f"   Product ID: {position.product_id}")
            if position.stored_at:
                duration = datetime.now() - position.stored_at
                print(f"   Stored: {position.stored_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Duration: {self._format_duration(duration)}")

            confirm = input("\nRetrieve this item? (y/N): ").strip().lower()

            if confirm == 'y':
                print(f"\n⏱️ Retrieving item from position {position_id}...")
                success = await self.controller.retrieve_item(position_id)

                if success:
                    print(f"✅ Retrieval task submitted for position {position_id}")
                    await self._wait_for_task_completion("retrieving", position.product_id)
                else:
                    print("❌ Failed to submit retrieval task")
            else:
                print("❌ Retrieval cancelled")

        except ValueError:
            print("❌ Invalid position number")

    async def _retrieve_by_product_id(self):
        """Retrieve item by product ID using proven pattern"""
        # Show available products
        products = {}
        for position in self.controller.position_manager.positions.values():
            if position.product_id and position.status.value == "occupied":
                if position.product_id not in products:
                    products[position.product_id] = []
                products[position.product_id].append(position)

        if not products:
            print("❌ No products found")
            return

        print(f"\nAvailable products ({len(products)} unique):")
        for i, (product_id, positions) in enumerate(sorted(products.items()), 1):
            print(f"   {i}. {product_id} ({len(positions)} {'copy' if len(positions) == 1 else 'copies'})")

        try:
            product_input = input("\nProduct ID (or number): ").strip()

            # Check if input is a number
            if product_input.isdigit():
                selection = int(product_input)
                if 1 <= selection <= len(products):
                    product_id = list(products.keys())[selection - 1]
                else:
                    print("❌ Invalid selection")
                    return
            else:
                product_id = product_input

            if product_id not in products:
                print(f"❌ Product '{product_id}' not found")
                return

            positions_with_product = products[product_id]

            if len(positions_with_product) == 1:
                position = positions_with_product[0]
            else:
                # Multiple copies
                print(f"\nFound {len(positions_with_product)} copies of {product_id}:")
                for i, pos in enumerate(positions_with_product, 1):
                    duration_str = ""
                    if pos.stored_at:
                        duration = datetime.now() - pos.stored_at
                        duration_str = f" ({self._format_duration(duration)} old)"
                    print(f"   {i}. Position {pos.id} ({pos.grid_location}){duration_str}")

                choice = input("Select position (1-{}): ".format(len(positions_with_product)))
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(positions_with_product):
                        position = positions_with_product[choice_idx]
                    else:
                        print("❌ Invalid selection")
                        return
                except ValueError:
                    print("❌ Invalid selection")
                    return

            # Confirm retrieval
            print(f"\n📍 Selected: {product_id} from position {position.id}")
            confirm = input("Retrieve this item? (y/N): ").strip().lower()

            if confirm == 'y':
                print(f"\n⏱️ Retrieving {product_id}...")
                success = await self.controller.retrieve_item(position.id)

                if success:
                    print(f"✅ Retrieval task submitted for {product_id}")
                    await self._wait_for_task_completion("retrieving", product_id)
                else:
                    print("❌ Failed to submit retrieval task")
            else:
                print("❌ Retrieval cancelled")

        except ValueError:
            print("❌ Invalid input")

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable way"""
        total_seconds = int(duration.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes}m"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    async def _wait_for_task_completion(self, operation: str, item_name: str = "item"):
        """Wait for task completion using proven asyncio pattern"""
        start_time = time.time()
        max_wait = self.controller.config['operation']['command_timeout']

        dots = ""
        while time.time() - start_time < max_wait:
            if not self.controller.active_task:
                break

            # Animated progress dots
            dots = "." * ((int(time.time() - start_time) % 4) + 1)
            elapsed = time.time() - start_time
            print(f"\r⏱️ {operation.title()} {item_name}{dots:<4} ({elapsed:.1f}s)", end='', flush=True)
            await asyncio.sleep(0.5)

        print()  # New line

        # Check if task completed
        if self.controller.completed_tasks:
            last_task = self.controller.completed_tasks[-1]
            if last_task.result:
                print(f"   {last_task.result}")

        print("✅ Operation completed")
        self.display_grid(force_update=True)

    def show_position_details(self):
        """Show position details"""
        print("\n📍 POSITION DETAILS")
        print("-" * 20)

        try:
            position_input = input("Position (1-35), 'all', or 'occupied': ").strip().lower()

            if position_input in ['all', 'occupied']:
                self._show_multiple_positions(position_input)
            else:
                try:
                    position_id = int(position_input)
                    if 1 <= position_id <= 35:
                        self._show_single_position(position_id)
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")

        except Exception as e:
            print(f"❌ Error: {e}")

    def _show_single_position(self, position_id: int):
        """Show details for single position"""
        position = self.controller.position_manager.get_position(position_id)

        if not position:
            print(f"❌ Position {position_id} not found")
            return

        print(f"\n📍 POSITION {position_id} DETAILS:")
        print(f"   Name: {position.position_name}")
        print(f"   Grid Location: {position.grid_location}")
        print(f"   Status: {position.status.value.upper()}")
        print(f"   LED State: {'🟢 ON' if position.led_state else '🔴 OFF'}")
        print(f"   Button Pressed: {'🔘 YES' if position.button_pressed else '⚪ NO'}")

        if position.status.value == "occupied" and position.product_id:
            print(f"   Product ID: {position.product_id}")
            if position.stored_at:
                print(f"   Stored At: {position.stored_at.strftime('%Y-%m-%d %H:%M:%S')}")
                duration = datetime.now() - position.stored_at
                print(f"   Duration: {self._format_duration(duration)}")

        if position.last_activity:
            print(f"   Last Activity: {position.last_activity.strftime('%Y-%m-%d %H:%M:%S')}")

    def _show_multiple_positions(self, filter_type: str):
        """Show multiple positions"""
        positions = list(self.controller.position_manager.positions.values())

        if filter_type == 'occupied':
            positions = [p for p in positions if p.status.value == "occupied"]
            title = "OCCUPIED POSITIONS"
        else:
            title = "ALL POSITIONS"

        if not positions:
            print(f"\n📭 No {filter_type} positions found")
            return

        print(f"\n📋 {title} ({len(positions)}):")
        print(f"{'Pos':<4} {'Grid':<6} {'Status':<10} {'LED':<4} {'BTN':<4} {'Product ID':<15} {'Duration'}")
        print("-" * 75)

        for position in sorted(positions, key=lambda p: p.id):
            led_icon = "🟢" if position.led_state else "🔴"
            btn_icon = "🔘" if position.button_pressed else "⚪"
            duration_str = ""

            if position.stored_at:
                duration = datetime.now() - position.stored_at
                duration_str = self._format_duration(duration)

            product_display = (position.product_id or "")[:15]

            print(f"{position.id:<4} {position.grid_location:<6} {position.status.value:<10} "
                  f"{led_icon:<4} {btn_icon:<4} {product_display:<15} {duration_str}")

    def display_system_status(self):
        """Display system status using proven pattern"""
        status = self.controller.get_system_status()

        print("\n" + "="*75)
        print(f"   📊 SYSTEM STATUS - {status['system_name']}")
        print("="*75)

        # System info
        uptime_str = self._format_duration(timedelta(seconds=status['uptime_seconds']))
        print(f"Version: {status['version']} (Proven Asyncua Pattern)")
        print(f"Status: {status['status'].upper()}")
        print(f"Uptime: {uptime_str}")
        print(f"Timestamp: {datetime.fromisoformat(status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

        # PLC connection with proven pattern info
        print(f"\n🔌 PLC CONNECTION (Proven Pattern):")
        plc = status['plc']
        connection_quality = "Excellent" if plc['errors'] < 5 else "Good" if plc['errors'] < 20 else "Poor"
        print(f"   Address: {plc['ip']} ({plc['url']})")
        print(f"   Status: {'🟢 CONNECTED' if plc['connected'] else '🔴 DISCONNECTED'}")
        print(f"   Variables: {plc['total_variables']} discovered")
        print(f"   Operations: {plc['reads']} reads, {plc['writes']} writes")
        print(f"   Errors: {plc['errors']} (Quality: {connection_quality})")

        # Storage rack
        print(f"\n📦 STORAGE RACK:")
        rack = status['rack']
        print(f"   Layout: {rack['layout']} ({rack['total_positions']} total positions)")
        print(f"   Occupancy: {rack['occupied_positions']}/{rack['total_positions']} ({rack['occupancy_percent']}%)")
        print(f"   Available: {rack['empty_positions']} positions")
        if rack.get('unique_products'):
            print(f"   Products: {rack['unique_products']} unique items")

        # Task management
        print(f"\n📋 TASK MANAGEMENT:")
        tasks = status['tasks']
        print(f"   Queue: {tasks['queue_size']} pending")
        print(f"   Active: {tasks['active'] or 'None'}")
        print(f"   Completed: {tasks['completed']} (Total: {tasks['operations_total']})")

        if tasks['failed'] > 0:
            print(f"   Failed: {tasks['failed']}")

        # Recent activity
        if tasks['recent_completed']:
            print(f"\n🔄 Recent Completed Tasks:")
            for task in tasks['recent_completed']:
                print(f"   • {task['id']}: {task['type']} - {task['status']}")

        if tasks['recent_failed']:
            print(f"\n❌ Recent Failed Tasks:")
            for task in tasks['recent_failed']:
                result = task['result'][:50] + "..." if len(task['result']) > 50 else task['result']
                print(f"   • {task['id']}: {result}")

        # Emergency status
        print(f"\n🚨 EMERGENCY STATUS:")
        emergency = status['emergency']
        if emergency['active']:
            print(f"   🚨 EMERGENCY STOP ACTIVE!")
        else:
            print(f"   ✅ Normal operation - Real-time monitoring active")

        print("="*75)

    def show_stored_items_summary(self):
        """Show stored items summary"""
        inventory = self.controller.position_manager.get_inventory_report()

        if not inventory['occupied_positions']:
            print("📭 No items currently stored")
            return

        print(f"\n📋 STORED ITEMS SUMMARY")
        print("-" * 35)

        # Group by product
        products = {}
        for item in inventory['occupied_positions']:
            pid = item['product_id']
            if pid not in products:
                products[pid] = []
            products[pid].append(item)

        print(f"Total Items: {len(inventory['occupied_positions'])}")
        print(f"Unique Products: {len(products)}")
        print()

        print(f"{'Product ID':<20} {'Qty':<4} {'Positions':<25} {'Avg Duration'}")
        print("-" * 75)

        for product_id, items in sorted(products.items()):
            positions = [f"P{item['position_id']:02d}" for item in items]
            positions_str = ", ".join(positions)
            if len(positions_str) > 25:
                positions_str = positions_str[:22] + "..."

            # Average duration
            durations = [item['duration'] for item in items if item['duration'] > 0]
            avg_duration = sum(durations) / len(durations) if durations else 0
            duration_str = self._format_duration(timedelta(hours=avg_duration))

            print(f"{product_id:<20} {len(items):<4} {positions_str:<25} {duration_str}")

    def list_stored_items(self):
        """List stored items"""
        self.show_stored_items_summary()

        inventory = self.controller.position_manager.get_inventory_report()
        if inventory['occupied_positions']:
            print()
            show_details = input("Show detailed position information? (y/N): ").strip().lower()
            if show_details == 'y':
                print(f"\n📋 DETAILED INVENTORY")
                print("-" * 25)
                print(f"{'Pos':<4} {'Grid':<6} {'Product ID':<20} {'Stored At':<16} {'Duration'}")
                print("-" * 75)

                for item in sorted(inventory['occupied_positions'], key=lambda x: x['position_id']):
                    stored_time = datetime.fromisoformat(item['stored_at']).strftime("%m-%d %H:%M")
                    duration_str = self._format_duration(timedelta(hours=item['duration']))

                    print(f"P{item['position_id']:02d}  {item['grid_location']:<6} "
                          f"{item['product_id']:<20} {stored_time:<16} {duration_str}")

    async def update_display(self):
        """Update LED display using proven pattern"""
        print("\n💡 UPDATING LED DISPLAY (Proven Pattern)...")

        success = await self.controller.update_display()
        if success:
            print("✅ LED update task submitted")
            await self._wait_for_task_completion("updating display", "LEDs")
        else:
            print("❌ Failed to update LED display")

    async def monitor_buttons(self):
        """Monitor button presses using proven pattern"""
        print("\n🔘 BUTTON MONITORING MODE (Proven Pattern)")
        print("-" * 40)
        print("Real-time variable monitoring is active...")
        print("Button changes detected via proven asyncua pattern")
        print("Press Ctrl+C to stop monitoring\n")

        monitoring_start = datetime.now()
        events_detected = 0

        try:
            # Show current button states
            print("Current button states:")
            for pos_id in range(1, min(11, 36)):  # Show first 10
                position = self.controller.position_manager.get_position(pos_id)
                if position:
                    state = "🔘 PRESSED" if position.button_pressed else "⚪ Released"
                    print(f"   Button {pos_id}: {state}")

            print("\nMonitoring for button changes...")
            print("(Changes will be detected automatically via variable monitoring)")

            while True:
                current_time = datetime.now()
                elapsed = current_time - monitoring_start

                # Show periodic status
                if int(elapsed.total_seconds()) % 10 == 0:
                    print(f"📊 [{current_time.strftime('%H:%M:%S')}] Monitoring active... "
                          f"(Running {self._format_duration(elapsed)})")

                await asyncio.sleep(1.0)

        except KeyboardInterrupt:
            elapsed = datetime.now() - monitoring_start
            print(f"\n⏹️ Button monitoring stopped")
            print(f"   Duration: {self._format_duration(elapsed)}")
            print(f"   Note: Real-time variable monitoring continues in background")

    def check_emergency_status(self):
        """Check emergency status"""
        print("\n🚨 EMERGENCY STATUS CHECK")
        print("-" * 30)

        status = self.controller.get_system_status()
        emergency = status['emergency']

        if emergency['active']:
            print("🚨 EMERGENCY STOP IS ACTIVE!")
            print("   All operations stopped")
            print("   Clear emergency and restart system")
        else:
            print("✅ Emergency status is NORMAL")
            print(f"   System status: {status['status'].upper()}")
            print("   Real-time emergency monitoring active")

    def show_system_info(self):
        """Show system information"""
        print("\n📋 SYSTEM INFORMATION (Proven Asyncua)")
        print("-" * 40)

        config = self.controller.config
        session_duration = datetime.now() - self.session_start

        print("Application Information:")
        print(f"   Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Session Duration: {self._format_duration(session_duration)}")
        print(f"   Commands Executed: {self.commands_executed}")

        print("\nSystem Configuration:")
        print(f"   Name: {config['system']['name']}")
        print(f"   Version: {config['system']['version']}")
        print(f"   PLC Model: {config['system']['plc_model']}")
        print(f"   Communication: Proven Asyncua Pattern")

        print("\nPLC Configuration:")
        print(f"   IP Address: {config['plc']['ip']}")
        print(f"   Variables Path: {' → '.join(config['paths']['variables_path'])}")
        print(f"   Scan Interval: {config['operation']['scan_interval']}s")

        # Show OPC client statistics
        opc_stats = self.controller.opc_client.get_statistics()
        print("\nCommunication Statistics:")
        print(f"   Connection: {'🟢 Active' if opc_stats['connected'] else '🔴 Inactive'}")
        print(f"   Total Variables: {opc_stats['total_variables']}")
        print(f"   LED Nodes: {opc_stats['led_nodes']}")
        print(f"   Button Nodes: {opc_stats['button_nodes']}")
        print(f"   Operations: {opc_stats['reads']} reads, {opc_stats['writes']} writes")
        print(f"   Error Count: {opc_stats['errors']}")

    def clear_screen(self):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_header()
        if self.display_settings["auto_refresh"]:
            self.display_grid(force_update=True)

    async def run_interactive(self):
        """Run interactive interface using proven asyncio pattern"""
        self.display_header()
        self.show_commands()
        self.display_grid(force_update=True)

        while self.running:
            try:
                # Auto-refresh grid
                if (self.display_settings["auto_refresh"] and 
                    time.time() - self.last_grid_update > 30):
                    print("\n🔄 Auto-refreshing (proven pattern monitoring active)...")
                    self.display_grid(force_update=True)

                # Get command
                try:
                    command = input("\nEnter command: ").strip().upper()
                    if not command:
                        continue
                except EOFError:
                    print("\n🛑 EOF - shutting down")
                    break

                # Track commands
                self.commands_executed += 1
                self.command_history.append((datetime.now(), command))

                # Process commands using proven asyncio pattern
                if command == 'G':
                    self.display_grid(force_update=True)

                elif command == 'S':
                    await self.store_item_interface()

                elif command == 'R':
                    await self.retrieve_item_interface()

                elif command == 'P':
                    self.show_position_details()

                elif command == 'T':
                    self.display_system_status()

                elif command == 'L':
                    self.list_stored_items()

                elif command == 'U':
                    await self.update_display()

                elif command == 'M':
                    await self.monitor_buttons()

                elif command == 'E':
                    self.check_emergency_status()

                elif command == 'I':
                    self.show_system_info()

                elif command == 'C':
                    self.clear_screen()

                elif command == 'H':
                    self.show_commands()

                elif command == 'Q':
                    confirm = input("🛑 Quit system? (y/N): ").strip().lower()
                    if confirm == 'y':
                        print("🛑 Shutting down...")
                        await self.stop()
                        break
                    else:
                        print("❌ Cancelled")

                else:
                    print(f"❓ Unknown command: '{command}'. Type 'H' for help.")

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupt signal")
                confirm = input("Shutdown system? (y/N): ").strip().lower()
                if confirm == 'y':
                    await self.stop()
                    break
                else:
                    print("✅ Continuing...")

            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")
                print(f"❌ Error: {e}")

async def main():
    """Main entry point using proven asyncio pattern"""
    print("🏗️ BVM Auto Rack35 AS/RS Control System")
    print("   Starting with proven asyncua pattern...")

    app = None

    try:
        app = ASRSApplication()

        # Initialize with retries using proven pattern
        max_attempts = 3
        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"\n🔄 Attempt {attempt + 1}/{max_attempts}")
                await asyncio.sleep(2.0)

            if await app.initialize():
                break

            if attempt == max_attempts - 1:
                print("\n❌ Failed to initialize")
                return 1

        # Start and run using proven pattern
        await app.start()
        await app.run_interactive()

    except KeyboardInterrupt:
        print("\n🛑 Shutdown signal received")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        logger.exception("Fatal error")
        return 1
    finally:
        if app:
            try:
                await app.stop()
            except:
                pass

    print("\n👋 BVM AS/RS Control System shut down")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Crashed: {e}")
        sys.exit(1)
