#!/usr/bin/env python3
"""
Quick setup script for PostgreSQL connection
Run this after installing Python dependencies
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from .env.example"""
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    env_file = project_root / ".env"
    env_example = project_root / "config" / ".env.example"

    if env_file.exists():
        print(f"✅ .env file already exists at {env_file}")
        return

    if env_example.exists():
        with open(env_example, "r") as f:
            content = f.read()
        with open(env_file, "w") as f:
            f.write(content)
        print(f"✅ Created .env file from template")
        print(f"   📍 Location: {env_file}")
        print(f"   ⚠️  Update credentials in .env file!")
    else:
        print(f"❌ .env.example not found at {env_example}")
        sys.exit(1)


def check_postgres_installed():
    """Check if PostgreSQL client tools are available"""
    import shutil
    
    psql_exists = shutil.which("psql") is not None
    pg_isready_exists = shutil.which("pg_isready") is not None

    print("\n📦 PostgreSQL Installation Check:")
    print(f"   psql command: {'✅ Found' if psql_exists else '❌ Not found'}")
    print(f"   pg_isready:   {'✅ Found' if pg_isready_exists else '❌ Not found'}")

    if not psql_exists:
        print("\n⚠️  PostgreSQL client tools not found in PATH")
        print("   Please install PostgreSQL: https://www.postgresql.org/download/")


def print_next_steps():
    """Print next steps for user"""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Update PostgreSQL Credentials:
   - Edit: backend/.env
   - Update DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

2. Ensure PostgreSQL is Running:
   Windows:  Check Windows Services or run: Get-Service PostgreSQL*
   macOS:    brew services start postgresql@15
   Linux:    sudo systemctl start postgresql

3. Create the Database:
   psql -U postgres -c 'CREATE DATABASE expense_tracker;'

4. Test the Connection:
   cd backend
   python test_db_connection.py

5. Start the Backend Server:
   python main.py

6. Verify via API:
   curl http://localhost:8000/health
   curl http://localhost:8000/health/db
    """)
    print("="*70)


def main():
    """Run setup"""
    print("\n" + "🚀 "*35)
    print("EXPENSE TRACKER - DATABASE SETUP")
    print("🚀 "*35 + "\n")

    create_env_file()
    check_postgres_installed()
    print_next_steps()


if __name__ == "__main__":
    main()
