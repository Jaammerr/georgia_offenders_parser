import asyncio
import httpx

from loguru import logger





class Captcha(httpx.AsyncClient):
    def __init__(self, api_key: str, image_data: str):
        super().__init__()
        self.api_key: str = api_key
        self.task_id: int = 0
        self.image_data: str = image_data



    async def create_task(self) -> None:
        """Create captcha solving task"""
        url = "https://api.2captcha.com/createTask"

        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": self.image_data,
                "case": True,
                "minLength": 4,
                "maxLength": 7,
            }
        }

        while True:

            try:
                response = await self.post(url, json=data)
                response.raise_for_status()

                self.task_id = response.json()["taskId"]
                logger.info(f"Created captcha task with id: {self.task_id}")
                return

            except Exception as error:
                logger.error(f"Error while creating captcha task: {error}")
                await asyncio.sleep(3)


    async def get_task_result(self) -> str or bool:
        """Get task result"""
        url = "https://api.2captcha.com/getTaskResult"

        data = {
            "clientKey": self.api_key,
            "taskId": self.task_id
        }

        logger.info("Waiting for captcha result..")
        while True:
            try:
                response = await self.post(url, json=data)

                json_data = response.json()
                if int(json_data["errorId"]) == 0:

                    if json_data["status"] == "ready":
                        logger.info("Got captcha result")
                        solution = json_data["solution"]["text"]
                        logger.info(f"Captcha solution: {solution}")
                        return solution

                    else:
                        await asyncio.sleep(3)

                else:
                    logger.error(f"Error while getting captcha result: {json_data['errorDescription']}")
                    return False

            except Exception as error:
                logger.error(f"Error while getting captcha result: {error}")
                return False



    async def solve(self):
        """Solve captcha"""

        await self.create_task()
        result = await self.get_task_result()

        if not result:
            await self.solve()

        else:
            return result
