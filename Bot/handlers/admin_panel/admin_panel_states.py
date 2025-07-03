from aiogram.fsm.state import StatesGroup, State

class AddQuestionState(StatesGroup):
    text = State()
    options = State()
    correct_index = State()
    difficulty = State()

class AdminPanelState(StatesGroup):
    active = State()