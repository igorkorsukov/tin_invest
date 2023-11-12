

# bot = telebot.TeleBot(TOKEN)

# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     if message.text == "Привет":
#         bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
#     elif message.text == "/help":
#         bot.send_message(message.from_user.id, "Напиши привет")
#     else:
#         bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

# bot.polling(none_stop=True, interval=0)        

import os
import time
import signal

from tinkoff.invest import Client
import telebot;

import modules.bonds_divergence as bonds_divergence

TIN_TOKEN = os.environ["INVEST_TOKEN"]
TELE_TOKEN = os.environ["DIVERGENCE_BOT_TOKEN"]

NOTIFY_DIV_MIN = 1.0 # %
NOTIFY_DIV_CHANGE = 0.2 # %

bot = telebot.TeleBot(TELE_TOKEN) 

running = True

def users(bot):
    us = set()
    updates = bot.get_updates()
    for u in updates:
        if u.message and u.message.text == "/start":
            us.add(u.message.chat.id)
    return us

def send_message_to_all(bot, message):
    us = users(bot)
    for u in us:
        bot.send_message(u, message)

def signal_handler(signum, frame):
    global running
    running = False

def formatMsg(divinfo):
    msg = ""
    msg += "[" + divinfo.bond1 + "] delta: " + str(divinfo.delta1) + "%\n"
    msg += "[" + divinfo.bond2 + "] delta: " + str(divinfo.delta2) + "%\n"   
    msg += "divergence: " + str(divinfo.divergence) + "%"
    return msg

def main():

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    with Client(TIN_TOKEN) as client: 

        div = bonds_divergence.divergence(client) 
        print(formatMsg(div))
        send_message_to_all(bot, formatMsg(div))

        lastDiv = div.divergence

        # loop
        counter = 0
        while(running):

            if counter % 5 == 0:
                div = bonds_divergence.divergence(client) 
                if abs(div.divergence) > NOTIFY_DIV_MIN and abs(lastDiv - div.divergence) > NOTIFY_DIV_CHANGE:
                    print(formatMsg(div))
                    send_message_to_all(bot, formatMsg(div))
                    lastDiv = div.divergence

            time.sleep(1)
            counter += 1

if __name__ == "__main__":
    main()