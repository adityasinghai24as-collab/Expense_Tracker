"""
Database connection testing script
Run this to verify PostgreSQL connectivity
"""
import asyncio
import sys
from app.database import check_db_connection_sync, check_db_connection, DB_HOST, DB_PORT, DB_NAME, DB_USER


def test_sync_connection():
    """Test synchronous connection"""
    print("\n" + "="*60)
    print("🔍 Testing SYNCHRONOUS PostgreSQL Connection")
    print("="*60)
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print("-"*60)
    
    is_connected, message = check_db_connection_sync()
    if is_connected:
        print("✅ SUCCESS: Synchronous connection established!")
        print(f"   Message: {message}")
        return True
    else:
        print("❌ FAILED: Could not connect to database")
        print(f"   Error: {message}")
        return False


async def test_async_connection():
    """Test asynchronous connection"""
    print("\n" + "="*60)
    print("🔍 Testing ASYNCHRONOUS PostgreSQL Connection")
    print("="*60)
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print("-"*60)
    
    is_connected, message = await check_db_connection()
    if is_connected:
        print("✅ SUCCESS: Asynchronous connection established!")
        print(f"   Message: {message}")
        return True
    else:
        print("❌ FAILED: Could not connect to database")
        print(f"   Error: {message}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀 "*30)
    print("DATABASE CONNECTION TEST SUITE")
    print("🚀 "*30)
    
    sync_ok = test_sync_connection()
    async_ok = await test_async_connection()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Synchronous: {'✅ PASS' if sync_ok else '❌ FAIL'}")
    print(f"Asynchronous: {'✅ PASS' if async_ok else '❌ FAIL'}")
    print("="*60)
    
    if sync_ok and async_ok:
        print("\n✅ All tests passed! Database is ready to use.\n")
        return 0
    else:
        print("\n❌ Some tests failed. Please check your PostgreSQL setup.\n")
        print("Troubleshooting tips:")
        print("1. Ensure PostgreSQL is running:")
        print("   - Windows: Check Services or run 'pg_isready'")
        print("   - macOS: brew services list | grep postgres")
        print("   - Linux: sudo systemctl status postgresql")
        print("\n2. Verify credentials in .env file match your PostgreSQL user")
        print("\n3. Create the database if it doesn't exist:")
        print("   psql -U postgres -c 'CREATE DATABASE expense_tracker;'")
        print("\n4. Test connection manually:")
        print(f"   psql -h {DB_HOST} -U {DB_USER} -d {DB_NAME}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
