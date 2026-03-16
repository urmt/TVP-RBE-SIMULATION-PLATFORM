#!/bin/bash
# TVP-RBE-SIMULATION-PLATFORM Installation Script
# Automates environment setup, dependency installation, and database initialization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="TVP-RBE-SIMULATION-PLATFORM"
DB_FILE="rbe_resources.db"

echo "=========================================="
echo "  $PROJECT_NAME Installer"
echo "=========================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
if command -v /usr/bin/python3 &> /dev/null; then
    PYTHON_VERSION=$(/usr/bin/python3 --version 2>&1 | awk '{print $2}')
    echo "  Found Python $PYTHON_VERSION"
else
    echo "  ERROR: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/5] Setting up virtual environment..."
VENV_DIR="$SCRIPT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment already exists"
else
    /usr/bin/python3 -m venv "$VENV_DIR"
    echo "  Created virtual environment at $VENV_DIR"
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo ""
echo "[3/5] Installing Python dependencies..."

# Install from requirements files
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "  Installed from requirements.txt"
fi

if [ -f "$SCRIPT_DIR/requirements-p2p.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/requirements-p2p.txt"
    echo "  Installed from requirements-p2p.txt"
fi

echo "  Core dependencies installed"

# Initialize database
echo ""
echo "[4/5] Initializing SQLite database..."
DB_PATH="$SCRIPT_DIR/$DB_FILE"

cd "$SCRIPT_DIR"
/usr/bin/python3 << 'PYEOF'
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rbe_resources.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create resources table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        resource_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        unit TEXT NOT NULL,
        current_quantity REAL NOT NULL DEFAULT 0.0,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create allocations table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id TEXT NOT NULL,
        allocated_quantity REAL NOT NULL,
        allocated_to TEXT,
        purpose TEXT,
        allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
    )
""")

# Create feeds table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS feeds (
        feed_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        source_type TEXT NOT NULL,
        config TEXT,
        is_active BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create history table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id TEXT NOT NULL,
        quantity REAL NOT NULL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
    )
""")

# Create hub_decisions table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS hub_decisions (
        decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id TEXT NOT NULL,
        requested_amount REAL NOT NULL,
        approved_amount REAL NOT NULL,
        priority TEXT NOT NULL,
        sustainability_score REAL,
        equity_score REAL,
        decision_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create scarcity_scenarios table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scarcity_scenarios (
        scenario_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        resource_constraints TEXT,
        active BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print("Database initialized successfully")
PYEOF

echo "  Database initialized at $DB_PATH"

# Run tests
echo ""
echo "[5/5] Running integration tests..."
cd "$SCRIPT_DIR"
/usr/bin/python3 -m pytest tests/ -q --tb=short 2>&1 | tail -20

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Project Location: $SCRIPT_DIR"
echo "Database: $DB_PATH"
echo "Virtual Environment: $VENV_DIR"
echo ""
echo "Quick Start:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run CLI: /usr/bin/python3 -m tracker.cli --help"
echo "  3. Run tests: /usr/bin/python3 -m pytest tests/"
echo ""
echo "For P2P mode:"
echo "  /usr/bin/python3 -m rbe.p2p.network"
echo ""
