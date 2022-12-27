import asyncio
from typing import Optional, Tuple, List, Dict
import logging

import aiohttp

from .dataclasses import Settings, Queues, MQTTPublisherData

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, mqtt_service_host: str, mqtt_service_token: str, worker_count: int = 5):
        self.settings = Settings(
            mqtt_service_host=mqtt_service_host, mqtt_service_token=mqtt_service_token, worker_count=worker_count
        )
        self.queues = Queues(
            mqtt_message=asyncio.Queue()
        )
        self.headers = {'token': mqtt_service_token, 'Content-Type': 'application/json'}
        self.aio_session = aiohttp.ClientSession()
        self.__tasks = []
        for i in range(self.settings.worker_count):
            self.__tasks.append(asyncio.create_task(self.__task(name=f"Worker num: {i}")))
        self.kwgs = {'ssl': False} if aiohttp.__version__ >= '3.8.0' else {'verify_ssl': False}

    @staticmethod
    def __prepare_data(payload: dict, topics: List[str] = None) -> Dict:
        out = {'data': []}
        for _t in topics:
            out['data'].append({'topic': _t, 'payload': payload or {}})
        return out

    async def __send(self, data: dict) -> Tuple[dict, int]:
        async with self.aio_session.post(f'{self.settings.mqtt_service_host}/api/v1/publisher/publish_message/',
                                         headers=self.headers, json=data, **self.kwgs) as resp:
            if resp.status == 200:
                out = await resp.json()
            else:
                print(f'MQTT PUBLISHER GET INCORRECT RESPONSE: {resp.status}')

        return out, resp.status

    async def __task(self, name: str):
        queue = self.queues.mqtt_message
        while True:
            data: Optional[MQTTPublisherData] = await queue.get()
            if not data:
                logger.info(f"Task {name} was done!")
                return
            try:
                resp, status = await self.__send(data=data.data)
                if status != 200:
                    logger.error(f"Problem send mqtt data. Status {status}")
            except Exception as e:
                logger.exception(e)

    async def publish_message(self, payload: dict, topic: Optional[str] = None, topics: Optional[list] = None):
        data = self.__prepare_data(payload=payload, topics=[*topics, topic])
        await self.queues.mqtt_message.put(MQTTPublisherData(data=data))

    async def publish_force(self, payload: dict, topic: Optional[str] = None, topics: Optional[list] = None):
        data = self.__prepare_data(payload=payload, topics=[*topics, topic])
        try:
            resp, status = await self.__send(data=data)
        except Exception as e:
            logger.exception(e)
            resp, status = {}, None
        return resp, status

    async def close(self):
        async def check_shutdown_tasks(tasks: List[asyncio.Task]):
            for task in tasks:
                if not task.done():
                    await asyncio.sleep(2)
                    await check_shutdown_tasks(tasks=[task])
            return

        for i in range(self.settings.worker_count):
            await self.queues.mqtt_message.put(None)

        await check_shutdown_tasks(tasks=self.__tasks)
