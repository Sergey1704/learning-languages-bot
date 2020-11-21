from environs import Env
from time import sleep
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from googletrans import Translator

auth_token = ''

def get_abbyy_auth_token() -> str:
    env = Env()
    env.read_env()
    api_key = env.str('ABBYY_API_KEY')

    headers_auth = {'Authorization': 'Basic ' + api_key}
    auth = requests.post(url='https://developers.lingvolive.com/api/v1.1/authenticate', headers=headers_auth)

    global auth_token
    auth_token = auth.text

    return auth_token

def get_abbyy_word_translation(eng_word: str) -> str:
    global auth_token

    for _ in range(10):
        try:
            headers = {'Authorization': 'Bearer ' + auth_token}
            params = {'text': eng_word, 'srcLang': 1033, 'dstLang': 1049}
            response = requests.get('https://developers.lingvolive.com/api/v1/Minicard', headers=headers, params=params)
            response.raise_for_status()
            ru_word = response.json().get('Translation').get('Translation')
            return ru_word
        except requests.exceptions.HTTPError:
            get_abbyy_auth_token()

def translate_word(eng_word: str) -> str:
    for t in range(20):
        translator = Translator(service_urls=['translate.google.com'])
        try:
            ru_word = translator.translate(eng_word, src='en', dest='ru').text
            return ru_word
        except Exception as e:
            print(f'--{t}--TRANSLATE word delay')
            sleep(5)

    return 'не найдено'

def get_random_word() -> str:
    env = Env()
    env.read_env()
    api_key = env.str('WORDNIK_API_KEY')

    params = {'minCorpusCount': 5000, 'minDictionaryCount': 10, 'hasDictionaryDef': True, 'api_key': api_key,
              'excludePartOfSpeech': 'interjection,pronoun,preposition,abbreviation,affix,article,auxiliary-verb,'
                                     'conjunction,definite-article,family-name,given-name,noun-posessive,'
                                     'past-participle,phrasal-prefix,proper-noun,proper-noun-plural,'
                                     'proper-noun-posessive,suffix'}
    for t in range(20):
        try:
            response = requests.get('https://api.wordnik.com/v4/words.json/randomWord', params=params)
            response.raise_for_status()
            word = response.json().get('word')
            return word
        except requests.exceptions.HTTPError:
            print(f'--{t}--random word delay')
            sleep(5)

    return 'not found'


def send_word(context: CallbackContext):
    chat_id = context.job.context['chat_id']
    eng_word = get_random_word().lower()
    ru_word = translate_word(eng_word).lower()

    message = f'ENG: {eng_word}\nRUS: {ru_word}'

    keyboard = [[InlineKeyboardButton('знаю', callback_data='known'),
                 InlineKeyboardButton('не знаю', callback_data='unknown')]]
    context.bot.send_message(chat_id, message, reply_markup=InlineKeyboardMarkup(keyboard))


def word_callback(update: Update, context: CallbackContext):
    update.callback_query.answer()

    message = update.effective_message.text
    eng_word, ru_word = [line.split(': ')[-1] for line in message.split('\n')]

    is_known = update.callback_query.data
    user_name = update.effective_user.first_name
    knew = 'знает' if is_known == 'known' else 'не знает'
    verdict = f'Пользователь {user_name} {knew} слово {eng_word}'
    print(verdict)

    new_message = message.replace('-', '\-')
    if is_known == 'known':
        new_message = f'~{new_message}~'

    update.callback_query.edit_message_text(new_message, parse_mode='MarkdownV2', reply_markup=None)

    return
