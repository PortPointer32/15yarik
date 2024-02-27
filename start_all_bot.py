import os
import logging
import time
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.dispatcher import Dispatcher, FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from random import randrange
import asyncio

from telegram_bot.message_s import MESSAGES
from telegram_bot.KeyboardButton import BUTTON_TYPES
from telegram_bot.dop_functional import convert_rub_to_btc, check_state_4_5, check_state_6
from telegram_bot.utils import StatesUsers
from cfg.database import Database


db = Database('/home/str/15yarik/cfg/database')


async def start_bot(dp):
    event_loop.create_task(dp.start_polling())


def bot_init(event_loop, token, number_bot):
    bot = Bot(token, parse_mode="HTML")
    dp = Dispatcher(bot=bot, storage=MemoryStorage())

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()

    all_type_pay = ["rub", "litecoin", "bitcoin", "ethereum"]

    # ===================================================
    # ================== СТАРТ КОМАНДА ==================
    # ===================================================
    async def start_command(message: Message):
            state = dp.current_state(user=message.from_user.id)
            current_state = await state.get_state()
            if current_state == "state_4" or current_state == "state_5":
                await check_state_4_5(state, db, message)
            elif current_state == "state_6":
                await check_state_6(state, message, db)
            elif current_state == "state_2":
                data = await state.get_data()
                if message.text == data["captha"]:
                    await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
                    await state.finish()
                else:
                    captcha_text = os.listdir(path="img")[4:][random.randint(0, 9)][0:-4]
                    with open(f'img/{captcha_text}.jpg', 'rb') as photo:
                        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=MESSAGES["captha"])
                    await state.update_data(captha=captcha_text)
                    await state.set_state(StatesUsers.all()[2])
            else:
                if not bool(len(db.user_exists(message.from_user.id))):
                    db.add_user(message.from_user.id, message.from_user.username)
                    print(str(db.get_all_info("CAPTHA")))
                    if str(db.get_all_info("CAPTHA")[0]) == "True":
                        captcha_text = os.listdir(path="img")[4:][random.randint(0, 9)][0:-4]
                        with open(f'img/{captcha_text}.jpg', 'rb') as photo:
                            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=MESSAGES["captha"])
                        await state.update_data(captha=captcha_text)
                        await state.set_state(StatesUsers.all()[2])
                    else:
                        await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
                        await state.finish()
                else:
                    await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
                    await state.finish()

    # ================== ПРОХОЖДЕНИЕ КАПЧИ ==================
    async def captha_start(message: Message, state: FSMContext):
        data = await state.get_data()
        if message.text == data["captha"]:
            await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()
        else:
            captcha_text = os.listdir(path="img")[4:][random.randint(0, 9)][0:-4]
            with open(f'img/{captcha_text}.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=MESSAGES["captha"])
            await state.update_data(captha=captcha_text)
            await state.set_state(StatesUsers.all()[2])

    # ===================================================
    # ================= ПРОСТЫЕ КОМАНДЫ =================
    # ===================================================
    async def easy_task(message: Message):
        state = dp.current_state(user=message.from_user.id)
        current_state = await state.get_state()
        if current_state == "state_4" or current_state == "state_5":
            await check_state_4_5(state, db, message)
        elif current_state == "state_6":
            await check_state_6(state, message, db)
        else:
            if message.text == "❓ Помощь" or message.text == "/help":
                await message.answer(MESSAGES[f"{message.text}_{number_bot}"], reply_markup=BUTTON_TYPES["BTN_HOME"])
            else:
                await message.answer(MESSAGES[f"{message.text}"], reply_markup=BUTTON_TYPES["BTN_HOME"])

            state = dp.current_state(user=message.from_user.id)
            await state.finish()

    # ===================================================
    # ================= ПОПОЛНИТЬ БАЛАНС ================
    # ===================================================
    async def top_up_balance_task(message: Message):
        state = dp.current_state(user=message.from_user.id)
        current_state = await state.get_state()
        if current_state == "state_4" or current_state == "state_5":
            await check_state_4_5(state, db, message)
        elif current_state == "state_6":
            await check_state_6(state, message, db)
        else:
            await state.finish()
            await message.answer(MESSAGES[f"{message.text}"] % db.get_all_info("MIN_BALANCE")[0], reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.set_state(StatesUsers.all()[0])

    # ================= ВВОД СУММЫ ================
    async def input_balance_task(message: Message, state: FSMContext):
        if message.text.isnumeric():
            if int(message.text) >= int(db.get_all_info("MIN_BALANCE")[0]):
                btn = {'keyboard': [[{'text': f'☑️ Перейти к оплате up_balance_{message.text}'}], [{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
                await state.update_data(count_top_up=message.text)
                await message.answer(MESSAGES["sure_balance"] % message.text, reply_markup=btn)
                await state.set_state(StatesUsers.all()[1])
            else:
                await message.answer(MESSAGES["💰 Пополнить баланс"] % db.get_all_info("MIN_BALANCE")[0])
                await state.set_state(StatesUsers.all()[0])
        else:
            await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()

    # ================= ВЫБОР ТИПА ОПЛАТЫ ================
    async def what_pay_task(message: Message, state: FSMContext):
        await message.answer(MESSAGES[f"what_pay"], reply_markup=BUTTON_TYPES["BTN_HOME"])
        time.sleep(1)
        await message.answer(MESSAGES[f"what_pay_{number_bot}"], reply_markup=BUTTON_TYPES["BTN_HOME"])
        await state.set_state(StatesUsers.all()[3])

    # ================= ПОДТВЕРЖДЕНИЯ ОПЛАТЫ ================
    async def pay_task(message: Message, state: FSMContext):
        num_pay = message.text.split("/")[-1].split("_")
        await message.answer(MESSAGES[f"what_pay"], reply_markup=BUTTON_TYPES["BTN_HOME"])
        time.sleep(1)
        number_order = int(db.get_all_info("NUM_ORDER")[0]) + int(random.randint(11, 39))
        db.update_num_order(number_order)
        NUMBER_CARD = db.get_all_info("NUMBER_CARD")[0].split("|")
        NUMBER_LTC = db.get_all_info("NUMBER_LTC")[0].split("|")
        NUMBER_BTC = db.get_all_info("NUMBER_BTC")[0].split("|")
        NUMBER_ETH = db.get_all_info("NUMBER_ETH")[0].split("|")
        all_number = [NUMBER_CARD, NUMBER_LTC, NUMBER_BTC, NUMBER_ETH]
        data = await state.get_data()
        if "/up_balance_1" in message.text:
            rub_coin = int(data['count_top_up'])
        else:
            rub_coin = f"{float(convert_rub_to_btc(int(data['count_top_up']), all_type_pay[int(num_pay[2])-1]))*1.1:.8f}"
        now_plus_30 = datetime.now() + timedelta(minutes=60)
        await state.update_data(number_order=number_order)
        await state.update_data(number_coin=all_number[int(num_pay[2])-1][randrange(len(all_number[int(num_pay[2])-1]))])
        await state.update_data(rub_coin=rub_coin)
        await state.update_data(time_30=now_plus_30)
        await state.update_data(mess=f"data_pay_{num_pay[2]}")
        if f"{num_pay[2]}" != "0":
            text = f"""💰 Вы сформировали заявку на пополнение баланса на сумму {data['count_top_up']} руб.
До конца резерва осталось 60мин.\n"""
            await message.answer(text + MESSAGES[f"data_pay_{num_pay[2]}"] % (number_order, all_number[int(num_pay[2])-1][randrange(len(all_number[int(num_pay[2])-1]))], rub_coin), reply_markup=BUTTON_TYPES["BTN_HOME_2"])
            await state.set_state(StatesUsers.all()[4])
        else:
            await message.answer(MESSAGES[f"data_pay_{num_pay[2]}"] % (rub_coin, number_order), reply_markup=BUTTON_TYPES["BTN_HOME_2"])

        data = await state.get_data()
        if datetime.now().minute + 15 > 60:
            min_date = datetime.now().minute + 15 - 60
            if datetime.now().hour + 1 == 24:
                scheduler.add_job(napominalca_15, trigger='cron', hour=0, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
            else:
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour + 1, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
        else:
            scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute + 15, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
        if datetime.now().minute + 30 > 60:
            min_date = datetime.now().minute + 30 - 60
            if datetime.now().hour + 1 == 24:
                scheduler.add_job(napominalca_15, trigger='cron', hour=0, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
            else:
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour + 1, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order + 1}")
        else:
            scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute + 30, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order + 1}")

    # ================= ПРОВЕРКА ОПЛАТЫ ================
    async def check_pay_task(message: Message, state: FSMContext):
        data = await state.get_data()
        if message.text == "🚫 Отменить заказ" or message.text == "/order_cancel":
            await message.answer(MESSAGES["cancel_pay"] % data["number_order"], reply_markup=BUTTON_TYPES["BTN_HOME_3"])
            scheduler.remove_job(f"{data['number_order']}")
            scheduler.remove_job(f"{int(data['number_order']) + 1}")
            await state.set_state(StatesUsers.all()[5])
        else:
            time_left = str(data['time_30'] - datetime.now())
            if time_left[0] == "-":
                count_warring = int(db.user_exists(message.from_user.id)[0][4]) - 1
                await message.answer(MESSAGES["not_pay"])
                if count_warring == 0:
                    await message.answer(MESSAGES["ban_pay"], reply_markup=BUTTON_TYPES["BTN_HOME"])
                    await state.update_data(data_ban=datetime.now() + timedelta(minutes=60))
                    await state.set_state(StatesUsers.all()[6])
                else:
                    await message.answer(MESSAGES["warning_pay"] % count_warring, reply_markup=BUTTON_TYPES["BTN_HOME"])
                    await state.finish()
                db.update_count_warring(message.from_user.id, int(count_warring))
            else:
                time_left = time_left.split(":")[1]
                text = f"""❗️ Напоминаем,
ваш заказ не оплачен на сумму {data['count_top_up']} руб.
До конца резерва осталось {time_left} минут.\n"""
                await message.answer(text + MESSAGES[data['mess']] % (data['number_order'], data['number_coin'], data['rub_coin']), reply_markup=BUTTON_TYPES["BTN_HOME_2"])
                await state.set_state(StatesUsers.all()[4])

    # ================= ОТМЕНА ОПЛАТЫ ================
    async def cancel_pay_task(message: Message, state: FSMContext):
        if message.text == "✔️ Подтверждаю отмену":
            count_warring = int(db.user_exists(message.from_user.id)[0][4]) - 1
            await message.answer(MESSAGES["not_pay"])
            if count_warring == 0:
                await message.answer(MESSAGES["ban_pay"], reply_markup=BUTTON_TYPES["BTN_HOME"])
                await state.update_data(data_ban=datetime.now() + timedelta(minutes=60))
                await state.set_state(StatesUsers.all()[6])
            else:
                await message.answer(MESSAGES["warning_pay"] % count_warring, reply_markup=BUTTON_TYPES["BTN_HOME"])
                await state.finish()
            db.update_count_warring(message.from_user.id, int(count_warring))
        else:
            data = await state.get_data()
            time_left = str(data['time_30'] - datetime.now())
            time_left = time_left.split(":")[1]
            text = f"""❗️ Напоминаем,
ваш заказ не оплачен на сумму {data['count_top_up']} руб.
До конца резерва осталось {time_left} минут.\n"""
            await message.answer(text + MESSAGES[data['mess']] % (data['number_order'], data['number_coin'], data['rub_coin']),reply_markup=BUTTON_TYPES["BTN_HOME_2"])
            await state.set_state(StatesUsers.all()[4])

    # ================= БАН ================
    async def ban_task(message: Message, state: FSMContext):
        data = await state.get_data()
        last_data_ban = str(data["data_ban"] - datetime.now())
        last_data_ban_1 = last_data_ban.split(":")[1]
        if last_data_ban[0] == "-":
            await state.finish()
        else:
            await message.answer(MESSAGES["ban_pay_data"] % last_data_ban_1, reply_markup=BUTTON_TYPES["BTN_HOME"])
            db.update_count_warring(message.from_user.id, 3)
            await state.set_state(StatesUsers.all()[6])

    # ================= Напоминалка ================
    async def napominalca_15(data, message):
        time_left = str(data['time_30'] - datetime.now())
        time_left = time_left.split(":")[1]
        text = f"""❗️ Напоминаем,
ваш заказ не оплачен на сумму {data['count_top_up']} руб.
До конца резерва осталось {time_left} минут.\n"""
        await message.answer(
            text + MESSAGES[data['mess']] % (data['number_order'], data['number_coin'], data['rub_coin']),
            reply_markup=BUTTON_TYPES["BTN_HOME_2"])

    # ===================================================
    # =================== ВСЕ ПРОДУКТЫ ==================
    # ===================================================
    async def all_products_task(message: Message):
        state = dp.current_state(user=message.from_user.id)
        current_state = await state.get_state()
        if current_state == "state_4" or current_state == "state_5":
            await check_state_4_5(state, db, message)
        elif current_state == "state_6":
            await check_state_6(state, message, db)
        else:
            await state.finish()
            all_products_db = db.get_all_products_keyboard()
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            i = 0
            discount_product = db.get_all_info("DISCOUNT")[0]
            products_dop = []
            for idx, products_db in enumerate(all_products_db):
                idx+=1
                products = products_db[0].split("|")
                for idx2, product in enumerate(products):
                    if product not in products_dop:
                        product = product.split("(")
                        btn['keyboard'].insert(i, [{'text': f'{product[0]} /product_{idx}_{idx2}'}])
                        i += 1
                        text += f"📦 {product[0]}\n<b>+ скидка до {discount_product}%</b>\n{product[1][:-4]} руб 👉 /product_{idx}_{idx2}\n🗻🗻🗻🗻🗻🗻🗻\n"
                products_dop += products

            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["all_products"] % text, reply_markup=btn)

    # =============== ВЫБОР ГОРОДА ===============
    async def product_city_task(message: Message):
        try:
            id_product = message.text.split("/")[-1].split("_")
            product_db = db.get_keyboard_city_id(id_product[1])[0].split("|")[int(id_product[2])]
            all_products_db = db.get_all_keyboard()
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            i = 0
            discount_product = db.get_all_info("DISCOUNT")[0]
            for idx, products_db in enumerate(all_products_db):
                idx+=1
                all_product_in_city = products_db[2].split("|")
                for idx2, product_in_city in enumerate(all_product_in_city):
                    if product_db == product_in_city:
                        btn['keyboard'].insert(i, [{'text': f'{products_db[1]} /order_{idx}_{idx2}'}])
                        i += 1
                        text += f"<i>🚩 {products_db[1]}</i>\n<b>+ скидка до {discount_product}%</b>\n<i>Далее 👉 /order_{idx}_{idx2}</i>\n🗻🗻🗻🗻🗻🗻🗻\n"
            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["add_product"] % (product_db.split("(")[0], product_db.split("(")[1][:-1], text), reply_markup=btn)
        except Exception as ex:
            print(ex)
            await message.answer("Ошибка!\nТакого города нет!")

    # =============== ВЫБОР РАЙОНА ===============
    async def product_district_task(message: Message):
        try:
            id_product = message.text.split("/")[-1].split("_")
            product_db = db.get_keyboard_city_id(id_product[1])[0].split("|")[int(id_product[2])].split("(")
            city_product = db.get_keyboard_city_id(id_product[1])
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            i = 0
            all_district = city_product[2].split("|")
            discount_product = db.get_all_info("DISCOUNT")[0]
            for idx, district in enumerate(all_district):
                # print("".join(district.split("[")[1:]).split("]"))
                # print(district.split("[")[1:])
                if id_product[2] in "".join(district.split("[")[1:]).split("]"):
                    # print(district)
                    btn['keyboard'].insert(i, [{'text': f'{district.split("[")[0]} /district_{id_product[1]}_{id_product[2]}_{idx}'}])
                    i += 1
                    text += f"🚩 {district.split('[')[0]}</i>\n<b>+ скидка до {discount_product}%</b>\n<i>Выбрать 👉 /district_{id_product[1]}_{id_product[2]}_{idx}\n🗻🗻🗻🗻🗻🗻🗻\n"
            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["add_district"] % (product_db[0], product_db[1][:-1], city_product[1], text), reply_markup=btn)
        except:
            await message.answer("Ошибка!\nТакого района нет!")

    # =============== ВЫБОР ОПЛАТЫ ===============
    async def pay_product_task(message: Message):
        try:
            discount_product = db.get_all_info("DISCOUNT")[0]
            id_product = message.text.split("/")[-1].split("_")
            id_pay_product = f"{id_product[1]}_{id_product[2]}_{id_product[3]}"
            await message.answer(MESSAGES[f"product_pay_{number_bot}"].replace("%s", id_pay_product).replace("%a", f"{discount_product}%"), reply_markup=BUTTON_TYPES["BTN_HOME"])
        except Exception as ex:
            print(ex)
            await message.answer("Ошибка!\nТакого товара нет!")

    # =============== ОПЛАТА ТОВАРА ===============
    async def buy_product_task(message: Message):
        id_product = message.text.split("/")[-1].split("_")
        price_product = db.get_keyboard_city_id(id_product[3])[0].split("|")[int(id_product[4])].split("(")
        discount_price = int(int(price_product[1][:-4]) - (int(db.get_all_info("DISCOUNT")[0]) / 100 * int(price_product[1][:-4])))
        if "/buy_product_0" in message.text:
            await message.answer(MESSAGES["balance_pay"] % price_product[1][:-1])
        else:
            district_name = db.get_keyboard_city_id(id_product[3])[2].split("|")[int(id_product[5])].split("[")[0]
            NUMBER_CARD = db.get_all_info("NUMBER_CARD")[0].split("|")
            NUMBER_LTC = db.get_all_info("NUMBER_LTC")[0].split("|")
            NUMBER_BTC = db.get_all_info("NUMBER_BTC")[0].split("|")
            NUMBER_ETH = db.get_all_info("NUMBER_ETH")[0].split("|")
            all_number = [NUMBER_CARD, NUMBER_LTC, NUMBER_BTC, NUMBER_ETH]
            num_coin = all_number[int(id_product[2])-1][randrange(len(all_number[int(id_product[2])-1]))]
            number_order = int(db.get_all_info("NUM_ORDER")[0]) + int(random.randint(11, 39))
            db.update_num_order(number_order)
            if "/buy_product_1" in message.text:
                discount_price = int(int(discount_price) + (int(discount_price) * db.get_all_info("COMMISSION")[0] / 100))
                rub_coin = discount_price
            else:
                rub_coin = f"{float(convert_rub_to_btc(discount_price, all_type_pay[int(id_product[2]) - 1]))*1.1:.8f}"
            await message.answer(MESSAGES[f"buy_product_{id_product[2]}"] % (f"{price_product[0]}", district_name, number_order, num_coin, rub_coin), reply_markup=BUTTON_TYPES["BTN_HOME_2"])

            state = dp.current_state(user=message.from_user.id)
            now_plus_30 = datetime.now() + timedelta(minutes=60)
            await state.update_data(number_order=number_order)
            await state.update_data(number_coin=num_coin)
            await state.update_data(rub_coin=rub_coin)
            await state.update_data(time_30=now_plus_30)
            await state.update_data(mess=f"data_pay_{id_product[2]}")
            await state.update_data(count_top_up=int(discount_price))
            data = await state.get_data()

            if datetime.now().minute + 15 > 60:
                min_date = datetime.now().minute + 15 - 60
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour + 1, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
            else:
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute + 15, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order}")
            if datetime.now().minute + 30 > 60:
                min_date = datetime.now().minute + 30 - 60
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour + 1, minute=min_date, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order + 1}")
            else:
                scheduler.add_job(napominalca_15, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute + 30, start_date=datetime.now(), kwargs={"data": data, "message": message}, id=f"{number_order + 1}")

            await state.set_state(StatesUsers.all()[4])

    # ===================================================
    # =================== ВСЕ ЛОКАЦИИИ ==================
    # ===================================================
    async def all_locations_task(message: Message):
        state = dp.current_state(user=message.from_user.id)
        current_state = await state.get_state()
        if current_state == "state_4" or current_state == "state_5":
            await check_state_4_5(state, db, message)
        elif current_state == "state_6":
            await check_state_6(state, message, db)
        else:
            await state.finish()
            discount_product = db.get_all_info("DISCOUNT")[0]
            all_products_db = db.get_keyboard()
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            for idx, city_db in enumerate(all_products_db):
                btn['keyboard'].insert(idx, [{'text': f'{city_db[0]} /location_{idx + 1}'}])
                text += f"🚩 {city_db[0]}</i>\n<b>+ скидка до {discount_product}%</b>\n<i>Жми 👉 /location_{idx + 1}\n🗻🗻🗻🗻🗻🗻🗻\n"
            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["get_city"] % text, reply_markup=btn)

    # =================== ВЫБОР РАЙОНА ==================
    async def location_district_task(message: Message):
        try:
            id_product = message.text.split("/")[-1].split("_")
            all_district = db.get_keyboard_city_id(id_product[1])
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            i = 0
            discount_product = db.get_all_info("DISCOUNT")[0]
            products_dop = []

            for idx, districts in enumerate(all_district[2].split("|")):
                if f"🏘 {districts.split('[')[0]}\nЖми 👉 " not in text:
                    if districts.split('[')[0] not in products_dop:
                        btn['keyboard'].insert(i, [{'text': f'{districts.split("[")[0]} /districts_{id_product[1]}_{idx}'}])
                        i += 1
                        text += f"🏘 {districts.split('[')[0]}</i>\n<b>+ скидка до {discount_product}%</b>\n<i>Жми 👉 /districts_{id_product[1]}_{idx}\n🗻🗻🗻🗻🗻🗻🗻\n"
                products_dop += [districts.split('[')[0]]
            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["get_district"] % (all_district[1], text), reply_markup=btn)
        except:
            await message.answer("Ошибка!\nТакого города нет!")

    # =================== ВЫБОР ПРОДУКТА ==================
    async def district_product_task(message: Message):
        try:
            id_product = message.text.split("/")[-1].split("_")
            all_district = db.get_keyboard_city_id(id_product[1])
            text = ""
            btn = {'keyboard': [[{'text': '🏠 Меню'}], [{'text': '📦 Все продукты'}, {'text': '👉 Локации'}], [{'text': '💰 Мой последний заказ'}, {'text': '❓ Помощь'}], [{'text': '💰 Баланс'}, {'text': '💰 Пополнить баланс'}]], 'resize_keyboard': True}
            my_id_product = []
            for my_district in all_district[2].split("|"):
                if all_district[2].split("|")[int(id_product[2])][:-3] in my_district:
                    my_id_product += [int(my_district[-2])]
            i = 0
            discount_product = db.get_all_info("DISCOUNT")[0]
            for idx, products in enumerate(all_district[0].split("|")):
                if idx in my_id_product:
                    btn['keyboard'].insert(i, [{'text': f'{products.split("(")[0]} /district_{id_product[1]}_{idx}_{id_product[2]}'}])
                    i += 1
                    text += f"📦 {products.split('(')[0]}\n<b>{products.split('(')[1][:-1]}</b>\n<b>+ скидка до {discount_product}%</b>\n<i>Заказать 👉 /district_{id_product[1]}_{idx}_{id_product[2]}</i>\n🗻🗻🗻🗻🗻🗻🗻\n"
            text = "\n".join(text.split("\n")[:-2]) + "\n"
            await message.answer(MESSAGES["get_product"] % (all_district[2].split("|")[int(id_product[2])][:-3], text), reply_markup=btn)
        except:
            await message.answer("Ошибка!\nТакого района нет!")

    # ===================================================
    # =============== НЕИЗВЕСТНАЯ КОМАНДА ===============
    # ===================================================
    async def unknown_command(message: Message):
        if not bool(len(db.user_exists(message.from_user.id))):
            db.add_user(message.from_user.id, message.from_user.username)
            if str(db.get_all_info("CAPTHA")[0]) == "True":
                captcha_text = os.listdir(path="img")[4:][random.randint(0, 9)][0:-4]
                with open(f'img/{captcha_text}.jpg', 'rb') as photo:
                    await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=MESSAGES["captha"])
                state = dp.current_state(user=message.from_user.id)
                await state.update_data(captha=captcha_text)
                await state.set_state(StatesUsers.all()[2])
            else:
                await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])

        else:
            await bot.send_message(text=MESSAGES[f"start_user_{number_bot}"], chat_id=message.from_user.id, reply_markup=BUTTON_TYPES["BTN_HOME"])
            state = dp.current_state(user=message.from_user.id)
            await state.finish()

    # СТАРТ
    dp.register_message_handler(start_command, lambda message: message.text == '/start' or message.text == '/menu' or message.text == '🏠 Меню', state="*")
    dp.register_message_handler(captha_start, state=StatesUsers.STATE_2)

    # ПРОСТЫЕ ЗАДАЧИ
    dp.register_message_handler(easy_task, lambda message: message.text.lower() == '💰 мой последний заказ' or message.text.lower() == '/last_order' or message.text.lower() == '💰 баланс' or message.text.lower() == '/balance'  or message.text.lower() == '❓ помощь' or message.text.lower() == '/help', state="*")

    # ВСЕ ПРОДУКТЫ
    dp.register_message_handler(all_products_task, lambda message: message.text == '📦 Все продукты' or message.text == '/products', state="*")
    dp.register_message_handler(product_city_task, lambda message: "/product_" in message.text)
    dp.register_message_handler(product_district_task, lambda message: "/order_" in message.text)
    dp.register_message_handler(pay_product_task, lambda message: "/district_" in message.text)
    dp.register_message_handler(buy_product_task, lambda message: "/buy_product_" in message.text)

    # ВСЕ ЛОКАЦИИ
    dp.register_message_handler(all_locations_task, lambda message: message.text == '👉 Локации' or message.text == '/locations', state="*")
    dp.register_message_handler(location_district_task, lambda message: "/location_" in message.text)
    dp.register_message_handler(district_product_task, lambda message: "/districts_" in message.text)

    # ПОПОЛНИТЬ БАЛАНС
    dp.register_message_handler(top_up_balance_task, lambda message: message.text == '💰 Пополнить баланс', state="*")
    dp.register_message_handler(input_balance_task, state=StatesUsers.STATE_0)
    dp.register_message_handler(what_pay_task, state=StatesUsers.STATE_1)
    dp.register_message_handler(pay_task, state=StatesUsers.STATE_3)
    dp.register_message_handler(check_pay_task, state=StatesUsers.STATE_4)
    dp.register_message_handler(cancel_pay_task, state=StatesUsers.STATE_5)
    dp.register_message_handler(ban_task, state=StatesUsers.STATE_6)

    # НЕИЗВЕСТНАЯ КОМАНДА
    dp.register_message_handler(unknown_command, content_types=["text"])

    event_loop.run_until_complete(start_bot(dp))


if __name__ == '__main__':
    pid = os.getpid()
    db.update_pid(pid)

    logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)
    tokens = db.get_bot_token()[0].split("|")
    event_loop = asyncio.get_event_loop()

    for idx, token in enumerate(tokens):
        if idx != 0:
            try:
                token = token.split(",")
                bot_init(event_loop, token[0], token[1])
            except:
                ...

    event_loop.run_forever()
