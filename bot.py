from copy import copy
from os import environ
from threading import Thread
from time import sleep

import schedule
import telebot

from stores import OnTheBus, Cosmic, Geekach, Bookovka

list_of_stores = [OnTheBus(), Cosmic(), Geekach(), Bookovka()]
TOKEN = environ['TOKEN']
bot = telebot.TeleBot(TOKEN)


def create_filtered_comics(search_term):
    filtered_comics = {}
    for store in list_of_stores:
        filtered_comics.setdefault(store.shop_name, store.comics_filter(search_term))
    return filtered_comics


def create_message(filtered_comics):
    result_messages = []
    message = ''
    for store in filtered_comics:
        if filtered_comics.get(store):
            message += f'\n\n{store}:'
            for comic in filtered_comics.get(store):
                message += f'\n\n{comic.get("name")}: {comic.get("source")}'
                if len(message) > 3800:
                    result_messages.append(copy(message))
                    message = ''
    result_messages.append(message)
    if not result_messages[0]:
        return ["Sorry, we can't find anything"]
    else:
        return result_messages


@bot.message_handler(commands='start')
def start(message):
    bot.send_message(message.chat.id, 'Hi, what are you searching ?')


@bot.message_handler(content_types='text')
def main_function(message):
    message_list = create_message(create_filtered_comics(message.text))
    for message_ in message_list:
        bot.send_message(message.chat.id, message_)


def update_comics_lists():
    for store in list_of_stores:
        store.update_comics_list()


def run_update_function():
    schedule.every().day.at('03:00').do(update_comics_lists)

    while True:
        schedule.run_pending()
        sleep(59)


update_comics_lists()
t = Thread(target=run_update_function)
t.start()
bot.polling(none_stop=True, interval=0)
