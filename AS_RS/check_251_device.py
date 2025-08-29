#!/usr/bin/env python3
"""
Check 192.168.251.1 Device
See if this is another interface of your AS/RS PLC
"""

import socket
import subprocess
import platform

def ping_test(ip):
    """Test if device responds to ping"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '2', ip], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '2', ip], 
                                  capture_output=True, text=True, timeout=10)

        return result.returncode == 0
    except:
        return False

def check_opc_port(ip):
    """Check if OPC UA port 4840 is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, 4840))
        sock.close()
        return result == 0
    except:
        return False

def check_common_ports(ip):
    """Check common industrial automation ports"""
    ports_to_check = {
        4840: "OPC UA",
        502: "Modbus TCP", 
        44818: "EtherNet/IP",
        80: "HTTP Web Interface",
        443: "HTTPS"
    }

    open_ports = []
    for port, description in ports_to_check.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                open_ports.append((port, description))
        except:
            pass

    return open_ports

def main():
    print("🔍 Checking Device at 192.168.251.1")
    print("=" * 40)

    ip = "192.168.251.1"

    # Test ping
    print("📡 Testing connectivity...")
    if ping_test(ip):
        print(f"✅ {ip} responds to ping")
    else:
        print(f"❌ {ip} does not respond to ping")
        print("   This device may not be accessible from your network")
        return

    # Check OPC UA specifically
    print("\n🔌 Testing OPC UA port 4840...")
    if check_opc_port(ip):
        print("✅ OPC UA server running on port 4840!")
        print("   This might be your AS/RS PLC on a different network!")
    else:
        print("❌ No OPC UA server on port 4840")

    # Check other ports
    print("\n🔍 Scanning common industrial ports...")
    open_ports = check_common_ports(ip)

    if open_ports:
        print("✅ Open ports found:")
        for port, description in open_ports:
            print(f"   Port {port}: {description}")
    else:
        print("❌ No common industrial ports open")

    print("\n" + "=" * 40)
    print("🎯 Analysis:")
    if check_opc_port(ip):
        print("   This device has OPC UA server!")
        print("   It might be your AS/RS PLC on 192.168.251.x network")
        print("   You may need to change your PC network settings")
    else:
        print("   This is not an OPC UA server")
        print("   Focus on enabling OPC UA on 10.10.14.104")

if __name__ == "__main__":
    main()
