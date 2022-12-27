from dataclasses import dataclass
from asyncio import Queue
from typing import Optional, List

import aiohttp

from .choices import Priorities


@dataclass
class Settings:
    mqtt_service_host: str
    mqtt_service_token: str
    worker_count: int


@dataclass
class Queues:
    mqtt_message: Queue


@dataclass
class MQTTPublisherData:
    data: dict
