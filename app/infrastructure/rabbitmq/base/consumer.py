import abc
import asyncio

import aiormq
from loguru import logger

from app.config import RabbitMQSettings


class BaseConsumer(abc.ABC):
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
                self._channel = await self._connection.channel()
                await self._channel.exchange_declare(
                    exchange=self._config.exchange_name,
                    exchange_type=self._config.exchange_type,
                )
                await self._channel.queue_declare(
                    queue=self._config.queue_name,
                )
                await self._channel.queue_bind(
                    queue=self._config.queue_name,
                    exchange=self._config.exchange_name,
                    routing_key=self._config.queue_name,
                )
                await self._channel.basic_qos(
                    prefetch_count=self._config.prefetch_count
                )
                logger.info(
                    "%s connection is established." % self.__class__.__name__
                )
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

    async def shutdown(self) -> None:
        if self._connection is not None:
            try:
                await self._connection.close()
            except aiormq.exceptions.ConnectionClosed:
                pass

        if self._channel is not None:
            try:
                await self._channel.close()
            except aiormq.exceptions.ChannelClosed:
                pass

        self._channel, self._connection = None, None

        logger.info("%s connection is closed." % self.__class__.__name__)

    async def consume(self) -> None:
        if self._connection is None or self._channel is None:
            await self._connect()

        await self._channel.basic_consume(
            queue=self._config.queue_name,
            consumer_callback=self._on_message,
            no_ack=False,
        )

    @abc.abstractmethod
    async def _on_message(self, message: aiormq.abc.DeliveredMessage) -> None:
        pass
