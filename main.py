import config
import telebot
from telebot import types  # кнопки
from string import Template

bot = telebot.TeleBot(config.token)  # токен

user_dict = {}


class User:
    def __init__(self, club):
        self.club = club

        # с помощью списка и цикла, который по нему идёт, прописываем атрибуты в кострукторе класса
        keys = ['discipline', 'mode', 'team_name', 'players_nicknames', 'captain_phone', 'decision']

        for key in keys:
            self.key = None


# приветствие, а так же при вводе /help, /start
@bot.message_handler(commands=['help', 'start'])
def greeting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('/about')
    itembtn2 = types.KeyboardButton('/reg')
    markup.add(itembtn1, itembtn2)

    bot.send_message(message.chat.id, "Здравствуйте "
                     + message.from_user.first_name
                     + ", я бот 🤖, который поможет вам в регистрации на турнир от *название компании*, по различным "
                       "игровым "
                       "дисциплинам. 🎮", reply_markup=markup)


# информация о компании
@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id,
                     "Сеть компьютерных клубов города Москвы, созданные игроками с 20 летним опытом для "
                     "того, чтобы ты получил максимальное удовольствие от любимой игры!")


# регистрация на турнир
@bot.message_handler(commands=['reg'])
def user_reg(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Клуб - адрес клуба')
    itembtn2 = types.KeyboardButton('Клуб - адрес клуба')
    itembtn3 = types.KeyboardButton('Клуб - адрес клуба')

    markup.add(itembtn1, itembtn2, itembtn3)

    msg = bot.send_message(message.chat.id, 'Выберите удобный клуб:', reply_markup=markup)
    bot.register_next_step_handler(msg, discipline)


# дисциплина
def discipline(message):
    chat_id = message.chat.id
    user_dict[chat_id] = User(message.text)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('Dota 2')
    itembtn2 = types.KeyboardButton('CS GO')
    itembtn3 = types.KeyboardButton('Fortnite')
    itembtn4 = types.KeyboardButton('CS 1.6')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    msg = bot.send_message(chat_id, 'Выберите дисциплину:', reply_markup=markup)
    bot.register_next_step_handler(msg, mode)


# выбор игрового режима
def mode(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.discipline = message.text

    if user.discipline == 'Fortnite':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('1x1')
        itembtn2 = types.KeyboardButton('4x4')
        markup.add(itembtn1, itembtn2)

        msg = bot.send_message(chat_id, 'Выберите игровой режим:', reply_markup=markup)
        bot.register_next_step_handler(msg, team_name)

    elif user.discipline == 'Dota 2':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('1x1')
        itembtn2 = types.KeyboardButton('5x5')
        markup.add(itembtn1, itembtn2)

        msg = bot.send_message(chat_id, 'Выберите игровой режим:', reply_markup=markup)
        bot.register_next_step_handler(msg, team_name)

    elif user.discipline == 'CS GO' or 'CS 1.6':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('2x2')
        itembtn2 = types.KeyboardButton('5x5')
        markup.add(itembtn1, itembtn2)

        msg = bot.send_message(chat_id, 'Выберите игровой режим:', reply_markup=markup)
        bot.register_next_step_handler(msg, team_name)


# название команды
def team_name(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.mode = message.text

    # удалить старую клавиатуру
    markup = types.ReplyKeyboardRemove(selective=False)

    msg = bot.send_message(chat_id, 'Введите название команды:', reply_markup=markup)
    bot.register_next_step_handler(msg, players_nicknames)


# ники игроков
def players_nicknames(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.team_name = message.text

    msg = bot.send_message(chat_id, 'Введите ники игроков через запятую.\nПример: GoldenLosos, _Matrix_, PopCorn_IGM')
    bot.register_next_step_handler(msg, captain_phone)


# телефон капитана
def captain_phone(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.players_nicknames = message.text

    msg = bot.send_message(chat_id, 'Введите номер телефона капитана  в формате: "8XXXXXXXXXX":')
    bot.register_next_step_handler(msg, verification)


# формирование заявки
def verification(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.captain_phone = message.text

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        itembtn1 = types.KeyboardButton('Принять')
        itembtn2 = types.KeyboardButton('Отклонить')

        markup.add(itembtn1, itembtn2)

        msg = bot.send_message(chat_id, get_reg_data(user, '', message.from_user.first_name + ', ваша заявка сформирована.\nЕсли всё правильно - нажмите "Принять".\nПри наличае ошибок  - нажмите "Отменить".\n'),
                         parse_mode="Markdown", reply_markup=markup)
        bot.register_next_step_handler(msg, consideration)

    except ValueError as e:
        msg = bot.reply_to(message, 'Некорректный ввод. Проверьте правильность набора номера. Номер должен содержать только цифры.')
        bot.register_next_step_handler(msg, verification)


def get_reg_data(user, title, name):
    t = Template('$title *$name* \nКлуб: *$user_club* \nДисциплина: *$user_discipline* \nИгровой режим: *$user_mode* '
                 '\nКоманда: *$user_team_name* \nНики игроков: *$user_players_nicknames* \nТелефон капитана: '
                 '*$user_captain_phone*')

    return t.substitute({
        'title': title,
        'name': name,
        'user_club': user.club,
        'user_discipline': user.discipline,
        'user_mode': user.mode,
        'user_team_name': user.team_name,
        'user_players_nicknames': user.players_nicknames,
        'user_captain_phone': user.captain_phone

    })


# рассмотрение заявки
def consideration(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text == 'Принять':
        bot.send_message(chat_id, get_reg_data(user, '', '"Этот вид заявки будет отправлен в нужный чат"\n'),
                         parse_mode="Markdown")
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Ваша заявка отклонена', reply_markup=markup)


# произвольный набор текста
@bot.message_handler(content_types=["text"])
def send_help(message):
    # удалить старую клавиатуру
    markup = types.ReplyKeyboardRemove(selective=False)

    bot.send_message(message.chat.id, 'О нас - /about\nРегистрация - /reg\nПомощь - /help', reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True)
