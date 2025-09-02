"""
BVM AS/RS Application - Physical System Integration
Works with your actual Sysmac Studio PLC program
Supports physical crane movement and storage operations
"""

import asyncio
import json
import logging
from datetime import datetime
import signal
import sys
from pathlib import Path

# Import our actual AS/RS components
from asrs_core_actual import ActualPLCClient, PositionManager, SystemStatus, PositionStatus

logger = logging.getLogger(__name__)

class PhysicalASRSController:
    """Controller for physical AS/RS system"""

    def __init__(self, config_file: str = "asrs_config_actual.json"):
        self.config = self._load_config(config_file)
        self.plc_client = ActualPLCClient(self.config)
        self.position_manager = PositionManager(self.config)

        self.status = SystemStatus.DISCONNECTED
        self.running = False
        self.tasks = []

        # Statistics
        self.session_start = datetime.now()
        self.commands_executed = 0

    def _load_config(self, config_file: str) -> dict:
        """Load configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Default config
            return {
                "plc": {"url": "opc.tcp://10.10.14.104:4840"},
                "operation": {"scan_interval": 0.5}
            }

    async def initialize(self) -> bool:
        """Initialize physical AS/RS system"""
        try:
            logger.info("🔧 Initializing Physical AS/RS System...")
            logger.info("   Using your actual PLC variables from Sysmac Studio")

            # Connect to PLC
            if not await self.plc_client.connect():
                return False

            self.status = SystemStatus.CONNECTED
            logger.info("✅ Physical AS/RS System initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize AS/RS system: {e}")
            return False

    async def start(self):
        """Start AS/RS system"""
        try:
            self.status = SystemStatus.MONITORING
            self.running = True

            logger.info("🚀 Starting Physical AS/RS system...")

            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitor_system())
            self.tasks.append(monitor_task)

            logger.info("✅ Physical AS/RS system started successfully")

        except Exception as e:
            logger.error(f"Failed to start AS/RS system: {e}")

    async def stop(self):
        """Stop AS/RS system"""
        try:
            logger.info("⏹️ Stopping Physical AS/RS system...")

            self.running = False
            self.status = SystemStatus.DISCONNECTED

            # Cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()

            # Wait for tasks to complete
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)

            # Disconnect from PLC
            await self.plc_client.disconnect()

            logger.info("✅ Physical AS/RS system stopped")

        except Exception as e:
            logger.error(f"Error stopping system: {e}")

    async def _monitor_system(self):
        """Monitor physical system for button presses and changes"""
        try:
            logger.info("🔍 Monitoring physical AS/RS for button presses...")

            # Monitor PLC variables
            await self.plc_client.monitor_variable_changes(self._handle_plc_event)

        except asyncio.CancelledError:
            logger.info("System monitoring cancelled")
        except Exception as e:
            logger.error(f"System monitoring error: {e}")

    async def _handle_plc_event(self, event_type: str, position_id: int, value: any):
        """Handle events from physical PLC"""
        try:
            if event_type == "button_press":
                logger.info(f"🔘 Physical button pressed at position {position_id}")

                # Get position info
                position = self.position_manager.get_position(position_id)
                if position:
                    logger.info(f"   PLC Button: {position.plc_button_name}")
                    logger.info(f"   PLC LED: {position.plc_led_name}")

                    # If occupied, suggest retrieval
                    if position.status == PositionStatus.OCCUPIED:
                        logger.info(f"   💡 Position contains: {position.product_id}")
                        logger.info(f"   💡 Ready for retrieval!")
                    else:
                        logger.info(f"   💡 Position is empty - ready for storage!")

        except Exception as e:
            logger.error(f"Error handling PLC event: {e}")

    async def store_item_physically(self, product_id: str, position_id: int = None) -> bool:
        """Store item using physical AS/RS system"""
        try:
            self.status = SystemStatus.STORING

            # Auto-assign position if not specified
            if position_id is None:
                empty_pos = self.position_manager.find_empty_position()
                if not empty_pos:
                    logger.error("❌ No empty positions available")
                    return False
                position_id = empty_pos.id

            position = self.position_manager.get_position(position_id)
            if not position or not position.is_available:
                logger.error(f"❌ Position {position_id} not available")
                return False

            logger.info(f"📦 Starting physical store operation...")
            logger.info(f"   Product: {product_id}")
            logger.info(f"   Position: {position_id} ({position.plc_led_name})")

            # Execute physical store command
            if await self.plc_client.execute_store_command(position_id, product_id):
                # Update software inventory
                self.position_manager.store_item(position_id, product_id)

                # Turn on LED
                await self.plc_client.write_led_state(position_id, True)

                logger.info(f"✅ Physical store completed: {product_id} → Position {position_id}")
                self.commands_executed += 1
                return True
            else:
                logger.error(f"❌ Physical store operation failed")
                return False

        except Exception as e:
            logger.error(f"❌ Store operation error: {e}")
            return False
        finally:
            self.status = SystemStatus.MONITORING

    async def retrieve_item_physically(self, position_id: int) -> str:
        """Retrieve item using physical AS/RS system"""
        try:
            self.status = SystemStatus.RETRIEVING

            position = self.position_manager.get_position(position_id)
            if not position or position.status != PositionStatus.OCCUPIED:
                logger.error(f"❌ Position {position_id} is empty")
                return None

            logger.info(f"📤 Starting physical retrieve operation...")
            logger.info(f"   Position: {position_id} ({position.plc_button_name})")
            logger.info(f"   Product: {position.product_id}")

            # Execute physical retrieve command
            retrieved_item = await self.plc_client.execute_retrieve_command(position_id)

            if retrieved_item:
                # Update software inventory
                product_id = self.position_manager.retrieve_item(position_id)

                # Turn off LED
                await self.plc_client.write_led_state(position_id, False)

                logger.info(f"✅ Physical retrieve completed: {product_id} from Position {position_id}")
                self.commands_executed += 1
                return product_id
            else:
                logger.error(f"❌ Physical retrieve operation failed")
                return None

        except Exception as e:
            logger.error(f"❌ Retrieve operation error: {e}")
            return None
        finally:
            self.status = SystemStatus.MONITORING

    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        plc_stats = self.plc_client.get_statistics()
        rack_stats = self.position_manager.get_statistics()

        return {
            "system": {
                "status": self.status.value,
                "uptime": (datetime.now() - self.session_start).total_seconds(),
                "commands_executed": self.commands_executed
            },
            "plc": plc_stats,
            "rack": rack_stats,
            "timestamp": datetime.now().isoformat()
        }

    def display_grid(self):
        """Display current rack status"""
        grid = self.position_manager.get_grid_display()

        print("=" * 75)
        print("   📦 PHYSICAL AS/RS RACK STATUS - LIVE")
        print("=" * 75)
        print(f"Occupancy: {self.position_manager.get_statistics()['occupied_positions']}/35")
        print("Legend: [##] = Occupied,  ##  = Empty")
        print("      C1    C2    C3    C4    C5    C6    C7")

        row_labels = ['A', 'B', 'C', 'D', 'E']
        for i, row in enumerate(grid):
            print(f" {row_labels[i]}  " + "  ".join(row))
        print("=" * 75)

async def run_interactive_mode(controller: PhysicalASRSController):
    """Run interactive AS/RS interface"""

    print("="*80)
    print("   🏭 BVM PHYSICAL AS/RS CONTROL SYSTEM")
    print("="*80)
    print(f"   PLC: {controller.config['plc']['url']}")
    print(f"   Status: {controller.status.value.upper()}")
    print(f"   Physical Rack: 35 positions (5×7)")
    print("="*80)
    print()

    while controller.running:
        try:
            controller.display_grid()

            print("\n📖 COMMANDS:")
            print("  [S] Store Item        [R] Retrieve Item")
            print("  [G] Show Grid         [T] System Status")
            print("  [I] Inventory Report  [Q] Quit")
            print("-" * 50)

            command = input("Enter command: ").upper().strip()
            controller.commands_executed += 1

            if command == 'Q':
                break
            elif command == 'G':
                # Grid already displayed above
                pass
            elif command == 'T':
                status = controller.get_system_status()
                print("\n📊 SYSTEM STATUS:")
                print(f"   Status: {status['system']['status']}")
                print(f"   Uptime: {status['system']['uptime']:.1f}s")
                print(f"   Commands: {status['system']['commands_executed']}")
                print(f"   PLC Reads: {status['plc']['reads']}")
                print(f"   PLC Writes: {status['plc']['writes']}")
                print(f"   Rack Occupancy: {status['rack']['occupied_positions']}/35")

            elif command == 'S':
                product_id = input("Product ID: ").strip()
                if product_id:
                    print("\n1. Auto-assign position")
                    print("2. Specify position (1-35)")
                    choice = input("Select (1 or 2): ").strip()

                    position_id = None
                    if choice == '2':
                        try:
                            position_id = int(input("Position (1-35): "))
                            if not (1 <= position_id <= 35):
                                print("❌ Invalid position")
                                continue
                        except ValueError:
                            print("❌ Invalid position number")
                            continue

                    print(f"\n🏗️ Starting physical store operation...")
                    success = await controller.store_item_physically(product_id, position_id)
                    if success:
                        print("✅ Item stored successfully!")
                    else:
                        print("❌ Store operation failed")

            elif command == 'R':
                try:
                    position_id = int(input("Position to retrieve (1-35): "))
                    if not (1 <= position_id <= 35):
                        print("❌ Invalid position")
                        continue

                    print(f"\n🏗️ Starting physical retrieve operation...")
                    product_id = await controller.retrieve_item_physically(position_id)
                    if product_id:
                        print(f"✅ Retrieved: {product_id}")
                    else:
                        print("❌ Retrieve operation failed")

                except ValueError:
                    print("❌ Invalid position number")

            elif command == 'I':
                report = controller.position_manager.get_inventory_report()
                print("\n📋 INVENTORY REPORT:")
                print(f"Total Positions: {report['summary']['total_positions']}")
                print(f"Occupied: {report['summary']['occupied_positions']}")
                print(f"Empty: {report['summary']['empty_positions']}")
                print(f"Occupancy: {report['summary']['occupancy_percent']}%")

                if report['occupied_positions']:
                    print("\nOccupied Positions:")
                    for pos in report['occupied_positions'][:10]:  # Show first 10
                        print(f"  {pos['position_id']:2d}: {pos['product_id']} ({pos['plc_led']})")

            else:
                print("❌ Unknown command")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Interactive mode error: {e}")
            print(f"❌ Error: {e}")

async def main():
    """Main application entry point"""
    print("🏭 BVM Physical AS/RS Control System")
    print("Using your actual Sysmac Studio PLC variables")
    print()

    # Create controller
    controller = PhysicalASRSController()

    try:
        # Initialize system
        if not await controller.initialize():
            print("❌ Failed to initialize AS/RS system")
            return

        # Start system
        await controller.start()

        # Run interactive interface
        await run_interactive_mode(controller)

    finally:
        # Clean shutdown
        await controller.stop()
        print("👋 Physical AS/RS system shut down")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
