from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# ================= КНОПКИ ПОЛЬЗОВАТЕЛЯ =================

# МЕНЮ
btn_menu = KeyboardButton("🏠 Меню")
btn_all_product = KeyboardButton("📦 Все продукты")
btn_location = KeyboardButton("👉 Локации")
btn_last_order = KeyboardButton("💰 Мой последний заказ")
btn_help = KeyboardButton("❓ Помощь")
btn_balance = KeyboardButton("💰 Баланс")
btn_top_up_balance = KeyboardButton("💰 Пополнить баланс")

btn_check_pay = KeyboardButton("✔️ Проверить оплату")
btn_cancel_pay = KeyboardButton("🚫 Отменить заказ")

btn_accept_cancel_pay = KeyboardButton("✔️ Подтверждаю отмену")
btn_back = KeyboardButton("🔙 Назад")

btn_pay = InlineKeyboardButton(text="Оплатить", callback_data="pay_card_p")
btn_menu_home = KeyboardButton("Главное меню")
btn_menu_home_inline = InlineKeyboardButton(text="Главное меню", callback_data="menu_home")

# РЕФЕРАЛЬНАЯ П
btn_add_bot = InlineKeyboardButton(text="Добавить бота", callback_data="add_bot")

# ПОПОЛНЕНИЕ БАЛАНСА
btn_card = InlineKeyboardButton(text='Оплата на карту💳', callback_data="card")
btn_bitcoin = InlineKeyboardButton(text="Bitcoin", callback_data="bitcoin")
btn_ltc = InlineKeyboardButton(text="Litecoin", callback_data="ltc")
btn_problems_pay = InlineKeyboardButton(text="Проблемы с оплатой?", url="https://t.me/gopp123g")

btn_cancel = KeyboardButton("Отмена")


BUTTON_TYPES = {
    "BTN_HOME": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_menu).add(btn_all_product, btn_location).add(btn_last_order, btn_help).
    add(btn_balance, btn_top_up_balance),
    "BTN_HOME_2": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_check_pay, btn_cancel_pay).add(btn_menu).add(btn_all_product, btn_location).add(
        btn_last_order, btn_help).add(btn_balance, btn_top_up_balance),
    "BTN_HOME_3": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_accept_cancel_pay, btn_back).add(btn_menu).add(
        btn_all_product, btn_location).add(btn_last_order, btn_help).add(btn_balance, btn_top_up_balance),
    "BTN_MENU_HOME": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_menu_home),
    "BTN_ADD_BOT": InlineKeyboardMarkup().add(btn_add_bot).add(btn_menu_home_inline),
    "BTN_MENU": InlineKeyboardMarkup().add(btn_menu_home_inline),
    "BTN_PAY": InlineKeyboardMarkup().add(btn_card).add(btn_bitcoin).add(btn_ltc).add(btn_menu_home_inline),
    "BTN_PROBLEMS": InlineKeyboardMarkup().add(btn_problems_pay),
    "BTN_WHAT_PAY": InlineKeyboardMarkup().add(btn_pay).add(btn_menu_home_inline),

    "BTN_CANCEL": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel),
}
