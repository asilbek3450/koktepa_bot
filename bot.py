import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, ADMINS
from functions import check_is_admin
from keyboards import start_keyboards, admin_start_keyboards, contact
from database import create_db, user_in_database, add_data_to_users, \
                        hozirgi_userni_olish, add_data_to_category, get_all_categories
from state import RegisterState, CategoryState
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

# pip install aiogram==2.25.1

@dp.message_handler(commands=['start'])
async def salom_ber(message: types.Message):
    create_db()
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer(f"👑 ADMIN akkountga xush kelibsiz!", reply_markup=admin_start_keyboards)
    else:
        if user_in_database(id=message.from_user.id):
            user = hozirgi_userni_olish(user_id=message.from_user.id)  # tuple
            await message.answer(text=f"👤 Assalomu aleykum, xush kelibsiz {user.get('name')}!", reply_markup=start_keyboards)
        else:
            await message.answer(text="👤 Assalomu aleykum, ro'yhatdan o'tish kerak /register")
            
@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    await RegisterState.name.set()
    await message.answer("Ismingizni kiriting: ")


@dp.message_handler(state=RegisterState.name)
async def get_name(message: types.Message, state):
    name = message.text
    await RegisterState.next()
    await state.update_data(name=name)
    await message.answer("Telefon raqamingizni kiriting: ", reply_markup=contact)


@dp.message_handler(state=RegisterState.telefon, content_types=types.ContentTypes.CONTACT)
async def get_telefon(message: types.Message, state):
    telefon = message.contact.phone_number
    user_id = message.from_user.id
    await RegisterState.next()
    await state.update_data(telefon=telefon)
    await message.answer("Ro'yhatdan o'tdingiz!")
    data = await state.get_data()
    name, telefon, user_id = data['name'], data['telefon'], user_id
    add_data_to_users(name, telefon, user_id)
    await state.finish()


@dp.message_handler(lambda message: message.text == '🍴 Menu')
async def get_menu(message: types.Message):
    menu_keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
    categories = get_all_categories()
    for kb in categories:
        menu_keyboards.add(types.KeyboardButton(kb['name']))
        
    await message.answer("Menu", reply_markup=menu_keyboards)


@dp.message_handler(lambda message: message.text == 'Category ✏️/➕')
async def add_category(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Category nomini kiriting: ")
        await CategoryState.name.set()


@dp.message_handler(state=CategoryState.name)
async def get_category_name(message: types.Message, state):
    c_name = message.text
    add_data_to_category(c_name)
    await state.finish()
    await message.answer("Category qo'shildi! ✅", reply_markup=admin_start_keyboards)




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
