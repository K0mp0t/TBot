import telebot
from random import randrange

bot = telebot.TeleBot("1202416907:AAFpJendkHeeBEG_r0mvqysmhMcvPnBFxxk")


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


@bot.message_handler(content_types=['text'])
def handle_data(message):
    client_id = message.from_user.id
    if message.text == 'Отмена':
        del client_status[client_id]
        bot.send_message(message.chat.id, 'Отменено')
    elif client_id in client_status and client_status[client_id] == 'g':
        if client_id in client_base[group_keys[352446]]:
            if message.text not in group_keys.values():
                key = generate_key()
                group_keys[key] = message.text
                client_base[group_keys[key]] = []
                del client_status[client_id]
                update_keys()
                bot.send_message(message.chat.id, 'Код для присоединения к группе: %s' % key)
            else:
                bot.send_message(message.chat.id, 'Такая группа уже существует, попробуйте еще раз')
        else:
            bot.send_message(message.chat.id, 'У вас нет прав на это действие')
    elif client_id in client_status and client_status[client_id] == 'j':
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
    elif client_id in client_status and client_status[client_id] == 'l':
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
    elif client_id in client_status and client_status[client_id] == 'd':
        if message.text in client_base:
            if client_id in client_base[group_keys[352446]]:
                del client_base[message.text]
                update_keys()
                update_base()
                bot.send_message(client_id, 'Группа успешно удалена')
            else:
                bot.send_message(client_id, 'У вас нет прав на это действие')
        else:
            bot.send_message(client_id, 'Такой группы не существует')
    else:
        bot.send_message(message.chat.id,
                         'Что это? Попробуйте написать команду заново')


bot.polling()
