from app.infrastructure.database.exceptions import AppException


class ChatException(AppException):
    """Base Chat Exception"""


class ChatIdAlreadyExists(ChatException):
    """Chat ID already exists"""


class DataDuplicationError(ChatException):
    """Chat ID or phone or email already exists"""
