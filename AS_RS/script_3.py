# Create the main OMRON AS/RS application with interactive interface

omron_app_code = '''
"""
OMRON Auto Rack35 AS/RS Control Application
Interactive control interface for 35-position storage system
"""

import sys
import time
from omron_asrs_controller import *

class OmronASRSApplication:
    """Main application for OMRON Auto Rack35 AS/RS control"""
    
    def __init__(self, config_path: str = 'omron_asrs_config.json'):
        self.controller = OmronASRSController(config_path)
        self.running = False
        self.last_grid_update = 0
    
    def initialize(self) -> bool:
        """Initialize the AS/RS application"""
        logger.info("🔧 Initializing OMRON AS/RS Application...")
        
        if not self.controller.initialize():
            logger.error("❌ Failed to initialize OMRON AS/RS controller")
            return False
        
        logger.info("✅ OMRON AS/RS Application initialized successfully")
        return True
    
    def start(self):
        """Start the AS/RS application"""
        if not self.running:
            self.controller.start()
            self.running = True
            logger.info("🚀 OMRON AS/RS Application started")
    
    def stop(self):
        """Stop the AS/RS application"""
        if self.running:
            self.running = False
            self.controller.stop()
            logger.info("⏹️ OMRON AS/RS Application stopped")
    
    def run_interactive(self):
        """Run the interactive command interface"""
        self.display_header()
        self.show_help()
        
        while self.running:
            try:
                # Show live grid every 5 seconds or on command
                if time.time() - self.last_grid_update > 5:
                    self.display_live_grid()
                    self.last_grid_update = time.time()
                
                command = input("\\nEnter command: ").strip().upper()
                
                if command == 'G':
                    self.display_live_grid()
                    
                elif command == 'S':
                    self.store_item_interface()
                    
                elif command == 'R':
                    self.retrieve_item_interface()
                    
                elif command == 'P':
                    self.show_position_details()
                    
                elif command == 'T':
                    self.display_system_status()
                    
                elif command == 'M':
                    self.monitor_pushbuttons()
                    
                elif command == 'L':
                    self.list_stored_items()
                    
                elif command == 'U':
                    self.update_display()
                    
                elif command == 'E':
                    self.check_emergency_status()
                    
                elif command == 'H':
                    self.show_help()
                    
                elif command == 'Q':
                    print("🛑 Shutting down OMRON AS/RS system...")
                    self.stop()
                    break
                    
                else:
                    print("❓ Unknown command. Type 'H' for help.")
                    
            except KeyboardInterrupt:
                print("\\n🛑 Received shutdown signal")
                self.stop()
                break
            except Exception as e:
                logger.error(f"❌ Error in interactive loop: {e}")
    
    def display_header(self):
        """Display application header"""
        print("\\n" + "="*80)
        print("   🏗️ OMRON AUTO RACK35 AS/RS CONTROL SYSTEM")
        print("   " + "=" * 50)
        print(f"   PLC: {self.controller.config['system']['plc_model']}")
        print(f"   Positions: {self.controller.config['storage_rack']['total_positions']}")
        print(f"   Layout: {self.controller.config['storage_rack']['layout']['rows']}×{self.controller.config['storage_rack']['layout']['columns']} grid")
        print("="*80)
    
    def show_help(self):
        """Display help information"""
        print("\\n📖 AVAILABLE COMMANDS:")
        print("  [G] → Show Grid Display      [S] → Store Item")
        print("  [R] → Retrieve Item          [P] → Position Details")  
        print("  [T] → System Status          [M] → Monitor Push Buttons")
        print("  [L] → List Stored Items      [U] → Update LED Display")
        print("  [E] → Emergency Status       [H] → Help")
        print("  [Q] → Quit System")
        print("-" * 60)
    
    def display_live_grid(self):
        """Display real-time grid layout with LED status"""
        grid = self.controller.get_position_grid()
        stats = self.controller.position_manager.get_occupancy_stats()
        
        print("\\n" + "="*60)
        print("   📦 STORAGE RACK LAYOUT - LIVE STATUS")
        print("="*60)
        print(f"Occupancy: {stats['occupied_positions']}/{stats['total_positions']} ({stats['occupancy_percent']}%)")
        print("Legend: [##] = Occupied, ## = Empty")
        print()
        
        # Display column headers
        print("    ", end="")
        for col in range(1, 6):  # Columns 1-5
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
        if self.controller.completed_tasks:
            recent = self.controller.completed_tasks[-3:]
            print("\\n🔄 Recent Activity:")
            for task in recent:
                time_str = task.completed_at.strftime("%H:%M:%S") if task.completed_at else "Unknown"
                print(f"  {time_str}: {task.task_type.value} - {task.status}")
    
    def store_item_interface(self):
        """Interactive store item interface"""
        print("\\n📦 STORE ITEM IN RACK")
        print("-" * 25)
        
        try:
            product_id = input("Product ID: ").strip()
            if not product_id:
                print("❌ Product ID cannot be empty")
                return
            
            print("Storage options:")
            print("1. Auto-assign to first empty position")
            print("2. Specify position (1-35)")
            
            choice = input("Select option (1 or 2): ").strip()
            
            if choice == "1":
                # Auto-assign position
                if self.controller.store_item_auto_position(product_id):
                    print(f"✅ Storage task submitted for {product_id}")
                    
                    # Wait for completion and show progress
                    start_time = time.time()
                    while self.controller.active_task and time.time() - start_time < 10:
                        print(f"\\r⏱️  Storing {product_id}... ({time.time() - start_time:.1f}s)", end='', flush=True)
                        time.sleep(0.5)
                    
                    print("\\n✅ Item stored successfully")
                    self.display_live_grid()
                else:
                    print("❌ Failed to store item")
            
            elif choice == "2":
                # Specific position
                try:
                    position_id = int(input("Position (1-35): "))
                    if 1 <= position_id <= 35:
                        position = self.controller.position_manager.get_position(position_id)
                        if position and position.occupied:
                            print(f"❌ Position {position_id} is already occupied with {position.product_id}")
                            return
                        
                        if self.controller.store_item_at_position(position_id, product_id):
                            print(f"✅ Storage task submitted: {product_id} → Position {position_id}")
                            
                            # Wait for completion
                            start_time = time.time()
                            while self.controller.active_task and time.time() - start_time < 10:
                                print(f"\\r⏱️  Storing... ({time.time() - start_time:.1f}s)", end='', flush=True)
                                time.sleep(0.5)
                            
                            print("\\n✅ Item stored successfully")
                            self.display_live_grid()
                        else:
                            print("❌ Failed to store item")
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")
            
            else:
                print("❌ Invalid option")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def retrieve_item_interface(self):
        """Interactive retrieve item interface"""
        print("\\n📤 RETRIEVE ITEM FROM RACK")
        print("-" * 27)
        
        try:
            print("Retrieval options:")
            print("1. By Position (1-35)")
            print("2. By Product ID")
            
            choice = input("Select option (1 or 2): ").strip()
            
            if choice == "1":
                # By position
                try:
                    position_id = int(input("Position (1-35): "))
                    if 1 <= position_id <= 35:
                        position = self.controller.position_manager.get_position(position_id)
                        if not position or not position.occupied:
                            print(f"❌ Position {position_id} is empty")
                            return
                        
                        print(f"📦 Position {position_id} contains: {position.product_id}")
                        confirm = input("Retrieve this item? (y/N): ").strip().lower()
                        
                        if confirm == 'y':
                            if self.controller.retrieve_item_from_position(position_id):
                                print(f"✅ Retrieval task submitted for position {position_id}")
                                
                                # Wait for completion
                                start_time = time.time()
                                while self.controller.active_task and time.time() - start_time < 10:
                                    print(f"\\r⏱️  Retrieving... ({time.time() - start_time:.1f}s)", end='', flush=True)
                                    time.sleep(0.5)
                                
                                print("\\n✅ Item retrieved successfully")
                                self.display_live_grid()
                            else:
                                print("❌ Failed to retrieve item")
                        else:
                            print("❌ Retrieval cancelled")
                    else:
                        print("❌ Position must be between 1 and 35")
                except ValueError:
                    print("❌ Invalid position number")
            
            elif choice == "2":
                # By product ID
                product_id = input("Product ID: ").strip()
                if not product_id:
                    print("❌ Product ID cannot be empty")
                    return
                
                position = self.controller.position_manager.find_product(product_id)
                if not position:
                    print(f"❌ Product {product_id} not found in rack")
                    return
                
                print(f"📍 Found {product_id} at position {position.id}")
                print(f"📅 Stored at: {position.stored_at.strftime('%Y-%m-%d %H:%M:%S') if position.stored_at else 'Unknown'}")
                
                confirm = input("Retrieve this item? (y/N): ").strip().lower()
                if confirm == 'y':
                    if self.controller.retrieve_item_by_product(product_id):
                        print(f"✅ Retrieval task submitted for {product_id}")
                        
                        # Wait for completion
                        start_time = time.time()
                        while self.controller.active_task and time.time() - start_time < 10:
                            print(f"\\r⏱️  Retrieving... ({time.time() - start_time:.1f}s)", end='', flush=True)
                            time.sleep(0.5)
                        
                        print("\\n✅ Item retrieved successfully")
                        self.display_live_grid()
                    else:
                        print("❌ Failed to retrieve item")
                else:
                    print("❌ Retrieval cancelled")
            
            else:
                print("❌ Invalid option")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_position_details(self):
        """Show detailed position information"""
        print("\\n📍 POSITION DETAILS")
        print("-" * 20)
        
        try:
            position_input = input("Position (1-35) or 'all': ").strip().lower()
            
            if position_input == 'all':
                details = self.controller.get_position_details()
                occupied_positions = [d for d in details if d['occupied']]
                
                if occupied_positions:
                    print(f"\\n📦 OCCUPIED POSITIONS ({len(occupied_positions)}):")
                    print(f"{'Pos':<4} {'Grid':<6} {'Product ID':<15} {'Stored At'}")
                    print("-" * 50)
                    
                    for detail in occupied_positions:
                        stored_time = detail['stored_at'][:16] if detail['stored_at'] else "Unknown"
                        print(f"{detail['id']:<4} {detail['grid_location']:<6} {detail['product_id']:<15} {stored_time}")
                else:
                    print("\\n📭 No positions are currently occupied")
            
            else:
                try:
                    position_id = int(position_input)
                    if 1 <= position_id <= 35:
                        details = self.controller.get_position_details()
                        detail = next((d for d in details if d['id'] == position_id), None)
                        
                        if detail:
                            print(f"\\n📍 POSITION {position_id} DETAILS:")
                            print(f"   Name: {detail['name']}")
                            print(f"   Grid Location: {detail['grid_location']}")
                            print(f"   Status: {detail['status'].upper()}")
                            print(f"   Occupied: {'Yes' if detail['occupied'] else 'No'}")
                            if detail['occupied']:
                                print(f"   Product ID: {detail['product_id']}")
                                stored_time = detail['stored_at'][:19] if detail['stored_at'] else "Unknown"
                                print(f"   Stored At: {stored_time}")
                            print(f"   LED Node: {detail['led_node']}")
                            print(f"   Push Button: {detail['pushbutton_node']}")
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
        
        print("\\n" + "="*70)
        print(f"   📊 SYSTEM STATUS - {status['system_name']}")
        print("="*70)
        print(f"PLC Model: {status['plc_model']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"System Status: {status['status'].upper()}")
        
        print(f"\\n🔌 COMMUNICATION:")
        comm = status['communication']
        print(f"   Protocol: {comm['protocol']}")
        print(f"   Endpoint: {comm['endpoint']}")
        print(f"   Connected: {'Yes' if comm['connected'] else 'No'}")
        
        print(f"\\n📦 STORAGE:")
        storage = status['storage']
        print(f"   Total Positions: {storage['total_positions']}")
        print(f"   Occupied: {storage['occupied_positions']}")
        print(f"   Available: {storage['empty_positions']}")
        print(f"   Occupancy: {storage['occupancy_percent']}%")
        print(f"   Layout: {storage['grid_layout']}")
        
        print(f"\\n📋 TASKS:")
        tasks = status['tasks']
        print(f"   Pending: {tasks['pending']}")
        print(f"   Active: {tasks['active'] or 'None'}")
        print(f"   Completed: {tasks['completed']}")
        
        if tasks['recent']:
            print(f"\\n🔄 Recent Tasks:")
            for task in tasks['recent']:
                print(f"   {task['id']}: {task['type']} - {task['status']}")
        
        print(f"\\n🚨 SAFETY:")
        safety = status['safety']
        emergency_status = "ACTIVE" if safety['emergency_stop'] else "NORMAL"
        print(f"   Emergency Stop: {emergency_status}")
        
        print("="*70)
    
    def monitor_pushbuttons(self):
        """Monitor push button presses in real-time"""
        print("\\n🔘 PUSH BUTTON MONITORING")
        print("-" * 25)
        print("Press Ctrl+C to stop monitoring...")
        print("Push buttons will trigger automatic retrieval of items")
        
        try:
            last_pressed = set()
            while True:
                pressed = set(self.controller.position_manager.monitor_pushbuttons())
                
                # Check for new button presses
                new_presses = pressed - last_pressed
                if new_presses:
                    for pos_id in new_presses:
                        position = self.controller.position_manager.get_position(pos_id)
                        if position:
                            if position.occupied:
                                print(f"🔘 Button {pos_id} pressed - Auto-retrieving {position.product_id}")
                            else:
                                print(f"🔘 Button {pos_id} pressed - Position empty")
                
                last_pressed = pressed
                time.sleep(0.2)  # Check 5 times per second
                
        except KeyboardInterrupt:
            print("\\n⏹️ Stopped monitoring push buttons")
    
    def list_stored_items(self):
        """List all currently stored items"""
        details = self.controller.get_position_details()
        occupied_positions = [d for d in details if d['occupied']]
        
        print("\\n📋 STORED ITEMS INVENTORY")
        print("-" * 30)
        
        if occupied_positions:
            # Group by product ID
            products = {}
            for detail in occupied_positions:
                pid = detail['product_id']
                if pid not in products:
                    products[pid] = []
                products[pid].append(detail)
            
            print(f"Total Items: {len(occupied_positions)}")
            print(f"Unique Products: {len(products)}")
            print()
            
            print(f"{'Product ID':<15} {'Qty':<4} {'Positions':<20} {'Last Stored'}")
            print("-" * 65)
            
            for product_id, positions in products.items():
                pos_list = ", ".join([f"P{p['id']:02d}" for p in positions])
                last_stored = max([p['stored_at'] for p in positions if p['stored_at']])
                last_stored_str = last_stored[:16] if last_stored else "Unknown"
                print(f"{product_id:<15} {len(positions):<4} {pos_list:<20} {last_stored_str}")
        else:
            print("📭 No items currently stored in the rack")
    
    def update_display(self):
        """Update all LED displays"""
        print("\\n💡 UPDATING LED DISPLAY...")
        
        if self.controller.update_display():
            print("✅ LED update task submitted")
            
            # Wait for completion
            start_time = time.time()
            while self.controller.active_task and time.time() - start_time < 5:
                print(f"\\r⏱️  Updating LEDs... ({time.time() - start_time:.1f}s)", end='', flush=True)
                time.sleep(0.5)
            
            print("\\n✅ LED display updated successfully")
            self.display_live_grid()
        else:
            print("❌ Failed to update LED display")
    
    def check_emergency_status(self):
        """Check emergency stop status"""
        print("\\n🚨 EMERGENCY STATUS CHECK")
        print("-" * 25)
        
        kill_status = self.controller.opc_client.read_value(
            self.controller.config['control_nodes']['emergency_kill']
        )
        
        if kill_status is None:
            print("⚠️ Unable to read emergency kill switch status")
        elif kill_status:
            print("🚨 EMERGENCY KILL SWITCH IS ACTIVE!")
            print("   System is in emergency stop state")
            print("   Reset the emergency switch and restart system")
        else:
            print("✅ Emergency kill switch is NORMAL")
            print("   System is safe to operate")
        
        print(f"   System Status: {self.controller.status.value.upper()}")


def main():
    """Main entry point for OMRON AS/RS application"""
    print("🏗️ Starting OMRON Auto Rack35 AS/RS Control System...")
    
    app = OmronASRSApplication()
    
    if app.initialize():
        app.start()
        
        try:
            app.run_interactive()
        except KeyboardInterrupt:
            print("\\n🛑 Received shutdown signal")
        finally:
            app.stop()
    else:
        print("❌ Failed to initialize OMRON AS/RS system")
        return 1
    
    print("👋 OMRON AS/RS Control System shut down successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

# Save the OMRON application
with open('omron_asrs_app.py', 'w') as f:
    f.write(omron_app_code)

print("✅ OMRON AS/RS Application created: omron_asrs_app.py")
print("   - Interactive 7×5 grid display")
print("   - Store/retrieve item operations")
print("   - Real-time LED status monitoring")
print("   - Push button monitoring")
print("   - Position-specific controls")
print("   - Emergency stop monitoring")
print("   - Inventory management")