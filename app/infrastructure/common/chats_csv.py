import csv
import io

from app.infrastructure.database.models import ChatModel


def export_chats_to_csv(chats: list[ChatModel]) -> bytes:
    output = io.StringIO()
    csv_writer = csv.writer(output, delimiter=";")
    csv_writer.writerow(
        [
            "chat_id",
            "chat_title",
            "chat_type",
            "phone",
            "email",
            "role",
            "commentary",
            "created_at",
            "access_until",
        ]
    )
    for chat in chats:
        csv_writer.writerow(
            [
                chat.chat_id,
                chat.chat_title,
                chat.chat_type,
                chat.phone,
                chat.email,
                chat.role,
                chat.commentary,
                chat.created_at,
                chat.access_until,
            ]
        )
    return output.getvalue().encode("utf-16")
