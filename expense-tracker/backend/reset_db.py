import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base, ASYNC_DATABASE_URL
import app.models  # Ensure models are loaded

async def reset():
    engine = create_async_engine(ASYNC_DATABASE_URL)
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(reset())
