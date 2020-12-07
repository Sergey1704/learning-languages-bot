from random import choice

from environs import Env
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from jobs import start_saved_jobs
from persistence import MongoPersistence
from words import word_callback
from bot_settings import (
    handle_settings,
    num_of_words_callback,
    timezone_callback,
    start_time_callback,
    end_time_callback,
    back_callback,
    save_callback,
)


SET_NUMBER, ANSWERING = range(2)


def handle_test(update: Update, context: CallbackContext):
    print('Test command')
    chat_id = update.message.chat_id
    max_num = len(context.chat_data['words']['known'])

    test_start_param = {
        'started': True,
        'num_of_words': 0,
        'current_number': 1,
        'current_word': '',
    }
    context.user_data.update({'test': test_start_param})

    message = f'<b>Тест</b>\n\nВведи количество слов (макс. {max_num}):'
    context.bot.send_message(chat_id, message, parse_mode='HTML')

    return SET_NUMBER


def handle_stop_test(update: Update, context: CallbackContext):
    print('Stop command')
    chat_id = update.message.chat_id
    message = 'Тест завершен.'

    context.bot.send_message(chat_id, message)
    context.user_data['test']['started'] = False

    return ConversationHandler.END


def set_number_test(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    str_number = update.message.text

    try:
        number = int(str_number)
        if not 0 < number <= len(context.chat_data['words']['known']):
            raise ValueError

        context.user_data['test']['num_of_words'] = number
        context.bot.send_message(chat_id, 'Тест начинается...\n\nЧтобы закончить тест в любой момент, напиши /stop.')

        return answer_test(update, context)

    except ValueError:
        message = 'Некорректный ввод. :(\nПопробуй еще раз.'
        context.bot.send_message(chat_id, message)

        return SET_NUMBER


def answer_test(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    words = context.chat_data['words']
    test = context.user_data['test']

    num_of_words = test['num_of_words']
    current_number = test['current_number']
    current_word = test['current_word']

    if current_number != 1:
        user_translation = update.message.text
        correct_translation = words['known'][current_word]

        if user_translation.strip().lower() == correct_translation.strip().lower():
            message = 'Правильно! :)'
            context.bot.send_message(chat_id, message)

            words['known'].pop(current_word, None)
            words['well-known'][current_word] = correct_translation
        else:
            message = f'Неправильно. :(\nВерный ответ: {correct_translation}'
            context.bot.send_message(chat_id, message)

            words['known'].pop(current_word, None)
            words['unknown'][current_word] = correct_translation

        if current_number > num_of_words:
            return handle_stop_test(update, context)

    all_known_words = list(words['known'].keys())
    part_for_test = all_known_words[: num_of_words - current_number + 1]
    word = choice(part_for_test)

    context.user_data['test']['current_word'] = word
    context.user_data['test']['current_number'] += 1

    message = f'#{current_number}\nНапишите перевод слова:\n\n{word}'
    context.bot.send_message(chat_id, message)

    return ANSWERING


def handle_start(update: Update, context: CallbackContext):
    print('Start command')

    if not context.chat_data:
        default_chat_data = {
            'settings': {
                'num_of_words': 10,
                'timezone': 'UTC+03:00',
                'start_time': '07:30:00',
                'end_time': '17:30:00',
            },
            'words': {'sent': {}, 'unknown': {}, 'known': {}, 'well-known': {}},
        }
        context.chat_data.update(default_chat_data)

    chat_id = update.message.chat_id

    message = ('<b>Привет!</b> С моей помощью ты сможешь выучить много новых английских слов.\n\n'
               'Каждый день я буду отправлять тебе несколько слов с переводом. Для каждого '
               'из них ты можешь отметить, знаешь ты его или нет.\n\n'
               'В любой момент ты можешь провести тест (/test) на знание слов, которые ты отметил знакомыми. '
               'В случае правильного ответа соответствующее слово больше никогда не встретится в '
               'ежедневной рассылке. Если же твой перевод будет неверным, то через несколько дней '
               'это слово с переводом встретится тебе снова.\n\n'
               'Изменить параметры ежедневной рассылки можно в настройках (/settings).\n\n'
               'Основные команды можно найти в списке команд (/help).')

    context.bot.send_message(chat_id, message, parse_mode='HTML')


def handle_help(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    message = ('<b>Список команд</b>\n\n'
               '/start - Основная информация\n'
               '/help - Список команд\n'
               '/settings - Настройки рассылки\n'
               '/test - Тест на знание слов')

    context.bot.send_message(chat_id, message, parse_mode='HTML')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env.str('TOKEN')

    persistence = MongoPersistence(store_user_data=False, store_bot_data=False)
    updater = Updater(token, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher
    persistence.job_queue = updater.job_queue
    start_saved_jobs(updater)

    test_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('test', handle_test)],
        states={
            SET_NUMBER: [CommandHandler('stop', handle_stop_test), MessageHandler(Filters.text, set_number_test)],
            ANSWERING: [CommandHandler('stop', handle_stop_test), MessageHandler(Filters.text, answer_test)],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.all, handle_stop_test)]
        },
        fallbacks=[CommandHandler('stop', handle_stop_test)],
        conversation_timeout=10 * 60
    )
    dispatcher.add_handler(test_conv_handler)

    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(CommandHandler('help', handle_help))
    dispatcher.add_handler(CommandHandler('settings', handle_settings))

    dispatcher.add_handler(CallbackQueryHandler(word_callback, pattern=r'.*known$'))
    dispatcher.add_handler(CallbackQueryHandler(num_of_words_callback, pattern=r'^num_of_words.*'))
    dispatcher.add_handler(CallbackQueryHandler(timezone_callback, pattern=r'^timezone.*'))
    dispatcher.add_handler(CallbackQueryHandler(start_time_callback, pattern=r'^start_time.*'))
    dispatcher.add_handler(CallbackQueryHandler(end_time_callback, pattern=r'^end_time.*'))
    dispatcher.add_handler(CallbackQueryHandler(back_callback, pattern=r'^back.*'))
    dispatcher.add_handler(CallbackQueryHandler(save_callback, pattern=r'^save.*'))

    updater.start_polling()
    updater.idle()
