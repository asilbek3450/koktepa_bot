from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_all_categories, get_all_products


start_keyboards = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboards.add(KeyboardButton('🍴 Menu'))
start_keyboards.add(KeyboardButton('🛍 Mening zakazlarim'))
start_keyboards.add(KeyboardButton('✍️ Ariza qoldirish'), KeyboardButton('⚙️ Sozlamalar'))

admin_start_keyboards = ReplyKeyboardMarkup(resize_keyboard=True, 
    keyboard=[
        [KeyboardButton('🍴 Menu')],
        [KeyboardButton('Category ✏️/➕'), KeyboardButton('Mahsulot ✏️/➕')],
        [KeyboardButton('Category ochirish ❌'), KeyboardButton('Mahsulot ochirish ❌')],
        [KeyboardButton('Zakazlarni korish')]
])

contact = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Telefon raqam jonatish', request_contact=True))


def menu_keyboards():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    categories = get_all_categories()
    for category in categories:
        keyboard.add(KeyboardButton(category['name']))
    return keyboard


def product_keyboards_by_category(category_id):
    keyboard = InlineKeyboardMarkup()
    products = get_all_products()
    for product in products:
        if product['category_id'] == category_id:
            keyboard.add(InlineKeyboardButton(product['name'], callback_data=product['id']))
    return keyboard