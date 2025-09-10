
"""
Main ASRS Integration Service
Complete automation bridge between e-commerce and physical ASRS
"""

import sys
import signal
import time
import logging
from threading import Thread
from config import DATABASE_CONFIG, SERVICE_CONFIG
from order_monitor import OrderMonitor

# Configure logging
logging.basicConfig(
    level=getattr(logging, SERVICE_CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asrs_integration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ASRSIntegrationService:
    def __init__(self):
        self.order_monitor = OrderMonitor(DATABASE_CONFIG)
        self.monitor_thread = None
        self.running = False

    def start(self):
        """Start the integration service"""
        logger.info("🚀 Starting ASRS Integration Service...")
        logger.info("📊 Database: inventory_management")
        logger.info("🤖 ASRS: OPC UA Connection")
        logger.info("⏱️ Monitor Interval: {} seconds".format(SERVICE_CONFIG['monitor_interval']))

        try:
            # Start order monitoring in separate thread
            self.monitor_thread = Thread(target=self.order_monitor.monitor_orders, daemon=True)
            self.monitor_thread.start()
            self.running = True

            logger.info("✅ ASRS Integration Service is running!")
            logger.info("📦 Monitoring for new orders...")
            logger.info("🔄 Ready to process e-commerce orders automatically")

            # Keep main thread alive
            while self.running:
                time.sleep(1)

        except Exception as e:
            logger.error(f"❌ Service startup failed: {e}")
            self.stop()

    def stop(self):
        """Stop the integration service"""
        logger.info("🛑 Stopping ASRS Integration Service...")
        self.running = False

        if self.order_monitor:
            self.order_monitor.stop_monitoring()

        logger.info("👋 Service stopped successfully")

    def status(self):
        """Get service status"""
        if self.running:
            return "🟢 Service is running and monitoring orders"
        else:
            return "🔴 Service is stopped"

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info("📡 Received shutdown signal")
    service.stop()
    sys.exit(0)

def main():
    global service
    service = ASRSIntegrationService()

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        service.start()
    except KeyboardInterrupt:
        service.stop()

if __name__ == "__main__":
    main()
