import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    # Docker exposes port 5432 to localhost
    url = "postgresql+asyncpg://admin:supersecret@localhost:5432/expensedb"
    engine = create_async_engine(url)
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, name, icon, user_id FROM categories"))
        rows = result.fetchall()
        print(f"Total categories: {len(rows)}")
        for r in rows:
            print(dict(r._mapping))
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
