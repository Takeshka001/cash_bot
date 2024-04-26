import os
import dotenv
import telebot
from telebot import types
import csv

dotenv.load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
user_registration_file = 'users.csv'

bot = telebot.TeleBot(TOKEN)
user_registration = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Пройдите регистрацию пользователя, где вы должны указать свою фамилию, город проживания, адрес и телефон. /register')

@bot.message_handler(commands=['register'])
def register(message):
    chat_id = message.chat.id
    if chat_id not in user_registration:
        user_registration[chat_id] = {}
        bot.send_message(chat_id, 'Введите вашу фамилию:')
    else:
        bot.send_message(chat_id, 'Вы уже зарегистрированы')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id in user_registration:
        current_step = len(user_registration[chat_id]) 

        if current_step == 0:
            user_registration[chat_id]['full_name'] = message.text
            bot.send_message(chat_id, 'Введите ваш город проживания:')
        elif current_step == 1:
            user_registration[chat_id]['city'] = message.text
            bot.send_message(chat_id, 'Введите ваш адрес:')
        elif current_step == 2:
            user_registration[chat_id]['address'] = message.text
            bot.send_message(chat_id, 'Введите ваш номер телефона:')
        elif current_step == 3:
            user_registration[chat_id]['phone'] = message.text
            save_registration(chat_id)
            bot.send_message(chat_id, 'Спасибо! Ваши данные зарегистрированы.')

def save_registration(chat_id):
    with open(user_registration_file, 'a', newline='') as file:
        fieldnames = ['chat_id', 'full_name', 'city', 'address', 'phone']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({'chat_id': chat_id,
                         'full_name': user_registration[chat_id]['full_name'],
                         'city': user_registration[chat_id]['city'],
                         'address': user_registration[chat_id]['address'],
                         'phone': user_registration[chat_id]['phone']})

if __name__ == '__main__':
    bot.polling(none_stop=True)

