from telegram.ext import Updater, JobQueue
from datetime import datetime, time, timedelta
from database import set_to_database, get_from_database

from random import choice
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


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


def notify_user(context: CallbackContext):
    chat_id = context.job.context['chat_id']
    eng_word, ru_word = choice(list(words.items()))
    message = f'ENG: {eng_word}\nRUS: {ru_word}'

    keyboard = [[InlineKeyboardButton('знаю', callback_data='1'), InlineKeyboardButton('не знаю', callback_data='0')]]
    context.bot.send_message(chat_id, message, reply_markup=InlineKeyboardMarkup(keyboard))


def restart_user_jobs(chat_id: int, chat_data: dict, job_queue: JobQueue):
    current_jobs = job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    settings = chat_data.get('settings')
    num_of_words = settings.get('num_of_words')
    start_time = time.fromisoformat(settings.get('start_time'))
    end_time = time.fromisoformat(settings.get('end_time'))

    time_interval = timedelta(hours=end_time.hour - start_time.hour,
                              minutes=end_time.minute - start_time.minute) / num_of_words

    job_times = []
    for i in range(num_of_words):
        job_datetime = datetime.combine(datetime.utcnow(), start_time) + i * time_interval
        job_time = job_datetime.timetz()

        job_queue.run_daily(notify_user, job_time, context={'chat_id': chat_id}, name=str(chat_id))

        job_times.append({'time': job_time.isoformat()})

    set_to_database(chat_id, 'jobs', job_times)


def start_saved_jobs(updater: Updater):
    user_jobs = get_from_database('jobs')

    count_users, count_jobs = 0, 0
    for chat_id, jobs in user_jobs.items():
        for job in jobs:
            job_time = time.fromisoformat(job.get('time'))
            updater.job_queue.run_daily(notify_user, job_time, context={'chat_id': chat_id}, name=str(chat_id))

            count_jobs += 1
        count_users += 1

    print(f'Restored {count_jobs} jobs for {count_users} users.')

    return count_jobs
