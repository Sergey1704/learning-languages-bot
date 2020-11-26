import pytest
from re import compile
from words import translate_word, get_random_word


words = [
    ('hello', 'здравствуйте'),
    ('boy', 'мальчик'),
    ('cat', 'кошка')
]

@pytest.mark.parametrize('eng_word, expected_ru_word', words)
def test_translate_word(eng_word, expected_ru_word):
    ru_word = translate_word(eng_word)
    assert ru_word != 'не найдено'
    assert ru_word == expected_ru_word


def test_get_random_word():
    eng_word = get_random_word()
    assert eng_word != 'not found'
    assert type(eng_word) == str

    pattern = compile(r"^[a-zA-Z\-.`&]+$")
    assert pattern.match(eng_word)
