
"""
Order Monitor Service
Monitors database for new orders and triggers ASRS operations
"""

import mysql.connector
import time
import threading
import logging
from datetime import datetime
from asrs_control_enhanced import ASRSController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrderMonitor:
    def __init__(self, db_config):
        self.db_config = db_config
        self.last_checked_order_id = self.get_last_order_id()
        self.asrs = ASRSController()
        self.running = False

    def get_db_connection(self):
        """Get database connection"""
        return mysql.connector.connect(**self.db_config)

    def get_last_order_id(self):
        """Get the last processed order ID"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(order_id) FROM Orders WHERE order_status != 'pending'")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result[0] else 0
        except Exception as e:
            logger.error(f"Error getting last order ID: {e}")
            return 0

    def get_new_orders(self):
        """Get orders that haven't been processed yet"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT o.order_id, o.customer_name, o.customer_email, o.order_status,
                   oi.order_item_id, oi.item_id, oi.quantity, i.name as item_name
            FROM Orders o 
            JOIN OrderItems oi ON o.order_id = oi.order_id
            JOIN Items i ON oi.item_id = i.item_id
            WHERE o.order_id > %s AND o.order_status = 'pending'
            ORDER BY o.order_id, oi.order_item_id
            """
            cursor.execute(query, (self.last_checked_order_id,))
            orders = cursor.fetchall()

            cursor.close()
            conn.close()
            return orders

        except Exception as e:
            logger.error(f"Error getting new orders: {e}")
            return []

    def find_item_locations(self, item_id, quantity_needed):
        """Find locations where the item is stored"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT subcom_place, item_id
            FROM SubCompartments 
            WHERE item_id = %s AND status = 'Occupied'
            ORDER BY subcom_place
            LIMIT %s
            """
            cursor.execute(query, (item_id, quantity_needed))
            locations = cursor.fetchall()

            cursor.close()
            conn.close()
            return locations

        except Exception as e:
            logger.error(f"Error finding item locations: {e}")
            return []

    def update_order_status(self, order_id, status):
        """Update order status in database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE Orders SET order_status = %s, updated_at = NOW() WHERE order_id = %s",
                (status, order_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"📝 Updated order {order_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

    def record_transaction(self, item_id, location, action='retrieved'):
        """Record transaction in database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO Transactions (item_id, subcom_place, action, time) VALUES (%s, %s, %s, NOW())",
                (item_id, location, action)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"📋 Recorded transaction: {action} item {item_id} from {location}")
            return True

        except Exception as e:
            logger.error(f"Error recording transaction: {e}")
            return False

    def update_subcompartment_status(self, location, status='Empty'):
        """Update subcompartment status after retrieval"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            if status == 'Empty':
                cursor.execute(
                    "UPDATE SubCompartments SET status = %s, item_id = NULL WHERE subcom_place = %s",
                    (status, location)
                )
            else:
                cursor.execute(
                    "UPDATE SubCompartments SET status = %s WHERE subcom_place = %s",
                    (status, location)
                )

            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"🗃️ Updated {location} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating subcompartment status: {e}")
            return False

    def process_order_item(self, order_data):
        """Process a single order item through ASRS"""
        order_id = order_data['order_id']
        item_id = order_data['item_id']
        quantity = order_data['quantity']
        item_name = order_data['item_name']

        logger.info(f"🛍️ Processing order {order_id}: {quantity}x {item_name} (ID: {item_id})")

        # Find item locations
        locations = self.find_item_locations(item_id, quantity)

        if len(locations) < quantity:
            logger.warning(f"⚠️ Insufficient stock: need {quantity}, found {len(locations)}")
            return False

        success_count = 0

        # Process each location
        for i, location_data in enumerate(locations[:quantity]):
            location = location_data['subcom_place']

            try:
                logger.info(f"📦 Retrieving item {i+1}/{quantity} from {location}")

                # Execute ASRS retrieval
                if self.asrs.execute_command('retrieve', location):
                    # Update database records
                    self.record_transaction(item_id, location, 'retrieved')
                    self.update_subcompartment_status(location, 'Empty')
                    success_count += 1
                    logger.info(f"✅ Successfully retrieved from {location}")

                    # Wait between operations
                    time.sleep(3)
                else:
                    logger.error(f"❌ Failed to retrieve from {location}")

            except Exception as e:
                logger.error(f"Error processing location {location}: {e}")

        return success_count == quantity

    def process_order(self, order_data):
        """Process complete order"""
        order_id = order_data['order_id']
        customer_name = order_data['customer_name']

        logger.info(f"🎯 Starting order {order_id} for {customer_name}")

        # Update order status to processing
        self.update_order_status(order_id, 'processing')

        try:
            # Process the order item
            success = self.process_order_item(order_data)

            if success:
                self.update_order_status(order_id, 'shipped')
                logger.info(f"✅ Order {order_id} completed successfully!")
                return True
            else:
                self.update_order_status(order_id, 'cancelled')
                logger.error(f"❌ Order {order_id} failed - marked as cancelled")
                return False

        except Exception as e:
            logger.error(f"Error processing order {order_id}: {e}")
            self.update_order_status(order_id, 'cancelled')
            return False

    def monitor_orders(self):
        """Main monitoring loop"""
        self.running = True
        logger.info("🚀 Order monitoring started...")

        while self.running:
            try:
                new_orders = self.get_new_orders()

                if new_orders:
                    # Group orders by order_id
                    orders_dict = {}
                    for order in new_orders:
                        order_id = order['order_id']
                        if order_id not in orders_dict:
                            orders_dict[order_id] = []
                        orders_dict[order_id].append(order)

                    # Process each order
                    for order_id, order_items in orders_dict.items():
                        logger.info(f"🆕 New order detected: {order_id}")

                        # Process each item in the order
                        order_success = True
                        for order_item in order_items:
                            item_success = self.process_order(order_item)
                            if not item_success:
                                order_success = False

                        # Update last processed order ID
                        self.last_checked_order_id = max(self.last_checked_order_id, order_id)

                # Wait before next check
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)

    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.running = False
        logger.info("🛑 Stopping order monitoring...")

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'inventory_management',
        'user': 'root',  # Update with your credentials
        'password': 'password',  # Update with your credentials
        'autocommit': True
    }

    monitor = OrderMonitor(db_config)

    try:
        monitor.monitor_orders()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n👋 Service stopped by user")
