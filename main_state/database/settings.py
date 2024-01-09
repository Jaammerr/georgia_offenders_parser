from loguru import logger
from tortoise import Tortoise


async def initialize_database() -> None:
    try:
        await Tortoise.init(
            db_url="sqlite://database/db.sqlite3",
            modules={
                "models": [
                    "database.models.offenders",
                ]
            },
            timezone="Europe/Moscow",
        )

        await Tortoise.generate_schemas()

    except Exception as error:
        logger.error(f"Error while initializing database: {error}")
        input("Press any key to exit")
        exit(0)




