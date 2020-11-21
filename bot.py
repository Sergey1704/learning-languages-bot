from environs import Env
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from persistence import MongoPersistence
from jobs import start_saved_jobs
from words import word_callback


def convert_time_from_utc(utc_time: str, timezone: str) -> str:
    utc_time = utc_time[:5]
    utc_hours, utc_minutes = [int(t) for t in utc_time.split(':')]
    sign = 1 if timezone[3] == '+' else -1
    tz_hours, tz_minutes = [int(t) for t in timezone[-5:].split(':')]
    hours = utc_hours + sign * tz_hours
    minutes = utc_minutes + sign * tz_minutes
    if not (0 <= minutes <= 59):
        hours += minutes // 60
        minutes %= 60
    if not (0 <= hours <= 23):
        hours %= 24
    time = ':'.join([str(hours).zfill(2), str(minutes).zfill(2)])

    return time

def convert_time_to_utc(time: str, timezone: str) -> str:
    if timezone[3] == '+':
        inverse_timezone = timezone.replace('+', '-')
    else:
        inverse_timezone = timezone.replace('-', '+')
    utc_time = convert_time_from_utc(time, inverse_timezone)
    utc_time += ':00'

    return utc_time

def timezone_difference(timezone1: str, timezone2: str) -> str:
    sign1 = 1 if timezone1[3] == '+' else -1
    sign2 = 1 if timezone2[3] == '+' else -1
    tz1_hours, tz1_minutes = [int(t) for t in timezone1[-5:].split(':')]
    tz2_hours, tz2_minutes = [int(t) for t in timezone2[-5:].split(':')]
    tz_minutes = sign1 * (tz1_hours * 60 + tz1_minutes) - sign2 * (tz2_hours * 60 + tz2_minutes)
    sign = '+' if tz_minutes >= 0 else '-'
    tz_hours, tz_minutes = abs(tz_minutes) // 60, abs(tz_minutes) % 60
    timezone = 'UTC' + sign + ':'.join([str(tz_hours).zfill(2), str(tz_minutes).zfill(2)])

    return timezone

def back_and_save_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    func, setting_name = callback_data.split()
    if func == 'save':
        value = callback_message.split()[-1]

        if setting_name == 'num_of_words':
            num_of_words = int(value)
            context.chat_data['settings'][setting_name] = num_of_words

        elif setting_name == 'start_time' or setting_name == 'end_time':
            time = value
            timezone = context.chat_data.get('settings').get('timezone')
            utc_time = convert_time_to_utc(time, timezone)
            context.chat_data['settings'][setting_name] = utc_time

        elif setting_name == 'timezone':
            new_timezone = value
            current_timezone = context.chat_data.get('settings').get('timezone')
            convert_timezone = timezone_difference(new_timezone, current_timezone)

            current_start_time = context.chat_data.get('settings').get('start_time')
            new_start_time = convert_time_to_utc(current_start_time, convert_timezone)
            current_end_time = context.chat_data.get('settings').get('end_time')
            new_end_time = convert_time_to_utc(current_end_time, convert_timezone)

            context.chat_data['settings']['timezone'] = new_timezone
            context.chat_data['settings']['start_time'] = new_start_time
            context.chat_data['settings']['end_time'] = new_end_time

    new_message = '*Настройки*\n\u200C'
    if func == 'save':
        new_message += '\n_Настройки обновлены\._'
    keyboard = [[InlineKeyboardButton('Количество слов в день', callback_data='num_of_words')],
                [InlineKeyboardButton('Часовой пояс', callback_data='timezone')],
                [InlineKeyboardButton('Время начала отправки', callback_data='start_time')],
                [InlineKeyboardButton('Время конца отправки', callback_data='end_time')]]

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2',
                                            reply_markup=InlineKeyboardMarkup(keyboard))

    return

def empty_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()
    return

def timezone_callback(update: Update, context: CallbackContext):
    timezones = ['UTC−12:00', 'UTC−11:00', 'UTC−10:00', 'UTC−09:30', 'UTC−09:00', 'UTC−08:00', 'UTC−07:00',
                 'UTC−06:00', 'UTC−05:00', 'UTC−04:00', 'UTC−03:30', 'UTC−03:00', 'UTC−02:00', 'UTC−01:00',
                 'UTC±00:00', 'UTC+01:00', 'UTC+02:00', 'UTC+03:00', 'UTC+03:30', 'UTC+04:00', 'UTC+04:30',
                 'UTC+05:00', 'UTC+05:30', 'UTC+05:45', 'UTC+06:00', 'UTC+06:30', 'UTC+07:00', 'UTC+08:00',
                 'UTC+08:45', 'UTC+09:00', 'UTC+09:30', 'UTC+10:00', 'UTC+10:30', 'UTC+11:00', 'UTC+12:00',
                 'UTC+12:45', 'UTC+13:00', 'UTC+14:00']

    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff == 'timezone' or diff == '0':
        timezone = context.chat_data.get('settings').get('timezone')
    else:
        timezone = callback_message.split()[-1]
        index = timezones.index(timezone)
        if diff == '+':
            index += 1
        elif diff == '-':
            index -= 1
        if not (0 <= index < len(timezones)):
            return
        timezone = timezones[index]

    timezone = timezone.replace('+', '\\+').replace('-', '\\-')
    new_message = f'*Настройки*\n\nЧасовой пояс:\n\n{timezone}'
    keyboard = [[InlineKeyboardButton('\u25C1', callback_data='timezone -'),
                 InlineKeyboardButton('\u25A1', callback_data='timezone 0'),
                 InlineKeyboardButton('\u25B7', callback_data='timezone +')],
                [InlineKeyboardButton('Назад', callback_data='back timezone'),
                 InlineKeyboardButton('Сохранить', callback_data='save timezone')]]

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2',
                                            reply_markup=InlineKeyboardMarkup(keyboard))

    return

def num_of_words_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff == 'num_of_words' or diff == '0':
        num_of_words = context.chat_data.get('settings').get('num_of_words')
    else:
        num_of_words = int(callback_message.split()[-1])
        if diff == '+':
            num_of_words += 1
        elif diff == '-':
            num_of_words -= 1
        if not (0 <= num_of_words <= 50):
            return
        num_of_words = str(num_of_words)

    new_message = f'*Настройки*\n\nКоличество слов в день:\n\n{num_of_words}'
    keyboard = [[InlineKeyboardButton('\u25C1', callback_data='num_of_words -'),
                 InlineKeyboardButton('\u25A1', callback_data='num_of_words 0'),
                 InlineKeyboardButton('\u25B7', callback_data='num_of_words +')],
                [InlineKeyboardButton('Назад', callback_data='back num_of_words'),
                 InlineKeyboardButton('Сохранить', callback_data='save num_of_words')]]

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2',
                                            reply_markup=InlineKeyboardMarkup(keyboard))

    return

def make_time_callback_operation(setting_name: str, update: Update, context: CallbackContext) -> str:
    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff == setting_name or diff == 'h0' or diff == 'm0':
        time = context.chat_data.get('settings').get(setting_name)
        timezone = context.chat_data.get('settings').get('timezone')
        time = convert_time_from_utc(time, timezone)
        if diff == 'h0' or diff == 'm0':
            saved_hours, saved_minutes = [int(t) for t in time.split(':')]
            current_time = callback_message.split()[-1]
            hours, minutes = [int(t) for t in current_time.split(':')]
            if diff == 'h0':
                hours = saved_hours
            elif diff == 'm0':
                minutes = saved_minutes
            time = ':'.join([str(hours).zfill(2), str(minutes).zfill(2)])
    else:
        time = callback_message.split()[-1]
        hours, minutes = [int(t) for t in time.split(':')]
        if diff == 'h+':
            hours += 1
        elif diff == 'h-':
            hours -= 1
        elif diff == 'm+':
            minutes += 5
        elif diff == 'm-':
            minutes -= 5
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            hours %= 24
            minutes %= 60
        time = ':'.join([str(hours).zfill(2), str(minutes).zfill(2)])

    return time


def end_time_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    end_time = make_time_callback_operation('end_time', update, context)

    new_message = f'*Настройки*\n\nВремя конца отправки слов:\n\n{end_time}\n'
    keyboard = [[InlineKeyboardButton('\u25C1', callback_data='end_time h-'),
                 InlineKeyboardButton('час', callback_data='end_time h0'),
                 InlineKeyboardButton('\u25B7', callback_data='end_time h+')],
                [InlineKeyboardButton('\u25C1', callback_data='end_time m-'),
                 InlineKeyboardButton('мин', callback_data='end_time m0'),
                 InlineKeyboardButton('\u25B7', callback_data='end_time m+')],
                [InlineKeyboardButton('Назад', callback_data='back end_time'),
                 InlineKeyboardButton('Сохранить', callback_data='save end_time')]]

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2',
                                            reply_markup=InlineKeyboardMarkup(keyboard))

    return


def start_time_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    start_time = make_time_callback_operation('start_time', update, context)

    new_message = f'*Настройки*\n\nВремя начала отправки слов:\n\n{start_time}\n'
    keyboard = [[InlineKeyboardButton('\u25C1', callback_data='start_time h-'),
                 InlineKeyboardButton('час', callback_data='start_time h0'),
                 InlineKeyboardButton('\u25B7', callback_data='start_time h+')],
                [InlineKeyboardButton('\u25C1', callback_data='start_time m-'),
                 InlineKeyboardButton('мин', callback_data='start_time m0'),
                 InlineKeyboardButton('\u25B7', callback_data='start_time m+')],
                [InlineKeyboardButton('Назад', callback_data='back start_time'),
                 InlineKeyboardButton('Сохранить', callback_data='save start_time')]]

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2',
                                            reply_markup=InlineKeyboardMarkup(keyboard))

    return


def handle_start(update: Update, context: CallbackContext):
    print('Start command')
    if not context.chat_data:
        default_settings = {'num_of_words': 10, 'timezone': 'UTC+03:00',
                            'start_time': '07:30:00', 'end_time': '17:30:00'}
        context.chat_data['settings'] = default_settings


def handle_settings(update: Update, context: CallbackContext):
    print('Settings command')

    chat_id = update.message.chat_id
    message = '*Настройки*\n\u200C'
    keyboard = [[InlineKeyboardButton('Количество слов в день', callback_data='num_of_words')],
                [InlineKeyboardButton('Часовой пояс', callback_data='timezone')],
                [InlineKeyboardButton('Время начала отправки', callback_data='start_time')],
                [InlineKeyboardButton('Время конца отправки', callback_data='end_time')]]
    context.bot.send_message(chat_id, message, parse_mode='MarkdownV2', reply_markup=InlineKeyboardMarkup(keyboard))


def handle_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    context.bot.send_message(chat_id, text)

    #print(get_word_translation('party'))

    # print('------------chat_data------------')
    # print(json.dumps(context.chat_data, indent=2))
    # print('---------------------------------')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env.str('TOKEN')

    persistence = MongoPersistence(store_user_data=False, store_bot_data=False)
    updater = Updater(token, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher
    persistence.job_queue = updater.job_queue
    start_saved_jobs(updater)

    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(CommandHandler('settings', handle_settings))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_echo))

    dispatcher.add_handler(CallbackQueryHandler(word_callback, pattern=r'.*known$'))
    dispatcher.add_handler(CallbackQueryHandler(num_of_words_callback, pattern=r'^num_of_words.*'))
    dispatcher.add_handler(CallbackQueryHandler(timezone_callback, pattern=r'^timezone.*'))
    dispatcher.add_handler(CallbackQueryHandler(start_time_callback, pattern=r'^start_time.*'))
    dispatcher.add_handler(CallbackQueryHandler(end_time_callback, pattern=r'^end_time.*'))
    dispatcher.add_handler(CallbackQueryHandler(back_and_save_callback, pattern=r'^(save.*|back.*)'))
    dispatcher.add_handler(CallbackQueryHandler(empty_callback, pattern=r'^0$'))

    updater.start_polling()
    updater.idle()
