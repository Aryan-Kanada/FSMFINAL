# BVM Physical AS/RS Control System

## Overview
Complete integration with your Sysmac Studio PLC program for physical AS/RS control.

## Files
- `asrs_config_actual.json` - PLC configuration
- `asrs_core_actual.py` - Core system using actual PLC variables
- `asrs_app_physical.py` - Main application
- `test_physical_connection.py` - Connection test

## Your PLC Variables
- **LEDs**: ledA1, ledA2...ledE7 (35 positions)
- **Buttons**: A1, A2...E7 (35 positions) 
- **Motion**: X_write_position, Y_write_position, Z_write_position
- **Control**: Start_1, Start_2, Start_3

## Quick Start
1. Test connection: `python test_physical_connection.py`
2. Run system: `python asrs_app_physical.py`

## Features
- Physical crane control
- Store/retrieve operations
- LED control
- Button monitoring
- Inventory tracking
- Real-time status

## Commands
- **S** - Store item physically
- **R** - Retrieve item physically  
- **G** - Show grid
- **T** - System status
