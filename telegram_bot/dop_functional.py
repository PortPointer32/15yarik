import requests
from datetime import datetime

from telegram_bot.message_s import MESSAGES
from telegram_bot.KeyboardButton import BUTTON_TYPES
from telegram_bot.utils import StatesUsers


# ===================================================
# =============== ПОЛУЧЕНИЕ КУРСА BTC ===============
# ===================================================
def convert_rub_to_btc(amount, coin):
    try:
        if coin == "rub":
            return amount
        else:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": f"{coin}",
                "vs_currencies": "rub"
            }

            response = requests.get(url, params=params, verify=False).json()[coin]["rub"]
            amount_btc = amount / response
            return amount_btc

    except Exception as ex:
        print(ex)
        return "Не удалось получить курс обмена"


async def check_state_4_5(state, db, message):
    data = await state.get_data()
    time_left = str(data['time_30'] - datetime.now())
    if time_left[0:2] == "-1":
        count_warring = int(db.user_exists(message.from_user.id)[0][4]) - 1
        await message.answer(MESSAGES["not_pay"])
        await message.answer(MESSAGES["warning_pay"] % count_warring)
        db.update_count_warring(message.from_user.id, int(count_warring))
        await state.finish()
    else:
        time_left = time_left.split(":")[1]
        btn = {'keyboard': [[{'text': '✔️ Проверить оплату'}, {'text': '🚫 Отменить заказ'}], [{'text': '🏠 Меню'}],
                            [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}],
                            [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}],
                            [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
        text = f"""❗️ Напоминаем,
Ваш заказ не оплачен на сумму {data['count_top_up']} руб.
До конца резерва осталось {time_left} минут.\n"""
        await message.answer(
            text + MESSAGES[data['mess']] % (data['number_order'], data['number_coin'], data['rub_coin']),
            reply_markup=btn)


async def check_state_6(state, message, db):
    data = await state.get_data()
    last_data_ban = str(data["data_ban"] - datetime.now())
    last_data_ban_1 = last_data_ban.split(":")[1]
    if last_data_ban[0] == "-":
        await state.finish()
    else:
        await message.answer(MESSAGES["ban_pay_data"] % last_data_ban_1, reply_markup=BUTTON_TYPES["BTN_HOME"])
        db.update_count_warring(message.from_user.id, 3)
        await state.set_state(StatesUsers.all()[6])
