import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, ADMINS
from functions import check_is_admin
from keyboards import start_keyboards, admin_start_keyboards, contact, menu_keyboards, product_keyboards_by_category, product_keyboards_by_id
from database import create_db, user_in_database, add_data_to_users, get_user_id, hozirgi_userni_olish, \
                      add_data_to_category, get_all_categories, get_category_id, delete_category_by_id, \
                      get_all_products, add_data_to_product, get_c_id_by_name, get_product_by_id, \
                      add_data_user_product, add_data_to_cart, get_user_product, delete_product_by_id
from state import RegisterState, CategoryState, ProductState, DelCategoryState, DelProductState
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

# Database initialization
async def on_startup(dp):
    create_db()
    logging.info("Database initialized successfully.")

# Start command
@dp.message_handler(commands=['start'])
@dp.message_handler(lambda message: message.text == '🔙 Orqaga')
async def start_command(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("👑 ADMIN accountga xush kelibsiz!", reply_markup=admin_start_keyboards)
    else:
        if user_in_database(message.from_user.id):
            user = hozirgi_userni_olish(message.from_user.id)
            await message.answer(f"👤 Assalomu aleykum, {user['name']}!", reply_markup=start_keyboards)
        else:
            await message.answer("👤 Assalomu aleykum, ro'yhatdan o'tish kerak /register")

# Registration command
@dp.message_handler(commands=['register'])
async def register_command(message: types.Message):
    await RegisterState.name.set()
    await message.answer("Ismingizni kiriting:")

@dp.message_handler(state=RegisterState.name)
async def register_name(message: types.Message, state):
    await state.update_data(name=message.text)
    await RegisterState.next()
    await message.answer("Telefon raqamingizni kiriting:", reply_markup=contact)

@dp.message_handler(state=RegisterState.telefon, content_types=types.ContentTypes.CONTACT)
async def register_phone(message: types.Message, state):
    user_data = await state.get_data()
    add_data_to_users(user_data['name'], message.contact.phone_number, message.from_user.id)
    await state.finish()
    await message.answer("Ro'yhatdan o'tdingiz!", reply_markup=start_keyboards)

# Show menu
@dp.message_handler(lambda message: message.text == '🍴 Menu')
async def show_menu(message: types.Message):
    await message.answer("Menu", reply_markup=menu_keyboards())

# Add category (admin only)
@dp.message_handler(lambda message: message.text == 'Category ✏️/➕')
async def add_category(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Category nomini kiriting:")
        await CategoryState.name.set()

@dp.message_handler(state=CategoryState.name)
async def save_category(message: types.Message, state):
    add_data_to_category(message.text)
    await state.finish()
    await message.answer("Category qo'shildi! ✅", reply_markup=admin_start_keyboards)

# Add product (admin only)
@dp.message_handler(lambda message: message.text == 'Mahsulot ✏️/➕')
async def add_product(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Bu mahsulot qaysi kategoriyada:", reply_markup=menu_keyboards())
        await ProductState.category_id.set()

@dp.message_handler(state=ProductState.category_id)
async def set_product_category(message: types.Message, state):
    c_id = get_c_id_by_name(message.text)
    if c_id:
        await state.update_data(category_id=c_id)
        await message.answer("Mahsulot nomini kiriting:")
        await ProductState.name.set()
    else:
        await message.answer("Kategoriya topilmadi!")

@dp.message_handler(state=ProductState.name)
async def set_product_name(message: types.Message, state):
    await state.update_data(name=message.text)
    await message.answer("💵 Mahsulot narxini kiriting:")
    await ProductState.price.set()

@dp.message_handler(state=ProductState.price)
async def set_product_price(message: types.Message, state):
    await state.update_data(price=int(message.text))
    await message.answer("📸 Mahsulot rasmini kiriting:")
    await ProductState.image.set()

@dp.message_handler(state=ProductState.image, content_types=types.ContentTypes.PHOTO)
async def set_product_image(message: types.Message, state):
    user_data = await state.get_data()
    add_data_to_product(user_data['category_id'], user_data['name'], user_data['price'], message.photo[-1].file_id)
    await state.finish()
    await message.answer("Mahsulot saqlandi ✅", reply_markup=admin_start_keyboards)

# Delete category (admin only)
@dp.message_handler(lambda message: message.text == 'Category ochirish ❌')
async def delete_category(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Qaysi kategoriyani o'chirasiz?", reply_markup=menu_keyboards())
        await DelCategoryState.name.set()

@dp.message_handler(state=DelCategoryState.name)
async def confirm_delete_category(message: types.Message, state):
    category = get_category_id(message.text)
    if category:
        delete_category_by_id(category['id'])
        await message.answer("Category o'chirildi ❌", reply_markup=menu_keyboards())
    else:
        await message.answer("Kategoriya topilmadi!")
    await state.finish()


@dp.message_handler(lambda message: message.text == 'Mahsulot ochirish ❌')
async def delete_product(message: types.Message):
    if check_is_admin(ADMINS, message.from_user.id):
        await message.answer("Qaysi kategoriyadagi mahsulotni o'chirasiz?", reply_markup=menu_keyboards())
        await DelProductState.category_id.set()
    else:
        await message.answer("Siz admin emassiz!")


@dp.message_handler(state=DelProductState.category_id)
async def confirm_delete_product(message: types.Message, state):
    category = get_category_id(message.text)
    if category:
        await state.update_data(category_id=category['id'])
        await message.answer("Qaysi mahsulotni o'chirasiz?", reply_markup=product_keyboards_by_category(category['id']))
        await DelProductState.next()
    else:
        await message.answer("Kategoriya topilmadi!")
        await state.finish()

@dp.callback_query_handler(state=DelProductState.product_id)
async def confirm_delete_product(call: types.CallbackQuery, state):
    product_id = call.data.split('_')[-1]
    await state.update_data(product_id=product_id)
    product = get_product_by_id(product_id)
    await call.message.answer(f"{product['name']} o'chirilsinmi?", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Xa o'chirilsin", callback_data="confirm_delete_product")).add(types.InlineKeyboardButton("⬅️ Bekor qilish", callback_data="cancel_delete_product")))
    await DelProductState.confirm.set()


@dp.callback_query_handler(lambda call: call.data == "cancel_delete_product", state=DelProductState.confirm)
async def cancel_delete_product(call: types.CallbackQuery, state):
    await call.message.answer("O'chirish bekor qilindi!")
    await state.finish()
    

@dp.callback_query_handler(lambda call: call.data == "confirm_delete_product", state=DelProductState.confirm)
async def confirm_delete_product(call: types.CallbackQuery, state):
    user_data = await state.get_data()
    if user_data:
        delete_product_by_id(user_data['product_id'])
        await call.message.answer("Mahsulot muvaffaqiyatli o'chirildi! ✅")
        await state.finish()
    else:
        await call.message.answer("Xatolik yuz berdi!")
        print(user_data)
        await state.finish()
        

# Shopping cart handlers
@dp.callback_query_handler(lambda call: call.data.startswith('add_to_cart'))
async def add_to_cart(call: types.CallbackQuery):
    product_id = call.data.split('_')[-1]
    user = get_user_id(call.from_user.id)
    if user:
        add_data_user_product(user['id'], product_id)
        await call.message.answer("Savatga qo'shildi ✅")

@dp.message_handler(lambda message: message.text == '🛍 Mening zakazlarim')
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    cart_items = get_user_product(user_id)
    if not cart_items:
        await message.answer("Sizning savatingiz bo'sh!")
        return

    total_price = 0
    text = ""
    for item in cart_items:
        product = get_product_by_id(item['product_id'])
        total_price += product['price']
        text += f"{product['name']} - {product['price']} so'm\n"

    await message.answer(f"{text}\nJami: {total_price} so'm", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton("✅ Tasdiqlash")], [types.KeyboardButton("❌ Bekor qilish")]],
        resize_keyboard=True
    ))

@dp.message_handler(lambda message: message.text == "✅ Tasdiqlash")
async def confirm_order(message: types.Message):
    await message.answer("Zakazingiz qabul qilindi! ✅")
    user_id = message.from_user.id
    cart_items = get_user_product(user_id)
    total_price = 0
    for item in cart_items:
        product = get_product_by_id(item['product_id'])
        total_price += product['price']
    add_data_to_cart(user_id, cart_items, total_price)
    await bot.send_message(ADMINS[0], f"Yangi zakaz: \nFoydalanuvchi: {message.from_user.full_name}\nMahsulotlar: {cart_items}\nJami: {total_price} so'm")
    

@dp.message_handler(lambda message: message.text == "❌ Bekor qilish")
async def cancel_order(message: types.Message):
    await message.answer("Zakaz bekor qilindi! ❌") 


@dp.message_handler()
async def category_handler(message: types.Message):
    text = message.text
    kategory_id = get_c_id_by_name(text)
    await message.answer(text=f"{text}ni ichidagi mahsulotlar", reply_markup=product_keyboards_by_category(kategory_id))

@dp.callback_query_handler()
async def product_handler(call: types.CallbackQuery):

    if call.data == "back":
        await call.message.answer("Menu", reply_markup=menu_keyboards())
        return
    
    product_id = call.data
    mahsulot = get_product_by_id(id=product_id)
    c = f"{mahsulot.get('name')} - narxi: {mahsulot.get('price')} so'm" # SyntaxError: f-string: unmatched '('
    await call.message.answer_photo(photo=mahsulot.get("image"), caption=c, reply_markup=product_keyboards_by_id(product_id))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
