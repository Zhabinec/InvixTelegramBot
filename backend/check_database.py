
import asyncio

from sqlalchemy import text

from app.infrastructure.config import DatabaseSettings
from app.infrastructure.database.connection import create_database


async def main() -> None:
    settings = DatabaseSettings()
    engine, session_factory = create_database(settings)

    try:
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            print(f"PostgreSQL response: {result.scalar_one()}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
