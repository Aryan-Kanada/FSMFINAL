#!/usr/bin/env python3
"""
BVM Network Scanner - Find OMRON PLC IP Address
Scans 10.10.14.x network to find active devices
"""

import subprocess
import threading
import platform
import socket
from concurrent.futures import ThreadPoolExecutor

def ping_host(ip):
    """Ping a single IP address"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                  capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            return ip, True
        else:
            return ip, False
    except:
        return ip, False

def check_opc_port(ip):
    """Check if port 4840 (OPC UA) is open on the IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 4840))
        sock.close()
        return result == 0  # True if port is open
    except:
        return False

def scan_network():
    """Scan the 10.10.14.x network for active devices"""
    print("🔍 Scanning BVM Network (10.10.14.x) for Active Devices")
    print("=" * 60)
    print("This may take a moment...")

    # Scan range 10.10.14.100 to 10.10.14.110 (common PLC range)
    ip_range = [f"10.10.14.{i}" for i in range(100, 111)]

    # Add some other common addresses
    ip_range.extend([f"10.10.14.{i}" for i in [1, 10, 50, 113]])

    active_devices = []

    # Use ThreadPoolExecutor for faster scanning
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(ping_host, ip_range))

    print("\n📍 Active Devices Found:")
    print("-" * 40)

    for ip, is_active in results:
        if is_active:
            active_devices.append(ip)
            # Check if OPC UA port is open
            has_opc = check_opc_port(ip)
            opc_status = "🔌 OPC UA (4840)" if has_opc else "   No OPC UA"
            print(f"✅ {ip:<15} - {opc_status}")

    if not active_devices:
        print("❌ No active devices found in 10.10.14.100-110 range")
        print("\n🔍 Trying broader scan...")

        # Broader scan 10.10.14.1-50
        broader_range = [f"10.10.14.{i}" for i in range(1, 51)]
        with ThreadPoolExecutor(max_workers=20) as executor:
            broader_results = list(executor.map(ping_host, broader_range))

        for ip, is_active in broader_results:
            if is_active:
                has_opc = check_opc_port(ip)
                opc_status = "🔌 OPC UA (4840)" if has_opc else "   No OPC UA"
                print(f"✅ {ip:<15} - {opc_status}")

    print("\n" + "=" * 60)
    print("🎯 Looking for OMRON PLC:")
    print("   - Should respond to ping")
    print("   - Should have OPC UA port 4840 open")
    print("   - Usually in range 10.10.14.100-110")

if __name__ == "__main__":
    scan_network()
