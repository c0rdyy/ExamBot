from aiogram.fsm.state import State, StatesGroup

class TestState(StatesGroup):
    choosing_difficulty = State()
    answering = State()