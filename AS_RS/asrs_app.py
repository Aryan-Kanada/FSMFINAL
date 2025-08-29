"""
BVM AS/RS Interactive Application
User interface for controlling the 35-position AS/RS system
"""

import asyncio
import sys
import time
import logging
from typing import Optional
from datetime import datetime
from asrs_controller import ASRSController, ASRSTask

logger = logging.getLogger(__name__)

class ASRSApplication:
    """Interactive AS/RS application"""

    def __init__(self, config_path: str = "asrs_config.json"):
        self.controller = ASRSController(config_path)
        self.running = False
        self.last_grid_update = 0

    async def initialize(self) -> bool:
        """Initialize the application"""
        print("🔧 Initializing BVM AS/RS Application...")

        if not await self.controller.initialize():
            print("❌ Failed to initialize AS/RS controller")
            return False

        print("✅ BVM AS/RS Application initialized successfully")
        return True

    async def start(self):
        """Start the application"""
        if not self.running:
            await self.controller.start()
            self.running = True
            print("🚀 BVM AS/RS Application started")

    async def stop(self):
        """Stop the application"""
        if self.running:
            self.running = False
            await self.controller.stop()
            print("⏹️ BVM AS/RS Application stopped")

    def display_header(self):
        """Display application header"""
        config = self.controller.config
        print("\n" + "="*80)
        print("   🏗️ BVM AUTO RACK35 AS/RS CONTROL SYSTEM")
        print("   " + "=" * 50)
        print(f"   PLC: {config['system']['plc_model']} at {config['plc']['ip']}")
        print(f"   Positions: {config['rack']['positions']}")
        print(f"   Layout: {config['rack']['layout']['rows']}×{config['rack']['layout']['columns']} grid")
        print(f"   Version: {config['system']['version']}")
        print("="*80)

    def show_commands(self):
        """Display available commands"""
        print("\n📖 AVAILABLE COMMANDS:")
        print("  [G] → Show Grid Display      [S] → Store Item")
        print("  [R] → Retrieve Item          [P] → Position Details")
        print("  [T] → System Status          [L] → List Stored Items")
        print("  [U] → Update LED Display     [M] → Monitor Buttons")
        print("  [E] → Emergency Status       [H] → Help")
        print("  [Q] → Quit System")
        print("-" * 60)

    def display_grid(self):
        """Display the rack grid layout"""
        grid = self.controller.position_manager.get_grid_display()
        stats = self.controller.position_manager.get_statistics()

        print("\n" + "="*60)
        print("   📦 STORAGE RACK LAYOUT - LIVE STATUS")
        print("="*60)
        print(f"Occupancy: {stats['occupied_positions']}/{stats['total_positions']} ({stats['occupancy_percent']}%)")
        print("Legend: [##] = Occupied,  ##  = Empty")
        print()

        # Display column headers
        print("    ", end="")
        for col in range(1, stats['layout'].split('×')[1].strip() + 1):
            print(f"  C{col}  ", end="")
        print()

        # Display grid with row headers
        for i, row in enumerate(grid):
            print(f" R{i+1} ", end="")
            for cell in row:
                print(f" {cell} ", end="")
            print()

        print("="*60)

        # Show recent activity
        status = self.controller.get_system_status()
        if status['tasks']['recent']:
            print("\n🔄 Recent Activity:")
            for task in status['tasks']['recent']:
                print(f"  {task['id']}: {task['type']} - {task['status']}")

    async def store_item_interface(self):
        """Interactive store item interface"""
        print("\n📦 STORE ITEM IN RACK")
        print("-" * 25)

        try:
            product_id = input("Product ID: ").strip()
            if not product_id:
                print("❌ Product ID cannot be empty")
                return

            print("\nStorage options:")
            print("1. Auto-assign to first empty position")
            print("2. Specify position (1-35)")

            choice = input("Select option (1 or 2): ").strip()

            if choice == "1":
                success = await self.controller.store_item(product_id)
                if success:
                    print(f"✅ Storage task submitted for {product_id}")
                    await self._wait_for_task_completion("storing")
                else:
                    print("❌ Failed to submit storage task")

            elif choice == "2":
                try:
                    position_id = int(input("Position (1-35): "))
                    if 1 <= position_id <= 35:
                        position = self.controller.position_manager.get_position(position_id)
                        if position and position.status.value != "empty":
                            print(f"❌ Position {position_id} is already occupied")
                            return

                        success = await self.controller.store_item(product_id, position_id)
                        if success:
                            print(f"✅ Storage task submitted: {product_id} → Position {position_id}")
                            await self._wait_for_task_completion("storing")
                        else:
                            print("❌ Failed to submit storage task")
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")
            else:
                print("❌ Invalid option")

        except Exception as e:
            print(f"❌ Error: {e}")

    async def retrieve_item_interface(self):
        """Interactive retrieve item interface"""
        print("\n📤 RETRIEVE ITEM FROM RACK")
        print("-" * 27)

        try:
            print("Retrieval options:")
            print("1. By Position (1-35)")
            print("2. By Product ID")

            choice = input("Select option (1 or 2): ").strip()

            if choice == "1":
                try:
                    position_id = int(input("Position (1-35): "))
                    if 1 <= position_id <= 35:
                        position = self.controller.position_manager.get_position(position_id)
                        if not position or position.status.value == "empty":
                            print(f"❌ Position {position_id} is empty")
                            return

                        print(f"📦 Position {position_id} contains: {position.product_id}")
                        confirm = input("Retrieve this item? (y/N): ").strip().lower()

                        if confirm == 'y':
                            success = await self.controller.retrieve_item(position_id)
                            if success:
                                print(f"✅ Retrieval task submitted for position {position_id}")
                                await self._wait_for_task_completion("retrieving")
                            else:
                                print("❌ Failed to submit retrieval task")
                        else:
                            print("❌ Retrieval cancelled")
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")

            elif choice == "2":
                product_id = input("Product ID: ").strip()
                if not product_id:
                    print("❌ Product ID cannot be empty")
                    return

                position = self.controller.position_manager.find_product_position(product_id)
                if not position:
                    print(f"❌ Product {product_id} not found in rack")
                    return

                print(f"📍 Found {product_id} at position {position.id}")
                if position.stored_at:
                    print(f"📅 Stored at: {position.stored_at.strftime('%Y-%m-%d %H:%M:%S')}")

                confirm = input("Retrieve this item? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = await self.controller.retrieve_item(position.id)
                    if success:
                        print(f"✅ Retrieval task submitted for {product_id}")
                        await self._wait_for_task_completion("retrieving")
                    else:
                        print("❌ Failed to submit retrieval task")
                else:
                    print("❌ Retrieval cancelled")
            else:
                print("❌ Invalid option")

        except Exception as e:
            print(f"❌ Error: {e}")

    async def _wait_for_task_completion(self, operation: str):
        """Wait for task completion and show progress"""
        start_time = time.time()
        max_wait = 10  # Maximum wait time in seconds

        while time.time() - start_time < max_wait:
            if not self.controller.active_task:
                break
            print(f"\r⏱️  {operation.title()}... ({time.time() - start_time:.1f}s)", end='', flush=True)
            await asyncio.sleep(0.5)

        print("\n✅ Operation completed")
        self.display_grid()

    def show_position_details(self):
        """Show detailed position information"""
        print("\n📍 POSITION DETAILS")
        print("-" * 20)

        try:
            position_input = input("Position (1-35) or 'all': ").strip().lower()

            if position_input == 'all':
                occupied_positions = [
                    p for p in self.controller.position_manager.positions.values()
                    if p.status.value == "occupied"
                ]

                if occupied_positions:
                    print(f"\n📦 OCCUPIED POSITIONS ({len(occupied_positions)}):")
                    print(f"{'Pos':<4} {'Grid':<6} {'Product ID':<15} {'Stored At'}")
                    print("-" * 50)

                    for position in occupied_positions:
                        stored_time = position.stored_at.strftime("%Y-%m-%d %H:%M") if position.stored_at else "Unknown"
                        print(f"{position.id:<4} {position.grid_location:<6} {position.product_id:<15} {stored_time}")
                else:
                    print("\n📭 No positions are currently occupied")

            else:
                try:
                    position_id = int(position_input)
                    if 1 <= position_id <= 35:
                        position = self.controller.position_manager.get_position(position_id)

                        if position:
                            print(f"\n📍 POSITION {position_id} DETAILS:")
                            print(f"   Name: {position.position_name}")
                            print(f"   Grid Location: {position.grid_location}")
                            print(f"   Status: {position.status.value.upper()}")
                            print(f"   LED State: {'ON' if position.led_state else 'OFF'}")
                            if position.status.value == "occupied":
                                print(f"   Product ID: {position.product_id}")
                                stored_time = position.stored_at.strftime("%Y-%m-%d %H:%M:%S") if position.stored_at else "Unknown"
                                print(f"   Stored At: {stored_time}")
                        else:
                            print(f"❌ Position {position_id} not found")
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")

        except Exception as e:
            print(f"❌ Error: {e}")

    def display_system_status(self):
        """Display comprehensive system status"""
        status = self.controller.get_system_status()

        print("\n" + "="*70)
        print(f"   📊 SYSTEM STATUS - {status['system_name']}")
        print("="*70)
        print(f"Version: {status['version']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"System Status: {status['status'].upper()}")

        print(f"\n🔌 PLC CONNECTION:")
        plc = status['plc']
        print(f"   IP Address: {plc['ip']}")
        print(f"   URL: {plc['url']}")
        print(f"   Connected: {'Yes' if plc['connected'] else 'No'}")

        print(f"\n📦 STORAGE RACK:")
        rack = status['rack']
        print(f"   Total Positions: {rack['total_positions']}")
        print(f"   Occupied: {rack['occupied_positions']}")
        print(f"   Available: {rack['empty_positions']}")
        print(f"   Occupancy: {rack['occupancy_percent']}%")
        print(f"   Layout: {rack['layout']}")

        print(f"\n📋 TASKS:")
        tasks = status['tasks']
        print(f"   Queue Size: {tasks['queue_size']}")
        print(f"   Active: {tasks['active'] or 'None'}")
        print(f"   Completed: {tasks['completed']}")

        if tasks['recent']:
            print(f"\n🔄 Recent Tasks:")
            for task in tasks['recent']:
                print(f"   {task['id']}: {task['type']} - {task['status']}")

        print("="*70)

    def list_stored_items(self):
        """List all stored items"""
        positions = self.controller.position_manager.positions
        occupied = [p for p in positions.values() if p.status.value == "occupied"]

        print("\n📋 STORED ITEMS INVENTORY")
        print("-" * 30)

        if occupied:
            # Group by product ID
            products = {}
            for position in occupied:
                pid = position.product_id
                if pid not in products:
                    products[pid] = []
                products[pid].append(position)

            print(f"Total Items: {len(occupied)}")
            print(f"Unique Products: {len(products)}")
            print()

            print(f"{'Product ID':<15} {'Qty':<4} {'Positions':<20} {'Last Stored'}")
            print("-" * 65)

            for product_id, pos_list in products.items():
                pos_names = ", ".join([f"P{p.id:02d}" for p in pos_list])
                last_stored = max([p.stored_at for p in pos_list if p.stored_at])
                last_stored_str = last_stored.strftime("%m-%d %H:%M") if last_stored else "Unknown"
                print(f"{product_id:<15} {len(pos_list):<4} {pos_names:<20} {last_stored_str}")
        else:
            print("📭 No items currently stored in the rack")

    async def update_display(self):
        """Update LED display"""
        print("\n💡 UPDATING LED DISPLAY...")

        success = await self.controller.update_display()
        if success:
            print("✅ LED update task submitted")
            await self._wait_for_task_completion("updating display")
        else:
            print("❌ Failed to update LED display")

    async def monitor_buttons(self):
        """Monitor button presses"""
        print("\n🔘 BUTTON MONITORING MODE")
        print("-" * 25)
        print("Press Ctrl+C to stop monitoring...")
        print("Button presses will be shown in real-time\n")

        last_states = {}

        try:
            while True:
                for pos_id, position in self.controller.position_manager.positions.items():
                    current_state = position.button_pressed
                    last_state = last_states.get(pos_id, False)

                    if current_state and not last_state:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        if position.status.value == "occupied":
                            print(f"🔘 [{timestamp}] Button {pos_id} pressed - Auto-retrieving {position.product_id}")
                        else:
                            print(f"🔘 [{timestamp}] Button {pos_id} pressed - Position empty")

                    last_states[pos_id] = current_state

                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            print("\n⏹️ Stopped monitoring buttons")

    def check_emergency_status(self):
        """Check emergency status"""
        print("\n🚨 EMERGENCY STATUS")
        print("-" * 20)

        status = self.controller.get_system_status()
        system_status = status['status']

        if system_status == "emergency":
            print("🚨 EMERGENCY STOP IS ACTIVE!")
            print("   System has been shut down for safety")
            print("   Clear emergency condition and restart system")
        else:
            print("✅ Emergency status is NORMAL")
            print(f"   System status: {system_status.upper()}")

    async def run_interactive(self):
        """Run the interactive interface"""
        self.display_header()
        self.show_commands()

        while self.running:
            try:
                # Auto-refresh grid every 30 seconds
                if time.time() - self.last_grid_update > 30:
                    self.display_grid()
                    self.last_grid_update = time.time()

                command = input("\nEnter command: ").strip().upper()

                if command == 'G':
                    self.display_grid()
                    self.last_grid_update = time.time()

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

                elif command == 'H':
                    self.show_commands()

                elif command == 'Q':
                    print("🛑 Shutting down BVM AS/RS system...")
                    await self.stop()
                    break

                else:
                    print("❓ Unknown command. Type 'H' for help.")

            except KeyboardInterrupt:
                print("\n🛑 Received shutdown signal")
                await self.stop()
                break
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")
                print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    print("🏗️ Starting BVM Auto Rack35 AS/RS Control System...")

    app = ASRSApplication()

    try:
        if await app.initialize():
            await app.start()
            await app.run_interactive()
        else:
            print("❌ Failed to initialize BVM AS/RS system")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    finally:
        await app.stop()

    print("👋 BVM AS/RS Control System shut down successfully")
    return 0

if __name__ == "__main__":
    asyncio.run(main())
