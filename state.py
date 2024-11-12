from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    name = State()
    telefon = State()
    user_id = State()



class CategoryState(StatesGroup):
    name = State()


class DelCategoryState(StatesGroup):
    name = State()
    

class ProductState(StatesGroup):
    category_id = State()
    name = State()
    price = State()
    image = State()

