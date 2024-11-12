import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, ADMINS
from functions import check_is_admin
from keyboards import start_keyboards, admin_start_keyboards, contact, menu_keyboards, product_keyboards_by_category
from database import create_db, user_in_database, add_data_to_users, \
                        hozirgi_userni_olish, add_data_to_category, get_all_categories, get_category_id, delete_category_by_id, \
                        get_all_products, add_data_to_product, get_c_id_by_name, get_product_by_id
from state import RegisterState, CategoryState, ProductState, DelCategoryState
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
    await message.answer("Menu", reply_markup=menu_keyboards())


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


@dp.message_handler(lambda message: message.text == 'Mahsulot ✏️/➕')
async def add_product(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Bu mahsulot qaysi kategoriyada: ", reply_markup=menu_keyboards())
        await ProductState.category_id.set()


@dp.message_handler(state=ProductState.category_id)
async def get_category(message: types.Message, state):
    category = message.text
    c_id = get_c_id_by_name(category)
    await state.update_data(category_id=c_id)
    await message.answer("Mahsulot nomini kiriting: ")
    await ProductState.name.set()
    

@dp.message_handler(state=ProductState.name)
async def get_category_(message: types.Message, state):
    nomi = message.text
    await state.update_data(name=nomi)
    await message.answer("💵 Mahsulot narxini kiriting: ")
    await ProductState.price.set()


@dp.message_handler(state=ProductState.price)
async def get_category_(message: types.Message, state):
    narxi = message.text
    await state.update_data(price=narxi)
    await message.answer("📸 Mahsulot rasmini kiriting: ")
    await ProductState.image.set()
    

@dp.message_handler(state=ProductState.image, content_types=types.ContentType.PHOTO)
async def get_category_(message: types.Message, state):
    rasm = message.photo[-1].file_id
    await state.update_data(image=rasm)
    await message.answer("Mahsulot saqlandi ✅")
    data = await state.get_data()
    add_data_to_product(data.get('category_id'), data.get('name'), data.get('price'), data.get('image'))
    await state.finish()
    

@dp.message_handler(text="Category ochirish ❌")
async def del_category(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.reply("Qaysi kategoriyani o'chirasiz?", reply_markup=menu_keyboards())
        await DelCategoryState.name.set()
    else:
        await message.reply("Siz admin emassiz")


@dp.message_handler(state=DelCategoryState.name)
async def del_category(message: types.Message, state):
    await state.update_data(name=message.text)
    data = await state.get_data()
    category = data.get('name')
    await state.finish()
    category_id = get_category_id(category).get('id')
    delete_category_by_id(id=category_id)
    await message.answer("Category o'chirildi ❌", reply_markup=menu_keyboards())




@dp.message_handler()
async def menu_handler(message: types.Message):
    if message.text in [category['name'] for category in get_all_categories()]:  # 🍔 Burgerlar
        c_id = get_c_id_by_name(message.text)
        await message.answer("Mahsulotlar", reply_markup=product_keyboards_by_category(c_id))  # 🍔 Mini Burger
    elif message.text == '🛍 Mening zakazlarim':
        await message.answer("Sizning zakazlarizm")

    elif message.text == '✍️ Ariza qoldirish':
        await message.answer("Ariza qoldirish")


@dp.callback_query_handler(lambda call: call.data.startswith('add_to_cart'))
async def callback_handler(call: types.CallbackQuery):
    data = call.data
    product_id = data.split('_')[-1]
    product = get_product_by_id(product_id)
    # create_table_cart()
    # shu joyda database.py ni ichida add_product_to_cart funksiyasini yozing


@dp.callback_query_handler()
async def callback_handler(call: types.CallbackQuery):
    data = call.data
    product = get_product_by_id(data)
    await call.message.answer_photo(photo=product.get('image'), caption=f"{product.get('name')} - {product.get('price')} so'm",
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                        [types.InlineKeyboardButton('Savatchaga qo\'shish', callback_data=f"add_to_cart_{product.get('id')}")],
                                        [types.InlineKeyboardButton('Orqaga', callback_data='back')]
                                    ]))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=create_db())
