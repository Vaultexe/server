"""
Sets up postgresql database connection pool.
"""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(
    url=str(settings.DATABASE_DSN),
    echo=settings.is_dev,
    future=True,
    pool_pre_ping=True,
    pool_size=50,  # pgbouncer pool size = 50
    pool_timeout=100,  # pgbouncer pool timeout = 100
)

AsyncSessionFactory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
