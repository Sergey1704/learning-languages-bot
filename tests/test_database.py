import pytest

from database import get_database, get_from_database, set_to_database


def test_get_database():
    db1 = get_database()
    db2 = get_database()
    assert db1 is not None
    assert db1 == db2


data_for_database_examples = [
    (3, '132test321*/as--df', 'test_value'),
    (-178, '132test321*/as--df', True),
    (99, '132test321*/as--df', [1]),
    (-19815, '132test321*/as--df', {}),
    (0, '132test321*/as--df', {'5': [], 'sdibu': 7, 'x': {}}),
]


@pytest.mark.parametrize('chat_id, field_name, data', data_for_database_examples)
def test_get_from_database(chat_id, field_name, data):
    database = get_database()
    database.update_one({'chat_id': chat_id}, {'$set': {field_name: data}}, upsert=True)
    result = get_from_database(field_name)[chat_id]
    assert result == data


@pytest.mark.parametrize('chat_id, field_name, data', data_for_database_examples)
def test_set_to_database(chat_id, field_name, data):
    set_to_database(chat_id, field_name, data)
    database = get_database()
    result = database.find_one({'chat_id': chat_id}, ['chat_id', field_name])
    assert result[field_name] == data
