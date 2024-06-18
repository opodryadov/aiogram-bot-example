import aiormq
import orjson
from loguru import logger

from app.config import config
from app.infrastructure.rabbitmq.base.publisher import BasePublisher


class TelegramPublisher(BasePublisher):
    async def send(self, body: str, headers: dict) -> None:
        if self._connection is None:
            await self._connect()

        self._channel = await self._connection.channel()
        await self._channel.exchange_declare(
            exchange=self._config.exchange_name,
            exchange_type=self._config.exchange_type,
        )

        await self._channel.basic_publish(
            body=orjson.dumps(body),
            exchange=self._config.exchange_name,
            routing_key=self._config.queue_name,
            properties=aiormq.spec.Basic.Properties(headers=headers),
        )
        await self._shutdown()

        logger.info("Received message: %s" % headers)


telegram_publisher = TelegramPublisher(config=config.telegram_queue)
