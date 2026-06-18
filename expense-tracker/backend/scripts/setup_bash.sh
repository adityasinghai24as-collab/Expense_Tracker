#!/bin/bash
# Bash Setup Script for macOS/Linux
# Run: bash setup_bash.sh

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  EXPENSE TRACKER - PostgreSQL Setup (macOS/Linux)      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS:   brew install postgresql@15"
    echo "  Linux:   sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

echo "✅ PostgreSQL found: $(psql --version)"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting it..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@15
    else
        sudo systemctl start postgresql
    fi
    sleep 2
fi

echo "✅ PostgreSQL is running"
echo ""

# Resolve base directory (repo backend folder)
base_dir="$(cd "$(dirname "$0")/.." && pwd)"

# Create .env file from template (config/.env.example)
if [ ! -f "$base_dir/.env" ]; then
    if [ -f "$base_dir/config/.env.example" ]; then
        cp "$base_dir/config/.env.example" "$base_dir/.env"
        echo "✅ Created .env from template"
        echo "⚠️  Update credentials in $base_dir/.env (open with editor)"
    else
        echo "❌ $base_dir/config/.env.example not found"
        exit 1
    fi
else
    echo "✅ .env already exists at $base_dir/.env"
fi

echo ""

# Read database configuration from .env
export $(cat .env | grep -v '^#' | xargs)

# Create database if it doesn't exist
echo "📍 Creating database: $DB_NAME"
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME;"
echo "✅ Database ready: $DB_NAME"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  NEXT STEPS                                            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "1. Edit your credentials:"
echo "   nano .env"
echo ""
echo "2. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Test database connection:"
echo "   python test_db_connection.py"
echo ""
echo "4. Start the backend server:"
echo "   python main.py"
echo ""
echo "5. In another terminal, verify:"
echo "   curl http://localhost:8000/health/db"
echo ""
