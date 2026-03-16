#!/bin/bash
# TVP-RBE-SIMULATION-PLATFORM Installation Script
# Resource-Based Economy TVP Simulation Platform
# https://github.com/urmt/TVP-RBE-SIMULATION-PLATFORM

set -e

echo "=========================================="
echo "TVP-RBE-SIMULATION-PLATFORM Installer"
echo "Resource-Based Economy Simulation Platform"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "[1/6] Checking Python version..."
PYTHON_VERSION=$(/usr/bin/python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ -z "$PYTHON_VERSION" ]; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Version comparison
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $PYTHON_VERSION is too old. Python $REQUIRED_VERSION+ required.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Check for pip
echo ""
echo "[2/6] Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Warning: pip3 not found. Attempting to install...${NC}"
    /usr/bin/python3 -m ensurepip --upgrade 2>/dev/null || {
        echo -e "${RED}Error: Could not install pip. Please install manually.${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✓ pip is available${NC}"

# Create virtual environment
echo ""
echo "[3/6] Setting up virtual environment..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
else
    /usr/bin/python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "[4/6] Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo ""
echo "[5/6] Installing dependencies..."

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'REQEOF'
# TVP-RBE-SIMULATION-PLATFORM Dependencies
# Core dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0

# Optional UI dependencies (for web interface)
streamlit>=1.28.0

# Data processing
numpy>=1.24.0

# Networking (for P2P)
asyncio-mqtt>=0.16.0
REQEOF
    echo -e "${GREEN}✓ Created requirements.txt${NC}"
fi

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Initialize databases
echo ""
echo "[6/6] Initializing databases..."

/usr/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from tracker.database import ResourceDatabase
from hub.cybernation_hub import CybernationHub

# Initialize resource database
db = ResourceDatabase("rbe_resources.db")
print("✓ Resource database initialized")

# Initialize cybernation hub tables
hub = CybernationHub("rbe_resources.db")
print("✓ Cybernation hub tables initialized")

# Add sample resources if none exist
resources = db.get_all_resources()
if not resources:
    db.add_resource("energy-001", "Solar Array Alpha", "ENERGY", "kWh", 10000.0)
    db.add_resource("energy-002", "Wind Farm Beta", "ENERGY", "kWh", 15000.0)
    db.add_resource("water-001", "Central Reservoir", "WATER", "m³", 50000.0)
    db.add_resource("water-002", "Treatment Plant", "WATER", "m³", 20000.0)
    db.add_resource("material-001", "Steel Stock", "MATERIAL", "kg", 5000.0)
    db.add_resource("material-002", "Component Storage", "MATERIAL", "unit", 1000.0)
    print("✓ Sample resources added")
else:
    print(f"✓ {len(resources)} existing resources found")

print("\nDatabase initialization complete!")
PYEOF

echo ""
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  /usr/bin/python3 -m pytest tests/ -v"
echo ""
echo "To use the CLI:"
echo "  /usr/bin/python3 -m tracker.cli --help"
echo ""
echo "To start the UI (if streamlit is installed):"
echo "  streamlit run ui/main.py"
echo ""
echo "Project: TVP-RBE-SIMULATION-PLATFORM"
echo "GitHub: https://github.com/urmt/TVP-RBE-SIMULATION-PLATFORM"
echo ""
