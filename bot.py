from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import Update
from datetime import time
from database import get_from_database
from persistence import MongoPersistence
from jobs import start_saved_jobs

import json

def handle_callback(update: Update, context: CallbackContext):
    message = update.effective_message
    eng_word, ru_word = [line.split(': ')[-1] for line in message.text.split('\n')]

    is_known = update.callback_query.data
    user_name = update.effective_user.first_name
    knew = 'знает' if is_known == '1' else 'не знает'
    verdict = f'Пользователь {user_name} {knew} слово {eng_word}'
    print(verdict)

    query = update.callback_query
    query.answer()

    new_message_text = message.text
    if is_known == '1':
        new_message_text = f'~{new_message_text}~'

    query.edit_message_text(text=new_message_text, parse_mode='MarkdownV2', reply_markup=None)
    return

def handle_start(update: Update, context: CallbackContext):

    print('Start command')

    num_of_words = 10
    start_time = time(22, 55).isoformat()
    end_time = time(23, 00).isoformat()

    settings = {'num_of_words': num_of_words, 'start_time': start_time, 'end_time': end_time}

    context.chat_data['settings'] = settings

def handle_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    context.bot.send_message(chat_id, text)

    print('--------------jobs---------------')
    print(json.dumps(get_from_database('jobs'), indent=2))
    print('------------chat_data------------')
    print(json.dumps(get_from_database('chat_data'), indent=2))
    print('---------------------------------')


if __name__ == '__main__':
    with open('token.txt') as file:
        TOKEN = file.readline().strip()

    persistence = MongoPersistence(store_user_data=False, store_bot_data=False)
    updater = Updater(TOKEN, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher
    persistence.job_queue = updater.job_queue
    start_saved_jobs(updater)

    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_echo))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    updater.start_polling()
    updater.idle()
