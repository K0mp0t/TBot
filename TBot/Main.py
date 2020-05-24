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
client_base = {"Преподаватели": []}  # группа-список студентов
group_keys = {352446: "Преподаватели"}  # ключ-группа
update_dicts()


def generate_key():
    key = randrange(100000, 999999)
    if key not in client_base.keys():
        return key
    else:
        generate_key()


@bot.message_handler(commands=['new_group'])
def generate_new_group(message):
    client_id = message.from_user.id
    if client_id in client_base[group_keys[352446]]:
        client_status[message.from_user.id] = 'g'
        bot.send_message(message.chat.id, 'Введите название группы: ')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав на это действие')


@bot.message_handler(commands=['join_group'])
def join_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'j'
    bot.send_message(message.chat.id, 'Введите код для присоединения к группе')


@bot.message_handler(commands=['leave_group'])
def leave_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'l'
    bot.send_message(message.chat.id, 'Введите название группы, которую хотите покинуть')


@bot.message_handler(commands=['delete_group'])
def delete_group(message):
    client_id = message.from_user.id
    client_status[client_id] = 'd'
    bot.send_message(message.chat.id, 'Введите название группы, которую хототие удалить')


@bot.message_handler(commands=['forward_message'])
def forward_message(message):
    client_id = message.from_user.id
    client_status[client_id] = 'f'
    initialize_group_list(client_id)
    keyboard = make_keyboard(client_id)
    bot.send_message(message.chat.id, 'Выберите группы', reply_markup=keyboard)


def clear_lists(client_id):
    del forward_groups[client_id]
    del remaining_groups[client_id]


def make_group_list(client_id):
    group_list = []
    for group in group_keys.values():
        if client_id in client_base[group]:
            group_list.append(group)
    return group_list


def make_keyboard(client_id):  # ?
    initialize_group_list(client_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
    for group in remaining_groups[client_id]:
        keyboard.add(group)
    keyboard.add('Хватит')
    keyboard.add('Все группы')

    return keyboard


def find_key(group_name):
    for key in group_keys.keys():
        if group_keys[key] == group_name:
            return key


def initialize_group_list(client_id):
    if client_id not in forward_groups:
        forward_groups[client_id] = []
        remaining_groups[client_id] = make_group_list(client_id)
    else:
        pass


def handle_forwarding(client_id, message):
    for group in forward_groups[client_id]:
        for student in client_base[group]:
            bot.forward_message(student, message.chat.id, message.message_id)
    clear_lists(client_id)


@bot.message_handler(content_types=['text'])
def handle_data(message):
    client_id = message.from_user.id
    if message.text == 'Отмена':
        del client_status[client_id]
        bot.send_message(message.chat.id, 'Отменено')
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
                    bot.send_message(message.chat.id, 'Код для присоединения к группе: %s' % key)
                else:
                    bot.send_message(message.chat.id,
                                     'Такая группа уже существует, код для присоединенеия к ней: %d' % find_key(
                                         message.text))
            else:
                bot.send_message(message.chat.id, 'У вас нет прав на это действие')
        elif client_status[client_id] == 'j':
            try:
                key = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id, 'Вы ввели некорректный код')
            if key in group_keys and client_id not in client_base[group_keys[key]]:
                client_base[group_keys[key]].append(client_id)
                del client_status[client_id]
                update_base()
                bot.send_message(message.chat.id, 'Вы присоединились к группе \"%s\"' % group_keys[key])
            elif key in group_keys and client_id in client_base[group_keys[key]]:
                bot.send_message(message.chat.id, 'Вы уже состоите в этой группе')
            else:
                bot.send_message(message.chat.id, 'Вы ввели некорректный код')
        elif client_status[client_id] == 'l':
            if message.text in client_base:
                if client_id in client_base[message.text]:
                    client_base[message.text].remove(client_id)
                    update_keys()
                    update_base()
                    bot.send_message(client_id, 'Вы успешно покинули группу \"%s\"' % message.text)
                else:
                    bot.send_message(client_id, 'Вы не состоите в этой группе')
            else:
                bot.send_message(client_id, 'Такой группы не существует')
        elif client_status[client_id] == 'd':
            if message.text in client_base:
                if client_id in client_base[group_keys[352446]]:
                    del client_base[message.text]
                    del group_keys[find_key(message.text)]
                    update_keys()
                    update_base()
                    bot.send_message(client_id, 'Группа успешно удалена')
                else:
                    bot.send_message(client_id, 'У вас нет прав на это действие')
            else:
                bot.send_message(client_id, 'Такой группы не существует')
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
                keyboard = make_keyboard(client_id)
                bot.send_message(message.chat.id, 'ОК', reply_markup=keyboard)
            elif message.text not in client_base:
                bot.send_message(message.chat.id, 'Не могу найти такой группы')
        elif client_status[client_id] == 'fw':
            handle_forwarding(client_id, message)
    else:
        bot.send_message(message.chat.id,
                         'Что это? Попробуйте написать команду заново')


bot.polling()
