
"""
Configuration file for ASRS Integration Service
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'inventory_management'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'autocommit': True
}

# ASRS Configuration
ASRS_CONFIG = {
    'server_url': os.getenv('ASRS_SERVER_URL', 'opc.tcp://10.10.14.104:4840'),
    'connection_timeout': int(os.getenv('ASRS_TIMEOUT', 10)),
    'operation_delay': float(os.getenv('ASRS_DELAY', 2.0))
}

# Service Configuration
SERVICE_CONFIG = {
    'monitor_interval': int(os.getenv('MONITOR_INTERVAL', 5)),
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'max_retries': int(os.getenv('MAX_RETRIES', 3))
}

# Location Mapping (for your specific ASRS layout)
LOCATION_MAPPING = {
    # Format: 'database_location': 'asrs_command'
    'A1': 'A1', 'A2': 'A2', 'A3': 'A3', 'A4': 'A4', 'A5': 'A5', 'A6': 'A6', 'A7': 'A7',
    'B1': 'B1', 'B2': 'B2', 'B3': 'B3', 'B4': 'B4', 'B5': 'B5', 'B6': 'B6', 'B7': 'B7',
    'C1': 'C1', 'C2': 'C2', 'C3': 'C3', 'C4': 'C4', 'C5': 'C5', 'C6': 'C6', 'C7': 'C7',
    'D1': 'D1', 'D2': 'D2', 'D3': 'D3', 'D4': 'D4', 'D5': 'D5', 'D6': 'D6', 'D7': 'D7',
    'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4', 'E5': 'E5', 'E6': 'E6', 'E7': 'E7'
}
