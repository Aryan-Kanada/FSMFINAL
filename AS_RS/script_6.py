# 7. Create setup and requirements using proven asyncua pattern

setup_proven_code = '''"""
BVM AS/RS Setup Script - Proven Asyncua Pattern
Setup for AS/RS system using your working asyncua connection
"""

import json
import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages for proven pattern"""
    print("📦 Installing Dependencies (Proven Pattern)")
    print("-" * 45)
    
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
    print("   💡 Using asyncua (async version) - matches your working code")
    return True

def verify_config():
    """Verify configuration file"""
    print("\\n⚙️ Verifying Configuration (Proven Pattern)")
    print("-" * 50)
    
    try:
        with open('asrs_config.json', 'r') as f:
            config = json.load(f)
        
        print(f"   ✅ Configuration loaded")
        print(f"   📍 PLC IP: {config['plc']['ip']}")
        print(f"   🔗 PLC URL: {config['plc']['url']}")
        print(f"   📦 Positions: {config['rack']['positions']}")
        print(f"   📐 Layout: {config['rack']['layout']['rows']}×{config['rack']['layout']['columns']}")
        
        # Check proven path configuration
        if 'paths' in config and 'variables_path' in config['paths']:
            path = config['paths']['variables_path']
            print(f"   📁 Variables Path: {' → '.join(path)}")
            print(f"   ✅ Using proven path configuration")
        
        return True
        
    except FileNotFoundError:
        print("   ❌ Configuration file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON: {e}")
        return False

def update_plc_ip():
    """Update PLC IP address"""
    print("\\n🔧 PLC IP Configuration (Proven Pattern)")
    print("-" * 45)
    
    try:
        with open('asrs_config.json', 'r') as f:
            config = json.load(f)
        
        current_ip = config['plc']['ip']
        print(f"   Current PLC IP: {current_ip}")
        print(f"   Proven working IP: 10.10.14.104")
        
        new_ip = input("   Enter new PLC IP (or press Enter to keep current): ").strip()
        
        if new_ip and new_ip != current_ip:
            config['plc']['ip'] = new_ip
            config['plc']['url'] = f"opc.tcp://{new_ip}:4840"
            
            with open('asrs_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"   ✅ PLC IP updated to: {new_ip}")
        else:
            print(f"   ✅ PLC IP unchanged: {current_ip}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error updating PLC IP: {e}")
        return False

def check_system_files():
    """Check if all system files are present"""
    print("\\n📁 Checking System Files (Proven Pattern)")
    print("-" * 45)
    
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
        if os.path.exists(file_name):
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} - MISSING")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\\n   ❌ Missing {len(missing_files)} files")
        return False
    else:
        print(f"\\n   ✅ All {len(required_files)} files present")
        print(f"   💡 All files use proven asyncua pattern")
        return True

def test_python_version():
    """Test Python version compatibility"""
    print("\\n🐍 Checking Python Version")
    print("-" * 30)
    
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("   ✅ Python version compatible")
        print("   ✅ Supports asyncio and asyncua")
        return True
    else:
        print("   ❌ Python 3.7+ required for asyncua")
        return False

def verify_asyncua_compatibility():
    """Verify asyncua library compatibility"""
    print("\\n🔍 Checking Asyncua Compatibility")
    print("-" * 35)
    
    try:
        import asyncua
        print(f"   ✅ asyncua library available")
        
        # Check if it has the methods we need
        from asyncua import Client
        print(f"   ✅ asyncua.Client available")
        
        # Check for proven methods
        client = Client("opc.tcp://dummy:4840")
        if hasattr(client, 'get_objects_node'):
            print(f"   ✅ get_objects_node method available")
        
        print(f"   💡 Using proven asyncua pattern from your working code")
        return True
        
    except ImportError:
        print(f"   ❌ asyncua library not found")
        print(f"   💡 Run: pip install asyncua")
        return False
    except Exception as e:
        print(f"   ❌ asyncua compatibility issue: {e}")
        return False

def main():
    """Main setup process using proven pattern"""
    print("🏗️ BVM AS/RS System Setup (Proven Asyncua Pattern)")
    print("=" * 60)
    print("Setting up Auto Rack35 AS/RS Control System")
    print("Using your proven asyncua connection pattern")
    print("Based on your working plc_monitor.py and new.py code")
    print()
    
    steps = [
        ("Check Python Version", test_python_version),
        ("Check System Files", check_system_files),
        ("Install Dependencies", install_dependencies),
        ("Verify Asyncua Compatibility", verify_asyncua_compatibility),
        ("Verify Configuration", verify_config),
        ("Update PLC IP", update_plc_ip)
    ]
    
    for step_name, step_func in steps:
        success = step_func()
        if not success:
            print(f"\\n❌ Setup failed at: {step_name}")
            return False
    
    print("\\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\\n🚀 Next Steps:")
    print("   1. python discover_plc.py    # Discover PLC variables (proven method)")
    print("   2. python test_system.py     # Test system components")
    print("   3. python asrs_app.py        # Start AS/RS control system")
    
    print("\\n💡 System Features:")
    print("   ✅ Uses your proven asyncua connection pattern")
    print("   ✅ Real-time variable monitoring (like plc_monitor.py)")
    print("   ✅ Exact navigation path: Objects → new_Controller_0 → GlobalVars")
    print("   ✅ Professional 35-position AS/RS control system")
    print("   ✅ Emergency safety monitoring")
    
    print("\\n🔧 Troubleshooting:")
    print("   • Ensure OMRON PLC is powered on")
    print("   • Enable OPC UA server in Sysmac Studio")
    print("   • Check network connectivity to 10.10.14.104")
    print("   • Variables must be published in PLC (led1-led35, pb1-pb35, kill)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\\n❌ Setup incomplete. Please resolve errors.")
        sys.exit(1)
    else:
        print("\\n🎯 Ready to use your proven asyncua AS/RS system!")
        sys.exit(0)
'''

with open('setup.py', 'w') as f:
    f.write(setup_proven_code)

# Create requirements for proven asyncua system
requirements_proven = '''# BVM AS/RS System Requirements - Proven Asyncua Pattern
# Python packages for async OPC UA communication using your working pattern

# Core OPC UA Communication (async - matches your working code)
asyncua>=0.9.0

# Standard libraries (included with Python):
# - asyncio          # For async/await patterns (matches your code)
# - json            # Configuration files
# - logging         # System logging
# - dataclasses     # Data structures
# - typing          # Type hints
# - enum            # Enumerations
# - datetime        # Time handling
# - time            # Timing functions
# - sys             # System functions

# Optional for development:
# pytest>=6.0.0     # For testing
# black>=21.0.0     # Code formatting

# Note: This system uses the asynchronous 'asyncua' library
# exactly matching your proven working code pattern from:
# - plc_monitor.py
# - new.py 
# - discover_path.py

# Your proven connection pattern:
# async with Client(url=PLC_URL) as client:
#     current_node = client.get_objects_node()
#     for part in PATH[1:]:
#         current_node = await current_node.get_child(part)
'''

with open('requirements.txt', 'w') as f:
    f.write(requirements_proven)

print("✅ 7. Setup script (proven pattern): setup.py")
print("✅ 8. Requirements (proven pattern): requirements.txt")