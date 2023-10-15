"""
    This module is used to seed the database with initial data.
    It is called from the Dockerfile as part of the entrypoint.
"""
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa

# make sure all SQL Alchemy models are imported (app.model) before initializing DB # noqa
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28 # noqa
from app.core.config import settings
from app.db import repos
from app.db.session import AsyncSessionFactory, async_engine
from app.schemas import UserInvite

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Seed the database with initial data"""
    echo, async_engine.echo = async_engine.echo, False
    async with AsyncSessionFactory() as session:
        await _seed_super_user(session)
    async_engine.echo = echo


async def _seed_super_user(db: AsyncSession) -> None:
    """Seed super user if not exist"""
    admin_invite = UserInvite(
        email=settings.SUPERUSER_EMAIL,
        is_admin=True,
    )

    try:
        await repos.user.create(db, obj_in=admin_invite)
        await db.commit()
    except Exception:
        logger.info("Super user already exists")

    # TODO: Send an email invitation to the new admin to register his password


async def main() -> None:
    logger.info("--- Seeding DB ---")
    await init_db()
    logger.info("--- DB Seeded ---")


if __name__ == "__main__":
    asyncio.run(main())
