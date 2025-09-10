#!/bin/bash

# Inventory Reports Generator Setup and Startup Script
echo "🏗️  Inventory Reports Generator Setup"
echo "======================================"

# Check if we're in the reports directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: This script must be run from the reports directory"
    echo "   Please run: cd /path/to/inventory-system/reports && ./startup.sh"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Node.js installation
echo "1️⃣ Checking Node.js installation..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js found: $NODE_VERSION"
else
    echo "   ❌ Node.js not found. Please install Node.js first."
    exit 1
fi

# Check npm installation
echo "2️⃣ Checking npm installation..."
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "   ✅ npm found: $NPM_VERSION"
else
    echo "   ❌ npm not found. Please install npm first."
    exit 1
fi

# Install dependencies
echo "3️⃣ Installing dependencies..."
if npm install; then
    echo "   ✅ Dependencies installed successfully"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi

# Create output directories
echo "4️⃣ Creating output directories..."
mkdir -p output/csv output/pdf templates
echo "   ✅ Output directories created"

# Check database connectivity
echo "5️⃣ Testing database connection..."
if node -e "
const { testConnection } = require('./config/db');
testConnection().then(() => {
    console.log('   ✅ Database connection successful');
    process.exit(0);
}).catch((error) => {
    console.log('   ❌ Database connection failed:', error.message);
    process.exit(1);
});
"; then
    echo "   ✅ Database is accessible"
else
    echo "   ❌ Database connection failed. Please check:"
    echo "      • Backend database is running"
    echo "      • Database credentials are correct"
    echo "      • Network connectivity to database"
    exit 1
fi

# Run demo
echo "6️⃣ Running demonstration..."
if npm run demo; then
    echo "   ✅ Demo completed successfully"
else
    echo "   ⚠️  Demo failed, but setup may still be valid"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Available commands:"
echo "   npm start              - Start the API server"
echo "   npm run dev            - Start with auto-reload (development)"
echo "   npm run demo           - Run demonstration"
echo "   npm run cli help       - Show CLI help"
echo "   npm run generate:daily - Generate daily report"
echo "   npm run generate:all   - Generate all reports"
echo ""
echo "🌐 When server is running:"
echo "   API Server: http://localhost:3002"
echo "   Health Check: http://localhost:3002/health"
echo "   Reports List: http://localhost:3002/api/reports/list"
echo ""
echo "📁 Output files will be saved to:"
echo "   CSV: ./output/csv/"
echo "   PDF: ./output/pdf/"
echo ""

# Ask if user wants to start the server
echo "🚀 Would you like to start the API server now? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Starting API server..."
    npm start
else
    echo "✅ Setup complete. Run 'npm start' when ready to begin."
fi
