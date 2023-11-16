import asyncio
import os

import yaml
from loguru import logger

from src.main import Parser
from database import initialize_database, OffendersData


async def run() -> None:
    if os.path.exists(os.path.join(os.getcwd(), "settings.yaml")):
        with open('settings.yaml') as f:
            config = yaml.safe_load(f)

        if not config.get("two_captcha_api_key", "") or not config.get("max_iterations", ""):
            logger.error("Please fill settings.yaml file")
            input("Press any key to exit")
            exit(0)

    else:
        logger.error("File settings.yaml not found")

    await initialize_database()
    await OffendersData().all().delete()

    client = Parser(config)
    await client.start()




if __name__ == '__main__':
    asyncio.run(run())





