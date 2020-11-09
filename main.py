from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, time, timedelta
from random import choice

words = {'Algebra': 'алгебра',
        'Archaeology': 'археология',
        'Art': 'изобразительное искусство',
        'Biology': 'биология',
        'Botany': 'ботаника',
        'Calculus': 'математический анализ',
        'Chemistry': 'химия',
        'Computer science': 'информатика',
        'Drama': 'драматургия',
        'Economics': 'экономика',
        'English': 'английский',
        'French': 'французский',
        'Geography': 'география',
        'Geology': 'геология',
        'Geometry': 'геометрия',
        'German': 'немецкий',
        'Gym': 'гимнастика',
        'Health': 'охрана здоровья',
        'History': 'история',
        'Home economics': 'домоводство',
        'Keyboarding': 'машинопись',
        'Language arts': 'словесность',
        'Literature': 'литература',
        'Math': 'математика',
        'Mathematics': 'математика',
        'Music': 'музыка',
        'Pe': 'физкультура',
        'Physical education': 'физкультура',
        'Physics': 'физика',
        'Psychology': 'психология',
        'Reading': 'чтение',
        'Science': 'наука',
        'Social studies': 'социология, обществознание',
        'World geography': 'мировая география',
        'Writing': 'письменность, письменная речь'}

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
    eng_word = choice(list(words.keys()))
    message = f'ENG: {eng_word}\nRUS: {words[eng_word]}'
    context.bot.send_message(chat_id, message, reply_markup=InlineKeyboardMarkup(keyboard))

def handle_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    num_of_words = 10
    start_time = time(8, 00)
    end_time = time(20, 00)
    time_interval = timedelta(hours=end_time.hour - start_time.hour,
                              minutes=end_time.minute - start_time.minute) / num_of_words

    for i in range(num_of_words):
        job_datetime = datetime.combine(datetime.utcnow(), start_time) + i * time_interval
        job_time = job_datetime.timetz()
        context.job_queue.run_daily(notify_user, job_time, context={'chat_id': chat_id}, name=str(chat_id))

def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    context.bot.send_message(chat_id, text)

if __name__ == '__main__':
    # TODO подгружать токен из файла
    token = '1475171950:AAHrKfne24sx-TppHxig-eeJtS_bY9sUn94'

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))
    updater.start_polling()
