from flask import Flask, request
import flask
import os
import telebot
from telebot import types
from ParserTvs import tv
from ParserCams import cam

app = Flask(__name__)
APP_NAME = 'classique-bastille-17767'
TOKEN = '1242001511:AAGWYpDl98LnZgIWFikQHGQpi9RZ2V5pFO8'
bot = telebot.TeleBot(TOKEN)

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return "Hello from CompareWebsitesBot!", 200


keyboard = types.ReplyKeyboardMarkup(True, True)
keyboard.row('📋Список сравнений товаров')

@bot.message_handler(commands=['start'])
def message_start(message):
    bot.send_message(message.chat.id, 'Привет.', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def message_start(message):
    bot.send_message(message.chat.id, 'При различающемся наличии товаров на сайтах, \
бот Вам эти товары и пришлет. При совпадающем наличии всех товаров, бот Вам это подтвердит.', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def messages(message):
    shops_keyboard = types.InlineKeyboardMarkup(row_width=1)
    compare_list = ['Телевизоры', 'Камеры']

    for i in compare_list:
        if i == 'Телевизоры':
            button = types.InlineKeyboardButton('📺' + i, callback_data=i)
        elif i == 'Камеры':
            button = types.InlineKeyboardButton('📹' + i, callback_data=i)
        shops_keyboard.add(button)

    if message.text.lower() == '📋список сравнений товаров':
        bot.send_message(message.chat.id, '📋Список сравнений:', reply_markup=shops_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def messages_buttons(call):
    if call.message:
        if call.data == 'Телевизоры':
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='⏱Подождите, пожалуйста, 10-15 секунд.')
            tv_function = tv()
            bot.send_message(call.message.chat.id, tv_function, disable_web_page_preview=True, parse_mode='HTML')
        if call.data == 'Камеры':
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='⏱Подождите, пожалуйста, 5 минут.')
            cam_function = cam()
            try:
                file = open('Камеры.xlsx', 'rb')
                bot.send_document(call.message.chat.id, file)
            except:
                bot.send_message(call.message.chat.id, cam_function, parse_mode='HTML')
            try:
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Камеры.xlsx')
                os.remove(path)
            except:
                pass


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
