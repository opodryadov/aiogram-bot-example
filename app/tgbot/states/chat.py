from aiogram.fsm.state import State, StatesGroup


class AddChat(StatesGroup):
    chat_id = State()
    chat_title = State()
    phone = State()
    email = State()
    commentary = State()
    access_until = State()
    confirm = State()
    result = State()


class EditChat(StatesGroup):
    select_chat = State()
    select_field = State()
    result = State()


class DeleteChat(StatesGroup):
    select_chat = State()
    confirm = State()
    result = State()
