import telebot
from random import randrange

bot = telebot.TeleBot("1202416907:AAFpJendkHeeBEG_r0mvqysmhMcvPnBFxxk")
client_status = {}  # id-статус
client_base = {"Преподаватели": []}  # группа-список студентов
group_keys = {352446: "Преподаватели"}  # ключ-группа


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
                client_base[message.text] = []
                del client_status[client_id]
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
            bot.send_message(message.chat.id, 'Вы присоединились к группе \"%s\"' % group_keys[key])
        elif key in group_keys and client_id in client_base[group_keys[key]]:
            bot.send_message(message.chat.id, 'Вы уже состоите в этой группе')
        else:
            bot.send_message(message.chat.id, 'Вы ввели некорректный код')
    else:
        bot.send_message(message.chat.id,
                         'Что это? Попробуйте написать команду заново')


bot.polling()
