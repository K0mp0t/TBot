import telebot
from random import randrange
from id import bot_id

bot = telebot.TeleBot(bot_id())


def update_dicts():
    k = open('keys.txt', 'r', encoding='utf-8')
    for line in k:
        separated_line = line.split(':')
        key = int(separated_line[0])
        value = separated_line[1].rstrip()
        group_keys[key] = value
    k.close()
    b = open('base.txt', 'r', encoding='utf-8')
    for line in b:
        separated_line = line.split(':')
        key = separated_line[0]
        values = separated_line[1].split('.')
        value = []
        for v in values:
            value.append(int(v.rstrip()))
        client_base[key] = value
    b.close()


def update_keys():
    f = open('keys.txt', 'w', encoding='utf-8')
    for item in group_keys:
        s = str(item)
        s += ':'
        s += str(group_keys.get(item))
        s += '\n'
        f.write(s)
    f.close()


def update_base():
    f = open('base.txt', 'w', encoding='utf-8')
    for item in client_base:
        s = str(item)
        s += ':'
        s += '.'.join(str(e) for e in client_base.get(item))
        s += '\n'
        f.write(s)
    f.close()


client_status = {}  # id-статус
forward_groups = {}  # id-список групп
remaining_groups = {}  # id-оставшиеся группы
confirmation_dict = {} # id-название удаляемой группы
client_base = {"Преподаватели": []}  # группа-список студентов
group_keys = {352446: "Преподаватели"}  # ключ-группа
update_dicts()


def generate_key():
    key = randrange(100000, 999999)
    if key not in client_base.keys():
        return key
    else:
        generate_key()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    client_id = message.from_user.id
    keyboard = make_keyboard_commands(client_id)
    bot.send_message(message.chat.id, help_text(client_id), reply_markup=keyboard)


@bot.message_handler(commands=['new_group'])
def generate_new_group(message):
    client_id = message.from_user.id
    if client_id in client_base[group_keys[352446]]:
        client_status[message.from_user.id] = 'g'
        bot.send_message(message.chat.id, 'Введите название группы: ')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав на это действие',
                         reply_markup=make_keyboard_commands(client_id))


@bot.message_handler(commands=['join_group'])
def join_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'j'
    bot.send_message(message.chat.id, 'Введите код для присоединения к группе')


@bot.message_handler(commands=['leave_group'])
def leave_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'l'
    keyboard = make_keyboard_groups(client_id, False)
    bot.send_message(message.chat.id, 'Введите название группы, которую хотите покинуть', reply_markup=keyboard)


@bot.message_handler(commands=['delete_group'])
def delete_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'd'
    keyboard = make_keyboard_groups(client_id, False)
    bot.send_message(message.chat.id, 'Введите название группы, которую хототие удалить', reply_markup=keyboard)


@bot.message_handler(commands=['forward_message'])
def forward_message(message):
    client_id = message.from_user.id
    client_status[client_id] = 'f'
    initialize_group_list(client_id)
    keyboard = make_keyboard_groups(client_id, True)
    bot.send_message(message.chat.id, 'Выберите группы', reply_markup=keyboard)


def clear_lists(client_id):
    del forward_groups[client_id]
    del remaining_groups[client_id]


def make_group_list(client_id):
    group_list = []
    for group in group_keys.values():
        if client_id in client_base[group] and group != 'Преподаватели':
            group_list.append(group)
    return group_list


def make_keyboard_groups(client_id, enough_all_flag):  # ?
    initialize_group_list(client_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    groups = sorted(remaining_groups[client_id])
    for i in range(0, (len(groups) // 3) + 1):
        if len(groups) - i * 3 > 2:
            keyboard.add(telebot.types.KeyboardButton(groups[i * 3]),
                         telebot.types.KeyboardButton(groups[i * 3 + 1]),
                         telebot.types.KeyboardButton(groups[i * 3 + 2]))
        elif len(groups) - i * 3 == 2:
            keyboard.add(telebot.types.KeyboardButton(groups[i * 3]),
                         telebot.types.KeyboardButton(groups[i * 3 + 1]))
        elif len(groups) - i * 3 == 1:
            keyboard.add(telebot.types.KeyboardButton(groups[i * 3]))
    if enough_all_flag:
        keyboard.add('Хватит', 'Все группы', 'Отмена')
    else:
        keyboard.add('Отмена')
    return keyboard


def make_keyboard_commands(client_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if client_id in client_base['Преподаватели']:
        keyboard.add(telebot.types.KeyboardButton('/new_group'),
                     telebot.types.KeyboardButton('/delete_group'),
                     telebot.types.KeyboardButton('/forward_message'))
    keyboard.add(telebot.types.KeyboardButton('/join_group'),
                 telebot.types.KeyboardButton('/leave_group'),
                 telebot.types.KeyboardButton('/help'))
    return keyboard


def make_keyboard_confirmation():
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Да'),
                 telebot.types.KeyboardButton('Нет'))
    return keyboard


def find_key(group_name):
    for key in group_keys.keys():
        if group_keys[key] == group_name:
            return key


def initialize_group_list(client_id):
    forward_groups[client_id] = []
    remaining_groups[client_id] = make_group_list(client_id)


def handle_forwarding(client_id, message):
    for group in forward_groups[client_id]:
        for student in client_base[group]:
            bot.forward_message(student, message.chat.id, message.message_id)
    clear_lists(client_id)


def sort_by_alphabet(input_str):
    return input_str[0]


def help_text(client_id):
    if client_id in client_base['Преподаватели']:
        return '/new_group - создать новую группу, название вводится вручную \n' \
               '/delete_group - удалить существующую группу, есть возможность выбора из предложенных групп \n' \
               '/forward_message - выбрать группы и отправить всем студентам, ' \
               'принадлежащим этим группам сообщение(отправка документов поддерживается) \n' \
               '/join_group - присоединиться к группе по коду \n' \
               '/leave_group - выйти из группы, есть возможность выбора из предложенных \n'
    else:
        return '/join_group - присоединиться к группе по коду \n' \
               '/leave_group - выйти из группы, есть возможность выбора из предложенных \n'


@bot.message_handler(content_types=['text'])
def handle_data(message):
    client_id = message.from_user.id
    keyboard = make_keyboard_commands(client_id)
    if message.text == 'Отмена':
        del client_status[client_id]
        bot.send_message(message.chat.id, 'Отменено', reply_markup=keyboard)
    elif client_id in client_status:
        if client_status[client_id] == 'g':
            if client_id in client_base[group_keys[352446]]:
                if message.text not in group_keys.values():
                    key = generate_key()
                    group_keys[key] = message.text
                    client_base[group_keys[key]] = [client_id]
                    del client_status[client_id]
                    update_keys()
                    update_base()
                    bot.send_message(message.chat.id, 'Код для присоединения к группе: %s' % key, reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id,
                                     'Такая группа уже существует, код для присоединенеия к ней: %d' % find_key(
                                         message.text), reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'У вас нет прав на это действие', reply_markup=keyboard)
        elif client_status[client_id] == 'j':
            try:
                key = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id, 'Вы ввели некорректный код', reply_markup=keyboard)
            if key in group_keys and client_id not in client_base[group_keys[key]]:
                client_base[group_keys[key]].append(client_id)
                del client_status[client_id]
                update_base()
                bot.send_message(message.chat.id, 'Вы присоединились к группе \"%s\"' % group_keys[key], reply_markup=keyboard)
            elif key in group_keys and client_id in client_base[group_keys[key]]:
                bot.send_message(message.chat.id, 'Вы уже состоите в этой группе', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'Вы ввели некорректный код', reply_markup=keyboard)
        elif client_status[client_id] == 'l':
            if message.text in client_base:
                if client_id in client_base[message.text]:
                    client_base[message.text].remove(client_id)
                    update_keys()
                    update_base()
                    bot.send_message(client_id, 'Вы успешно покинули группу \"%s\"' % message.text, reply_markup=keyboard)
                else:
                    bot.send_message(client_id, 'Вы не состоите в этой группе', reply_markup=keyboard)
            else:
                bot.send_message(client_id, 'Такой группы не существует', reply_markup=keyboard)
        elif client_status[client_id] == 'd':
            if message.text in client_base:
                if client_id in client_base[group_keys[352446]]:
                    client_status[client_id] = 'c'
                    confirmation_dict[client_id] = message.text
                    bot.send_message(client_id, 'Вы уверены?', reply_markup=make_keyboard_confirmation())
                else:
                    bot.send_message(client_id, 'У вас нет прав на это действие', reply_markup=keyboard)
            else:
                bot.send_message(client_id, 'Такой группы не существует', reply_markup=keyboard)
        elif client_status[client_id] == 'f':
            initialize_group_list(client_id)
            if message.text == 'Хватит':
                client_status[client_id] = 'fw'
                bot.send_message(message.chat.id, 'Жду от вас сообщение')
            elif message.text == 'Все группы':
                client_status[client_id] = 'fw'
                forward_groups[client_id].extend(remaining_groups[client_id])
                bot.send_message(message.chat.id, 'Жду от вас сообщение')
            elif message.text in client_base:
                forward_groups[client_id].append(message.text)
                remaining_groups[client_id].remove(message.text)
                keyboard_groups = make_keyboard_groups(client_id, True)
                bot.send_message(message.chat.id, 'ОК', reply_markup=keyboard_groups)
            elif message.text not in client_base:
                bot.send_message(message.chat.id, 'Не могу найти такой группы', reply_markup=keyboard)
        elif client_status[client_id] == 'fw':
            handle_forwarding(client_id, message)
            bot.send_message(message.chat.id, 'Сообщение успешко отправлено, вы тоже его получите', reply_markup=keyboard)
        elif client_status[client_id] == 'c':
            if message.text == 'Да':
                del client_status[client_id]
                del client_base[confirmation_dict[client_id]]
                del group_keys[find_key(confirmation_dict[client_id])]
                update_keys()
                update_base()
                bot.send_message(client_id, 'Группа успешно удалена', reply_markup=keyboard)
            else:
                del client_status[client_id]
                bot.send_message(client_id, 'Отменено', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         'Что это? Попробуйте написать команду заново', reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling(none_stop=True)
