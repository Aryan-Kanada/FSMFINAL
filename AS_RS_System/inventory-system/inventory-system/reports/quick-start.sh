#!/bin/bash

# Inventory Reports System - Quick Setup and Test Script
# Usage: ./quick-start.sh

echo "🚀 Inventory Reports System - Quick Start"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the reports directory."
    exit 1
fi

print_info "Checking system requirements..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'.' -f1 | cut -d'v' -f2)
if [ $NODE_VERSION -lt 16 ]; then
    print_warning "Node.js version is older than 16. Some features may not work correctly."
else
    print_status "Node.js version check passed"
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "System requirements check completed"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_info "Installing dependencies..."
    npm install
    if [ $? -eq 0 ]; then
        print_status "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_status "Dependencies already installed"
fi

# Create output directories
print_info "Creating output directories..."
mkdir -p output/csv
mkdir -p output/pdf
mkdir -p templates
print_status "Output directories created"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status ".env file created from example"
        print_info "Please edit .env file with your database credentials"
    else
        print_warning "No .env.example found. You'll need to create .env manually"
    fi
fi

# Run system tests
print_info "Running system tests..."
node test-reports.js

if [ $? -eq 0 ]; then
    print_status "System tests completed successfully"
    
    echo ""
    echo "🎉 Setup completed! Your Inventory Reports System is ready."
    echo ""
    echo "📚 Available commands:"
    echo "   Start API server:     npm start"
    echo "   Development mode:     npm run dev"
    echo "   Generate all reports: npm run demo"
    echo "   Daily report:         npm run generate:daily"
    echo "   Weekly report:        npm run generate:weekly"
    echo "   Monthly report:       npm run generate:monthly"
    echo ""
    echo "🌐 Usage options:"
    echo "   API endpoints:        http://localhost:3002/api/reports/"
    echo "   Web interface:        open web-interface.html in browser"
    echo "   CLI tool:             node cli.js --help"
    echo ""
    echo "📁 Output location:"
    echo "   CSV files:            ./output/csv/"
    echo "   PDF files:            ./output/pdf/"
    echo ""
    
    # Ask if user wants to start the API server
    read -p "🚀 Would you like to start the API server now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Starting API server..."
        npm start
    else
        print_info "You can start the API server later with: npm start"
    fi
    
else
    print_error "System tests failed. Please check the error messages above."
    echo ""
    echo "🔧 Common issues and solutions:"
    echo "   • Database connection failed: Make sure MySQL is running and credentials are correct in .env"
    echo "   • Permission errors: Make sure you have write permissions in the current directory"
    echo "   • Missing dependencies: Run 'npm install' to install required packages"
    echo "   • Port conflicts: Make sure port 3002 is available for the API server"
    echo ""
    exit 1
fi
