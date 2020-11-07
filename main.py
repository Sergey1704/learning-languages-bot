from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

words = {'hello': 'привет',
         'cat': 'кот',
         'suka': 'сука',
         'kekw': 'кек',
         'pycharm': 'пайчарм'}

keyboard = [[InlineKeyboardButton('знаю', callback_data='1'), InlineKeyboardButton('не знаю', callback_data='0')]]

def handle_callback(update: Update, context: CallbackContext):
    word = update.callback_query.message.text
    is_known = update.callback_query.data
    user_name = update.callback_query.message.chat.first_name
    knew = 'знает' if is_known == '1' else 'не знает'
    verdict = f'Пользователь {user_name} {knew} слово {word}'
    print(verdict)

def notify_user(context: CallbackContext):
    chat_id = context.job.context['chat_id']
    context.bot.send_message(chat_id, words['hello'], reply_markup=InlineKeyboardMarkup(keyboard))

def handle_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    num_of_words = len(words)
    interval = 60 / num_of_words
    context.job_queue.run_repeating(notify_user, interval, first=0, last=interval*num_of_words, context={'chat_id': chat_id})

def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    context.bot.send_message(chat_id, text)

if __name__ == '__main__':
    token = '1475171950:AAHrKfne24sx-TppHxig-eeJtS_bY9sUn94'

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))
    updater.start_polling()
