# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import json
import logging
import os
from urllib import parse

import telegram
import requests
from fuzzywuzzy import process
from telegram.ext import CommandHandler, CallbackQueryHandler, Updater, MessageHandler, Filters, InlineQueryHandler

import voice_generator
from chat_wheel import Voice

dota2_wheel_file = open("voicelines/dota2_chat_wheels.json", "r")
voice_lines: dict = json.loads("".join(dota2_wheel_file.readlines()))
voice_line_names = list(voice_lines.keys())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

endpoint = "https://chat-wheels-bot.herokuapp.com/"


def search_voice_lines(query) -> [Voice]:
    r = requests.get("{endpoint}/search?query={query}".format_map({
        'endpoint': endpoint,
        'query': query
    }))
    return list(map(lambda item: Voice(item), r.json))

def fuzzy_search_by_name(update: telegram.Update, context):
    if update.message:  # your bot can receive updates without messages
        # Reply to the message
        message: telegram.Message = update.message

        best_results = search_voice_lines(message.text)

        if len(best_results) is 0:
            message.reply_text("Nothing found 🌻")
            return

        keyboard_items = []
        for voice in best_results:
            keyboard_items.append([
                telegram.InlineKeyboardButton(voice.name, callback_data=voice.id)
            ])

        message.reply_text("Select one of found 🌻:", reply_markup=telegram.InlineKeyboardMarkup(keyboard_items))


def start(update: telegram.Update, context):
    update.message.reply_text("Now just send my voice line name u would like to find 🌻")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def quick_search(update: telegram.Update, context):
    query = update.inline_query.query

    best_results = search_voice_lines(query)
    results = []

    for id, voice in enumerate(best_results):
        results.append(telegram.InlineQueryResultVoice(id, voice.url, voice.name, caption=voice.name))

    update.inline_query.answer(results)


def send_voice_line(update: telegram.Update, context):
    voice_line_id = int(update.callback_query.data)
    voice_line_name = voice_line_names[voice_line_id]
    voice_line_url = voice_lines[voice_line_name]

    update.callback_query.answer()

    file = voice_generator.make_ogg_file_path(voice_line_name,
                                              os.path.join(os.getcwd(), "voicelines", "files"))

    if not os.path.exists(file):
        voice_generator.generate_ogg_from_source(voice_line_url, file)

    update.callback_query.message.reply_voice(open(file, "rb"), caption=voice_line_name)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("905206939:AAH_3CFuxuYfKiYGo-7U5toBQ65SrR9Ggqg", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, fuzzy_search_by_name))
    updater.dispatcher.add_handler(CallbackQueryHandler(send_voice_line))
    updater.dispatcher.add_handler(InlineQueryHandler(quick_search))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
