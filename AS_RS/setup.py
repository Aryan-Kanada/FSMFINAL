"""
BVM AS/RS Setup Script
Quick setup and configuration for AS/RS system
"""

import json
import subprocess
import sys

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Dependencies")
    print("-" * 30)

    packages = ["asyncua"]

    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False

    print("   ✅ All dependencies installed")
    return True

def verify_config():
    """Verify configuration file"""
    print("\n⚙️ Verifying Configuration")
    print("-" * 30)

    try:
        with open('asrs_config.json', 'r') as f:
            config = json.load(f)

        print(f"   ✅ Configuration loaded")
        print(f"   📍 PLC IP: {config['plc']['ip']}")
        print(f"   🔗 PLC URL: {config['plc']['url']}")
        print(f"   📦 Positions: {config['rack']['positions']}")
        print(f"   📐 Layout: {config['rack']['layout']['rows']}×{config['rack']['layout']['columns']}")

        return True

    except FileNotFoundError:
        print("   ❌ Configuration file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in configuration: {e}")
        return False

def update_plc_ip():
    """Update PLC IP address in configuration"""
    print("\n🔧 PLC IP Configuration")
    print("-" * 30)

    try:
        with open('asrs_config.json', 'r') as f:
            config = json.load(f)

        current_ip = config['plc']['ip']
        print(f"   Current PLC IP: {current_ip}")

        new_ip = input("   Enter new PLC IP (or press Enter to keep current): ").strip()

        if new_ip and new_ip != current_ip:
            config['plc']['ip'] = new_ip
            config['plc']['url'] = f"opc.tcp://{new_ip}:4840"

            with open('asrs_config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print(f"   ✅ PLC IP updated to: {new_ip}")
            return True
        else:
            print(f"   ✅ PLC IP unchanged: {current_ip}")
            return True

    except Exception as e:
        print(f"   ❌ Error updating PLC IP: {e}")
        return False

def check_system_files():
    """Check if all system files are present"""
    print("\n📁 Checking System Files")
    print("-" * 30)

    required_files = [
        'asrs_config.json',
        'asrs_core.py',
        'asrs_controller.py',
        'asrs_app.py',
        'discover_plc.py',
        'test_system.py'
    ]

    missing_files = []

    for file_name in required_files:
        try:
            with open(file_name, 'r') as f:
                pass  # Just check if file can be opened
            print(f"   ✅ {file_name}")
        except FileNotFoundError:
            print(f"   ❌ {file_name} - MISSING")
            missing_files.append(file_name)

    if missing_files:
        print(f"\n   ❌ Missing {len(missing_files)} files")
        return False
    else:
        print(f"\n   ✅ All {len(required_files)} files present")
        return True

def main():
    """Main setup process"""
    print("🏗️ BVM AS/RS System Setup")
    print("=" * 40)
    print("Setting up Auto Rack35 AS/RS Control System")
    print()

    steps = [
        ("Check System Files", check_system_files),
        ("Install Dependencies", install_dependencies),
        ("Verify Configuration", verify_config),
        ("Update PLC IP", update_plc_ip)
    ]

    for step_name, step_func in steps:
        success = step_func()
        if not success:
            print(f"\n❌ Setup failed at: {step_name}")
            return False

    print("\n" + "="*40)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*40)

    print("\n🚀 Next Steps:")
    print("   1. python discover_plc.py    # Discover PLC variables")
    print("   2. python test_system.py     # Test system components")
    print("   3. python asrs_app.py        # Start AS/RS control system")

    print("\n💡 Tips:")
    print("   - Ensure your OMRON PLC is powered on")
    print("   - Verify OPC UA server is enabled in Sysmac Studio")
    print("   - Check network connectivity to 10.10.14.104")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup incomplete. Please resolve errors and try again.")
        sys.exit(1)
    else:
        sys.exit(0)
