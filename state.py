from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    name = State()
    telefon = State()
    user_id = State()



class CategoryState(StatesGroup):
    name = State()
    