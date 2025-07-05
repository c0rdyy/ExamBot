from aiogram.fsm.state import StatesGroup, State

class AddQuestionState(StatesGroup):
    text = State()
    options = State()
    correct_index = State()
    difficulty = State()

class AdminPanelState(StatesGroup):
    active = State()
    viewing_questions = State()
    viewing_users = State()

class EditQuestionState(StatesGroup):
    choosing_field = State()
    editing_text = State()
    editing_options = State()
    editing_correct_index = State()
    editing_difficulty = State()