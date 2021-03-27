from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import telebot
from telebot import types
import emmet
from threading import Thread
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import random, string


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."
bootstrap = Bootstrap(app)

bot = telebot.TeleBot(app.config['TGBOTAPI_TOKEN'])

@bot.message_handler(commands=["start"])
def start_command(message):
    tg_user = TgUser.query.filter_by(tg_id=message.from_user.id).first()
    if tg_user is None and message.from_user.is_bot == False:
        # новый пользователь
        print('Add user ' + message.from_user.username)
        tg_user = TgUser(tg_id=message.from_user.id, first_name=message.from_user.first_name,
                         last_name=message.from_user.last_name, username=message.from_user.username,
                         chat_id=message.chat.id)
        db.session.add(tg_user)
        db.session.commit()
    TgSessions.get_session(message.from_user.id)
    # print(message)
    source_markup = types.InlineKeyboardMarkup(row_width=2)
    source_markup_btn1 = types.InlineKeyboardButton('Документация', url='https://docs.emmet.io/')
    source_markup_btn2 = types.InlineKeyboardButton('Примеры', callback_data= 'start.example')
    source_markup_btn3 = types.InlineKeyboardButton('Шаблоны', callback_data='start.templates')
    source_markup.add(source_markup_btn1, source_markup_btn2)
    source_markup.add(source_markup_btn3)
    bot.send_message(message.chat.id, f'Привет, я EmmetBot.\nЯ помогаю ускорять HTML верстку генерируя html-код из '
                                      f'css-подобной нотации. Но проще один раз показать, чем объяснять.\n'
                                      f'Нажми [Примеры] или /examples\n'
                                      f'Если тебе знаком Emmet и не нужно ничего объяснять узнайте больше '
                                      f'про сохранение шаблонов:\n'
                                      f'Нажмит [Шаблоны] или введи /templates',
                     reply_markup=source_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        bot.answer_callback_query(call.id)
    except:
        print(call.data)
    if call.message:
        btn_group, spl, btn_data = call.data.partition('.')
        if btn_group == 'start':
            if btn_data=='example':
                examples_command(call.message)
            elif btn_data == 'templates':
                templates_command(call.message)

        elif btn_group == 'place_tpl':
            if int(btn_data)>0:
                tpl = EmmetTemplates.query.filter(EmmetTemplates.tgUser_tg_id==call.message.chat.id)\
                    .filter(EmmetTemplates.id==int(btn_data)).first()
                if tpl is not None:
                    kbd = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
                    kbd.add(types.KeyboardButton(tpl.template))
                    kbd.add(types.KeyboardButton('/delete '+tpl.title), types.KeyboardButton('/templates'))
                    bot.send_message(call.message.chat.id, f'*{tpl.title}*\n`{tpl.template}`', parse_mode='Markdown',
                                     reply_markup=kbd)


@bot.message_handler(commands=["examples"])
def examples_command(message):
    bot.send_message(message.chat.id, 'Отправьте текст примера и получите в ответ html-код\n'
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

@bot.message_handler(commands=["templates"])
def templates_command(message):
    tpls = EmmetTemplates.query.filter_by(tgUser_tg_id=message.chat.id).all()
    if tpls is not None and len(tpls) > 0:
        tpl_cnt = f'Сохраненных шаблонов: {len(tpls)}\n\n'
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        for t in tpls:
            keyboard.add(types.InlineKeyboardButton(t.title, callback_data= f'place_tpl.{t.id}'))
    else:
        tpl_cnt='Пока у вас нет шаблонов\n\n'
        keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f'Тут будут шаблоны которые вы сохраните.\n{tpl_cnt}'
                                      'Чтобы сохранить emmet-выражение как шаблон выберите сообщение, нажмите ответить '
                                      'и напишите команду \n*/save Название шаблона*\n'
                                      'Чтобы удалить шаблон пришлите команду \n*/delete Название шаблона*\n'
                                      'Список шаблонов */templates*',
                     parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(commands=["help"])
def help_command(message):
    TgSessions.get_session(message.from_user.id)
    bot.send_message(message.chat.id, '/templates - список шаблонов\n'
                                      '/example - пара примеров\n'
                                      '/docs - ссылка на документацию.', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["save"])
def help_command(message):
    TgSessions.get_session(message.from_user.id)

    print("Message text:"+message.text)
    print("Reply to:"+message.reply_to_message.text)
    cmd, spl, title = message.text.partition(' ')
    if title != "":
        try:
            emmet.expand(message.reply_to_message.text)
            em_tpl = EmmetTemplates(tgUser_tg_id=message.from_user.id, title=title,
                                    template=message.reply_to_message.text)
            db.session.add(em_tpl)
            db.session.commit()
            bot.send_message(message.chat.id, f'Шаблон *{title}* сохранен', parse_mode='Markdown',
                             reply_markup=types.ReplyKeyboardRemove())
        except:
            bot.send_message(message.chat.id, 'Некорректное Emmet-выражение', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, 'Шаблону нужен заголовок. Выберите сообщение с Emmet-выражением, '
                                          'нажмите Ответить и в качестве команды напишите */save Заголовок*',
                         parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["delete"])
def help_command(message):
    TgSessions.get_session(message.from_user.id)

    print("Message text:"+message.text)
    cmd, spl, title = message.text.partition(' ')
    if title != "":
        try:
            em_tpl = EmmetTemplates.query.filter(EmmetTemplates.tgUser_tg_id==message.from_user.id)\
                .filter(EmmetTemplates.title==title).delete()
            # db.session.delete()
            db.session.commit()
            if em_tpl>0:
                bot.send_message(message.chat.id, f'Шаблон *{title}* удален', parse_mode='Markdown',
                             reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(message.chat.id, f'Шаблон *{title}* не найден', parse_mode='Markdown',
                             reply_markup=types.ReplyKeyboardRemove())
        except:
            bot.send_message(message.chat.id, 'Ошибка удаления шаблона', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, 'Укажите заголовок шаблона который нужно удалить. '
                                          'Используйте команду  */delete Заголовок*',
                         parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['getpass'])
def getpass(message):
    s = string.ascii_lowercase + string.ascii_uppercase + string.digits
    passw = ''.join(random.sample(s, 10))
    auth = TgAuth(tgUser_id=message.from_user.id)
    auth.set_password(passw)
    db.session.add(auth)
    db.session.commit()
    bot.send_message(message.chat.id, '*Данные для входа*\n'
                                      f'ID: {auth.id}\nПароль: {passw}\n'
                                      'У вас 1 минута для входа.', parse_mode='Markdown')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    TgSessions.get_session(message.from_user.id)
    print(message)
    try:
        bot.send_message(message.chat.id, '`'+emmet.expand(message.text)+'`', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    except (emmet.token_scanner.TokenScannerException, emmet.scanner.ScannerException):
        bot.send_message(message.chat.id, 'Выражение *' + message.text + '* не поддается расшифровке', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())


Thread(target=bot.polling, args=()).start()
# bot.polling()

import routes
from models import TgUser, TgSessions, EmmetTemplates, TgAuth

