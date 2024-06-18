import abc
import asyncio

import aiormq
from loguru import logger

from app.config import RabbitMQSettings


class BasePublisher(abc.ABC):
    def __init__(self, config: RabbitMQSettings):
        super().__init__()
        self._config = config
        self._connection: aiormq.Connection = None  # type: ignore
        self._channel: aiormq.Channel = None  # type: ignore

    async def _connect(self) -> None:
        try_num = 0

        while True:
            try:
                self._connection = await aiormq.connect(url=self._config.url)
                break
            except aiormq.exceptions.ConnectionClosed:
                logger.warning("AIORMQ ConnectionClosed, will call on_error")
            except OSError:
                logger.error(
                    "Cannot connect AIORMQ to AMQP. Try connect %s after %s sec",
                    try_num + 1,
                    self._config.reconnect_delay,
                )

            await asyncio.sleep(self._config.reconnect_delay)
            try_num += 1

    async def _shutdown(self) -> None:
        if self._connection is not None:
            try:
                await self._connection.close()
            except aiormq.exceptions.ConnectionClosed:
                pass

        self._connection = None

    @abc.abstractmethod
    async def send(self, *args) -> None:
        pass
