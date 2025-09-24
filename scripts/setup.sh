#!/bin/bash

# Manhattan Power Grid - Linux/macOS Setup Script
# Automated setup for Unix-like environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================================"
echo -e "${GREEN}Manhattan Power Grid - Setup${NC}"
echo "======================================================"

# Function to print colored output
print_status() {
    local level=$1
    local message=$2
    case $level in
        "info")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "success")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "warning")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "error")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Check if Python is installed
print_status "info" "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_status "error" "Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "success" "Python $PYTHON_VERSION found"

# Check Python version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    print_status "error" "Python 3.8+ required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if we're in the project directory
if [ ! -f "main_complete_integration.py" ]; then
    print_status "error" "Please run this script from the project root directory"
    exit 1
fi

# Make the setup script executable
chmod +x scripts/setup.py

# Run the Python setup script
print_status "info" "Running setup script..."
python3 scripts/setup.py

# Check if setup was successful
if [ $? -eq 0 ]; then
    print_status "success" "Setup completed successfully!"
    echo ""
    echo "To start the application:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo "2. Run the application:"
    echo "   python main_complete_integration.py"
    echo "3. Open your browser to:"
    echo "   http://localhost:5000"
    echo ""
else
    print_status "error" "Setup failed"
    exit 1
fi