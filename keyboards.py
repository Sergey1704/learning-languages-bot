from telegram import InlineKeyboardButton, InlineKeyboardMarkup


SETTINGS_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('Количество слов в день', callback_data='num_of_words')],
    [InlineKeyboardButton('Часовой пояс', callback_data='timezone')],
    [InlineKeyboardButton('Время начала отправки', callback_data='start_time')],
    [InlineKeyboardButton('Время конца отправки', callback_data='end_time')],
])

NUM_OF_WORDS_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('\u25C1', callback_data='num_of_words -'),
     InlineKeyboardButton('\u25A1', callback_data='num_of_words 0'),
     InlineKeyboardButton('\u25B7', callback_data='num_of_words +')],
    [InlineKeyboardButton('Назад', callback_data='back num_of_words'),
     InlineKeyboardButton('Сохранить', callback_data='save num_of_words')],
])

TIMEZONE_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('\u25C1', callback_data='timezone -'),
     InlineKeyboardButton('\u25A1', callback_data='timezone 0'),
     InlineKeyboardButton('\u25B7', callback_data='timezone +')],
    [InlineKeyboardButton('Назад', callback_data='back timezone'),
     InlineKeyboardButton('Сохранить', callback_data='save timezone')],
])

START_TIME_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('\u25C1', callback_data='start_time h-'),
     InlineKeyboardButton('час', callback_data='start_time h0'),
     InlineKeyboardButton('\u25B7', callback_data='start_time h+')],
    [InlineKeyboardButton('\u25C1', callback_data='start_time m-'),
     InlineKeyboardButton('мин', callback_data='start_time m0'),
     InlineKeyboardButton('\u25B7', callback_data='start_time m+')],
    [InlineKeyboardButton('Назад', callback_data='back start_time'),
     InlineKeyboardButton('Сохранить', callback_data='save start_time')],
])

END_TIME_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('\u25C1', callback_data='end_time h-'),
     InlineKeyboardButton('час', callback_data='end_time h0'),
     InlineKeyboardButton('\u25B7', callback_data='end_time h+')],
    [InlineKeyboardButton('\u25C1', callback_data='end_time m-'),
     InlineKeyboardButton('мин', callback_data='end_time m0'),
     InlineKeyboardButton('\u25B7', callback_data='end_time m+')],
    [InlineKeyboardButton('Назад', callback_data='back end_time'),
     InlineKeyboardButton('Сохранить', callback_data='save end_time')],
])

SEND_WORD_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('знаю', callback_data='known'),
     InlineKeyboardButton('не знаю', callback_data='unknown')]
])
