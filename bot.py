#!/usr/bin/env python3
"""
d
"""
from threading import current_thread
from LaTeX2IMG.LaTeX2IMG import latex2img
from telebot import apihelper
import telebot
from telebot import logging
from telebot import types
import os

TOKEN = ''

chat_id = os.environ["CHAT_ID"]

with open("token.txt", "r") as file:
    TOKEN = file.readline().strip()

bot = telebot.TeleBot(TOKEN)
if os.environ["USE_PROXY"]:
    apihelper.proxy = {
        'https': os.environ["PROXY_URL"],
        'http': os.environ["PROXY_URL"]
    }

def send_equation(chat_id, text):
    try:
        bot.send_chat_action(chat_id, 'upload_document')

        filename = 'resultado' + current_thread().name

        latex2img(text, filename, 'webp')

        with open(filename + '.webp', 'rb') as equation:
            bot.send_sticker(chat_id, equation)
        os.remove(filename + '.webp')
    except Exception as exc:
        print(exc)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "You can convert LaTeX expression using\n\n/latex expression")
    except Exception as exc:
        print(exc)

@bot.message_handler(commands=['latex'])
def send_expression(message):
    try:
        chat_id = message.chat.id
        text = message.text[7:]
        if text and text != "LaTeX2IMGbot":
            send_equation(chat_id, text)
        else:
            new_msg = bot.reply_to(message, "Please send your expression with \"/latex expression\"")
    except Exception as exc:
        bot.reply_to(message, "Some unexpected error. " + exc.__str__())

@bot.inline_handler(lambda query: query.query)
def query_inline(inline_query):
    try:
        filename = 'resultado' + current_thread().name

        latex2img(inline_query.query, filename, 'webp')
        m = 0
        with open(filename + '.webp', 'rb') as equation:
            m = bot.send_sticker(chat_id, equation)
        os.remove(filename + '.webp')
        results = [types.InlineQueryResultCachedSticker('1', m.sticker.file_id)]
        bot.answer_inline_query(inline_query.id, results, cache_time=1.5)
    except Exception:
        print(Exception)

logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%m-%d %H:%M:%S')
ch = logging.FileHandler("log.txt")
logger.addHandler(ch)
logger.setLevel(logging.INFO)  # or use logging.INFO
ch.setFormatter(formatter)

bot.polling()
