import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Convert postgresql:// to postgresql+asyncpg:// for async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Clean up query params not supported by asyncpg
import re
# Remove channel_binding (not supported by asyncpg)
DATABASE_URL = re.sub(r"[&?]channel_binding=[^&]*", "", DATABASE_URL)
# Replace sslmode with ssl (asyncpg uses 'ssl' not 'sslmode')
DATABASE_URL = re.sub(r"sslmode=require", "ssl=require", DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session
