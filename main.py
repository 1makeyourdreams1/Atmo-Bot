import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

import os
from dotenv import load_dotenv

import database

# random_numbers = [70, 343, 317, 103, 268, 336, 439, 125, 472, 317]
# random_numbers = [123, 234, 345, 456]
admin_id = 844429666

db = database.Database()

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


def random_number_handler(message):
    button = InlineKeyboardButton("Еще разок!", callback_data="game1")
    markup = InlineKeyboardMarkup()
    markup.add(button)
    numbers = get_numbers()
    try:
        user_number = int(message.text)
    except ValueError:
        bot.delete_message(message.chat.id, db.get_last_message(message.chat.id))
        bot.delete_message(message.chat.id, db.get_last_message(message.chat.id) + 1)
        last_message = bot.send_message(message.chat.id,
                                        "Я просил ввести число :(", reply_markup=markup).message_id
        db.set_last_message(message.chat.id, last_message)
    else:
        if user_number in numbers:
            numbers.remove(user_number)
            set_numbers(numbers)
            # Отправка сообщения админу
            bot.send_message(admin_id, f"@{message.from_user.username} отгадал число {user_number}")
            bot.delete_message(message.chat.id, db.get_last_message(message.chat.id))
            bot.delete_message(message.chat.id, db.get_last_message(message.chat.id) + 1)
            mesg = bot.send_message(message.chat.id, "Ого, ты угадал число, поздравляю!"
                                                          " Введи номер своего бейджа")
            db.set_last_message(message.chat.id, mesg.message_id)
            bot.register_next_step_handler(mesg, victory_handler)

        else:
            bot.delete_message(message.chat.id, db.get_last_message(message.chat.id))
            bot.delete_message(message.chat.id, db.get_last_message(message.chat.id) + 1)
            last_message = bot.send_message(message.chat.id,
                                            "Не угадал, попробуй еще раз!", reply_markup=markup).message_id
            db.set_last_message(message.chat.id, last_message)


def victory_handler(message):
    with open('winners.json', 'r+') as f:
        winners = json.load(f)
        winners["@" + str(message.from_user.username)] = message.text
        f.seek(0)
        f.truncate(0)
        json.dump(winners, f, indent=2, ensure_ascii=False)
    start_message_handler(message)

def get_winners():
    with open('winners.json', 'r') as f:
        return json.load(f)

def get_numbers():
    with open('numbers.json', 'r') as f:
        return json.load(f)["numbers"]

def set_numbers(numbers):
    with open('numbers.json', 'w') as f:
        d = dict()
        d["numbers"] = numbers
        f.seek(0)
        f.truncate(0)
        json.dump(d, f, indent=2, ensure_ascii=False)




@bot.message_handler(commands=['start'])
def start_message_handler(message):
    if not db.user_exists(message.chat.id):
        db.add_user(message.chat.id)
        db.set_last_message(message.chat.id, 0)
    if "@" + str(message.from_user.username) in get_winners().keys():
        button = InlineKeyboardButton("Рейтинг🤩", url="https://vk.com/app51868403")
        markup = InlineKeyboardMarkup()
        markup.row(button)
        last_message = db.get_last_message(message.chat.id)
        if last_message != 0:
            bot.delete_message(message.chat.id, last_message)
        last_message = bot.send_message(message.chat.id,
                                        "Ты получил ачивку! Скоро она появится в рейтинге!",
                                        reply_markup=markup).message_id
        db.set_last_message(message.chat.id, last_message)
    elif len(get_numbers()) == 0:
        last_message = db.get_last_message(message.chat.id)
        if last_message != 0:
            bot.delete_message(message.chat.id, last_message)
        button = InlineKeyboardButton("😢", callback_data="😢")
        markup = InlineKeyboardMarkup()
        markup.row(button)
        last_message = bot.send_message(message.chat.id,
                                        "Привет! К сожалению, все числа уже отгадали :(",
                                        reply_markup=markup).message_id
        db.set_last_message(message.chat.id, last_message)
    else:
        button1 = InlineKeyboardButton("Конечно!", callback_data="game1")
        markup = InlineKeyboardMarkup()
        markup.row(button1)
        last_message = db.get_last_message(message.chat.id)
        if last_message != 0:
            bot.delete_message(message.chat.id, last_message)
        last_message = bot.send_message(message.chat.id,
                                        "Приветос! Предлагаю тебе отличную возможность заработать ачивку!"
                                        " Ты в деле?", reply_markup=markup).message_id
        db.set_last_message(message.chat.id, last_message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    if callback.data == 'go':
        start_message_handler(callback.message)
    elif callback.data == 'game1':
        bot.delete_message(callback.message.chat.id, db.get_last_message(callback.message.chat.id))
        if len(get_numbers()) != 0:
            markup = InlineKeyboardMarkup()
            mesg = bot.send_message(
                callback.message.chat.id,
                    f"Я загадал 10 случайных чисел (от 1 до 500), попробуй отгадать "
                    f"их раньше остальных участников! Напиши мне свой вариант\nОсталось "
                    f"{len(get_numbers())} из 10",
                    reply_markup=markup)
            db.set_last_message(callback.message.chat.id, mesg.message_id)
            bot.register_next_step_handler(mesg, random_number_handler)
        else:
            button = InlineKeyboardButton("😢", callback_data="😢")
            markup = InlineKeyboardMarkup()
            markup.row(button)
            mesg = bot.send_message(
                callback.message.chat.id,
                f"К сожалению, все числа кончились :(", reply_markup=markup)
            db.set_last_message(callback.message.chat.id, mesg.message_id)

    elif callback.data == '😢':
        bot.answer_callback_query(callback_query_id=callback.id, text='😢')


bot.polling(none_stop=True)