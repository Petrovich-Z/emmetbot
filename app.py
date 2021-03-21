from flask import Flask
from config import Config
import telebot
from telebot import types
import emmet

app = Flask(__name__)
app.config.from_object(Config)
counter = 0

bot = telebot.TeleBot(app.config['TGBOTAPI_TOKEN'])

@bot.message_handler(commands=["start"])
def start_command(message):
    global counter
    # print(message)
    source_markup = types.InlineKeyboardMarkup(row_width=2)
    source_markup_btn1 = types.InlineKeyboardButton('Документация', url='https://docs.emmet.io/')
    source_markup_btn2 = types.InlineKeyboardButton('Примеры', callback_data= 'start.example')
    source_markup_btn3 = types.InlineKeyboardButton('Шаблоны (0)', callback_data='start.templates')
    source_markup.add(source_markup_btn1, source_markup_btn2)
    source_markup.add(source_markup_btn3)
    bot.send_message(message.chat.id, f'Привет, я EmmetBot.\nЯ помогаю ускорять HTML верстку генерируя html-код из css-подобной нотации. Но проще один раз показать, чем объяснять. Хотя если вы тут вам скорее всего не нужно ничего объяснять. Если так, нажмите [шаблоны], там краткая инструкция как ими пользоваться.', reply_markup=source_markup)
    counter += 1

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        bot.answer_callback_query(call.id)
    except:
        print(call.data)
    if call.message:
        btn_group, spl, btn_data = call.data.partition('.')
        if btn_data=='example':
            bot.send_message(call.message.chat.id,'Отправьте текст примера и получите в ответ html-код\n'
                                                  '*Пример 1:*\n'
                                                  '`div#mainMenu>ul.menu>li.menuItem$*3{Пункт $}`\n'
                                                  'Сформирует заготовку для меню из 3 пунктов в виде маркированного '
                                                  'списка обернутого в div с id = "mainMenu" \n\n'
                                                  '*Пример 2:*\n'
                                                  '`html>(head>title{Пример}+style+script)+body>.header+.content+.footer`\n'
                                                  'На выходе будет простейший шаблон html документа '
                                                  'и в заголовке будет написано "Пример"\n\n'
                                                  '*Пример 3:*\n'
                                                  '`form[action="index.html"][method="POST"]>'
                                                  'label[for="username"]{Имя пользователя}+input#username+br+'
                                                  'label[for="password"]{Пароль}+input[type="password"]#password+br+'
                                                  'submit[value="Войти"]`\n'
                                                  'Самая простая форма для входа', parse_mode='Markdown')
        elif btn_data == 'templates':
            bot.send_message(call.message.chat.id, 'Тут будут шаблоны которые вы сохраните.\n'
                                                   'Пока  вас нет шаблонов\n\n'
                                                   'Чтобы сохранить шаблон отправьте после генерации html '
                                                   'команду /save Название шаблона\n'
                                                   'Чтобы удалить шаблон пришлите команду /delete Название шаблона\n'
                                                   'Список шаблонов /templates',
                                                   parse_mode='Markdown')
            # keyboard = types.InlineKeyboardMarkup(row_width=3)
            # keyboard.add(a, b, c, d, e, f, g, h, i)
            # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="X", reply_markup=keyboard)


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, '/templates - список шаблонов\n'
                                      '/example - пара примеров\n'
                                      '/docs - ссылка на документацию.', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print(message)
    try:
        bot.send_message(message.chat.id, '`'+emmet.expand(message.text)+'`', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    except (emmet.token_scanner.TokenScannerException, emmet.scanner.ScannerException):
        bot.send_message(message.chat.id, 'Выражение *' + message.text + '* не поддается расшифровке', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())



bot.polling()

import routes
