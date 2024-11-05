from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

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


