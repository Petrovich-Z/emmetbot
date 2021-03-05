from flask import Flask
from config import Config
import telebot
import emmet

app = Flask(__name__)
app.config.from_object(Config)

bot = telebot.TeleBot(app.config['TGBOTAPI_TOKEN'])
# bot.infinity_polling()

@bot.message_handler(commands=["start"])
def start_command(message):
    # print(message)
    bot.send_message(message.chat.id, 'Welcome! '+message.text)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print(message.text)
    bot.send_message(message.chat.id, emmet.expand(message.text))


bot.polling()

import routes
