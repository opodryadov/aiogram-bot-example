import orjson
from aiormq.abc import DeliveredMessage
from loguru import logger

from app.config import config
from app.infrastructure.rabbitmq.base.consumer import BaseConsumer
from app.tgbot.dispatcher import bot


class TelegramConsumer(BaseConsumer):
    async def _on_message(self, message: DeliveredMessage) -> None:
        from_user = message.header.properties.headers
        message_text = orjson.loads(message.body)

        try:
            await bot.send_message(
                chat_id=from_user.get("chat_id", None), text=message_text
            )
            await message.channel.basic_ack(
                delivery_tag=message.delivery.delivery_tag
            )
            logger.info(
                "Answer for message %s sent to Telegram"
                % from_user.get("message_id", None),
            )
        except Exception as exc:
            logger.error("Failed to process message: %s" % exc)
            await message.channel.basic_nack(
                delivery_tag=message.delivery.delivery_tag, requeue=True
            )


telegram_consumer = TelegramConsumer(config=config.telegram_queue)
