from aiogram.fsm.state import State, StatesGroup


class AdminMenu(StatesGroup):
    action = State()
