import os
import dotenv
import telebot
from telebot import types

dotenv.load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)

USERS_FILE = 'users.txt'
TRANSACTIONS_FILE = 'transactions.txt'

if not os.path.exists(USERS_FILE):
    open(USERS_FILE, 'a').close()

if not os.path.exists(TRANSACTIONS_FILE):
    open(TRANSACTIONS_FILE, 'a').close()

def get_user(chat_id):
    with open(USERS_FILE, 'r') as file:
        for line in file:
            user_data = line.strip().split(',')
            if user_data[0] == str(chat_id):
                return user_data[1:]

def save_user(chat_id, full_name, city, address, phone, iin):
    with open(USERS_FILE, 'a') as file:
        file.write(f'{chat_id},{full_name},{city},{address},{phone},{iin}\n')

def save_transaction(chat_id, amount, category):
    with open(TRANSACTIONS_FILE, 'a') as file:
        file.write(f'{chat_id},{amount},{category}\n')

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет! Для начала работы пройдите регистрацию. Введите ваше имя:')
    bot.register_next_step_handler(message, register_name)

def register_name(message):
    chat_id = message.chat.id
    full_name = message.text
    bot.send_message(chat_id, 'Введите ваш город проживания:')
    bot.register_next_step_handler(message, lambda msg: register_city(full_name, msg))

def register_city(full_name, message):
    chat_id = message.chat.id
    city = message.text
    bot.send_message(chat_id, 'Введите ваш адрес:')
    bot.register_next_step_handler(message, lambda msg: register_address(full_name, city, msg))

def register_address(full_name, city, message):
    chat_id = message.chat.id
    address = message.text
    bot.send_message(chat_id, 'Введите ваш номер телефона:')
    bot.register_next_step_handler(message, lambda msg: register_phone(full_name, city, address, msg))

def register_phone(full_name, city, address, message):
    chat_id = message.chat.id
    phone = message.text
    bot.send_message(chat_id, 'Введите ваш ИИН (индивидуальный идентификационный номер):')
    bot.register_next_step_handler(message, lambda msg: register_iin(full_name, city, address, phone, msg))

def register_iin(full_name, city, address, phone, message):
    chat_id = message.chat.id
    iin = message.text
    save_user(chat_id, full_name, city, address, phone, iin)
    bot.send_message(chat_id, 'Регистрация завершена! Теперь вы можете добавлять транзакции.')
    add_transaction(message)

@bot.message_handler(commands=['add_transaction'])
def add_transaction(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton('Доход'), types.KeyboardButton('Расход'))
    bot.send_message(chat_id, 'Выберите категорию транзакции:', reply_markup=markup)
    bot.register_next_step_handler(message, enter_category)

def enter_category(message):
    chat_id = message.chat.id
    category = message.text
    if category not in ['Доход', 'Расход']:
        bot.send_message(chat_id, 'Пожалуйста, выберите категорию, используя кнопки.')
        bot.register_next_step_handler(message, enter_category)
        return
    bot.send_message(chat_id, f'Вы выбрали категорию: {category}. Теперь введите сумму транзакции:')
    bot.register_next_step_handler(message, lambda msg: enter_amount(category, msg))

def enter_amount(category, message):
    chat_id = message.chat.id
    amount = message.text
    save_transaction(chat_id, amount, category)
    bot.send_message(chat_id, f'Транзакция на сумму {amount} в категории "{category}" успешно добавлена.')
    add_transaction(message)

if __name__ == '__main__':
    bot.polling(none_stop=True)