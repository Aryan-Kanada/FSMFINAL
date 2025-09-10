#!/bin/bash
# ASRS Integration Service Installation Script

echo "🚀 Installing ASRS Integration Service..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv asrs_env
source asrs_env/bin/activate

# Install required packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install mysql-connector-python opcua python-dotenv

# Create configuration file
echo "⚙️ Creating configuration files..."
cp .env.template .env
echo "✏️ Please edit .env file with your database credentials"

# Set permissions
chmod +x start_service.sh
chmod +x stop_service.sh

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run: ./start_service.sh"
echo "3. Test by placing an order on your e-commerce site"
echo ""
echo "🎯 Your ASRS system is now ready for automatic operation!"
