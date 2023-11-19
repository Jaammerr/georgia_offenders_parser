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

        if not config.get("two_captcha_api_key", "") or not config.get("threads", "") or not isinstance(config.get("threads", ""), int):
            logger.error("Please fill settings.yaml file")
            input("Press any key to exit")
            exit(0)

    else:
        logger.error("File settings.yaml not found")
        input("Press any key to exit")
        exit(0)

    await initialize_database()
    await OffendersData().all().delete()

    tasks = [asyncio.create_task(Parser(config, thread_id + 1).start_with_browser()) for thread_id in range(config.get("threads"))]
    await asyncio.gather(*tasks, return_exceptions=True)




if __name__ == '__main__':
    asyncio.run(run())





