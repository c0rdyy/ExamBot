from aiogram.fsm.state import State, StatesGroup

class TestState(StatesGroup):
    choosing_difficulty = State()
    answering = State()

class ProfileState(StatesGroup):
    editing_name = State()
    waiting_for_photo = State()