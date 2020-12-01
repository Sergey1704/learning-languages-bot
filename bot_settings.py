# pylint: disable=unused-argument

from telegram import Update
from telegram.ext import CallbackContext

from timezone import convert_time_from_utc, convert_time_to_utc, timezone_difference
from keyboards import (
    SETTINGS_KEYBOARD,
    NUM_OF_WORDS_KEYBOARD,
    TIMEZONE_KEYBOARD,
    START_TIME_KEYBOARD,
    END_TIME_KEYBOARD,
)


def handle_settings(update: Update, context: CallbackContext):
    print('Settings command')
    chat_id = update.message.chat_id

    message = '<b>Настройки</b>\n\u200C'
    context.bot.send_message(chat_id, message, parse_mode='HTML', reply_markup=SETTINGS_KEYBOARD)


def num_of_words_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff in ('num_of_words', '0'):
        num_of_words = context.chat_data.get('settings').get('num_of_words')
    else:
        num_of_words = int(callback_message.split()[-1])
        if diff == '+':
            num_of_words += 1
        elif diff == '-':
            num_of_words -= 1
        if not 0 <= num_of_words <= 50:
            num_of_words %= 51
        num_of_words = str(num_of_words)

    new_message = f'<b>Настройки</b>\n\nКоличество слов в день:\n\n{num_of_words}'
    update.callback_query.edit_message_text(new_message, parse_mode='HTML', reply_markup=NUM_OF_WORDS_KEYBOARD)


def timezone_callback(update: Update, context: CallbackContext):
    timezones = [
        'UTC−12:00', 'UTC−11:00', 'UTC−10:00', 'UTC−09:30', 'UTC−09:00', 'UTC−08:00',
        'UTC−07:00', 'UTC−06:00', 'UTC−05:00', 'UTC−04:00', 'UTC−03:30', 'UTC−03:00',
        'UTC−02:00', 'UTC−01:00', 'UTC±00:00', 'UTC+01:00', 'UTC+02:00', 'UTC+03:00',
        'UTC+03:30', 'UTC+04:00', 'UTC+04:30', 'UTC+05:00', 'UTC+05:30', 'UTC+05:45',
        'UTC+06:00', 'UTC+06:30', 'UTC+07:00', 'UTC+08:00', 'UTC+08:45', 'UTC+09:00',
        'UTC+09:30', 'UTC+10:00', 'UTC+10:30', 'UTC+11:00', 'UTC+12:00', 'UTC+12:45',
        'UTC+13:00', 'UTC+14:00'
    ]

    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff in ('timezone', '0'):
        timezone = context.chat_data.get('settings').get('timezone')
    else:
        timezone = callback_message.split()[-1]
        index = timezones.index(timezone)
        if diff == '+':
            index += 1
        elif diff == '-':
            index -= 1
        if not 0 <= index < len(timezones):
            return
        timezone = timezones[index]

    new_message = f'<b>Настройки</b>\n\nЧасовой пояс:\n\n{timezone}'
    update.callback_query.edit_message_text(new_message, parse_mode='HTML', reply_markup=TIMEZONE_KEYBOARD)


def make_time_callback_operation(setting_name: str, update: Update, context: CallbackContext) -> str:
    callback_data = update.callback_query.data
    callback_message = update.effective_message.text

    diff = callback_data.split()[-1]
    if diff in (setting_name, 'h0', 'm0'):
        time = context.chat_data.get('settings').get(setting_name)
        timezone = context.chat_data.get('settings').get('timezone')
        time = convert_time_from_utc(time, timezone)

        if diff == setting_name:
            return time

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


def start_time_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    start_time = make_time_callback_operation('start_time', update, context)

    new_message = f'<b>Настройки</b>\n\nВремя начала отправки слов:\n\n{start_time}\n'
    update.callback_query.edit_message_text(new_message, parse_mode='HTML', reply_markup=START_TIME_KEYBOARD)


def end_time_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    end_time = make_time_callback_operation('end_time', update, context)

    new_message = f'<b>Настройки</b>\n\nВремя конца отправки слов:\n\n{end_time}\n'
    update.callback_query.edit_message_text(new_message, parse_mode='HTML', reply_markup=END_TIME_KEYBOARD)


def back_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    callback_data = update.callback_query.data
    func = callback_data.split()[0]

    new_message = '<b>Настройки</b>\n\u200C'
    if func == 'save':
        new_message += '\n<i>Настройки обновлены.</i>'
    update.callback_query.edit_message_text(new_message, parse_mode='HTML', reply_markup=SETTINGS_KEYBOARD)


def save_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    callback_data = update.callback_query.data
    callback_message = update.effective_message.text
    settings = context.chat_data['settings']

    setting_name = callback_data.split()[-1]
    value = callback_message.split()[-1]

    if setting_name == 'num_of_words':
        num_of_words = int(value)
        settings[setting_name] = num_of_words

    elif setting_name in ('start_time', 'end_time'):
        time = value
        timezone = settings.get('timezone')
        utc_time = convert_time_to_utc(time, timezone)

        if (setting_name == 'start_time' and settings['end_time'] == utc_time
                or setting_name == 'end_time' and settings['start_time'] == utc_time):
            return None

        settings[setting_name] = utc_time

    elif setting_name == 'timezone':
        new_timezone = value
        current_timezone = settings.get('timezone')
        convert_timezone = timezone_difference(new_timezone, current_timezone)

        settings['timezone'] = new_timezone
        settings['start_time'] = convert_time_to_utc(settings['start_time'], convert_timezone)
        settings['end_time'] = convert_time_to_utc(settings['end_time'], convert_timezone)

    return back_callback(update, context)
