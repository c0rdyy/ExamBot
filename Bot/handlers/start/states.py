from aiogram.fsm.state import State, StatesGroup

class TestState(StatesGroup):
    choosing_difficulty = State()
    answering = State()

class ProfileState(StatesGroup):
    viewing = State()
    choosing_edit_option = State()
    editing_name = State()
    editing_photo = State()
    choosing_photo_action = State() 