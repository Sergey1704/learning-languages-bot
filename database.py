from collections import defaultdict
from pymongo import MongoClient


database = None

def get_database():
    global database

    if not database:
        client = MongoClient(host='localhost', port=27017)
        database = client.bot_database.users

    return database

def get_from_database(field_name: str) -> dict:
    mongo = get_database()
    result_dict = defaultdict(dict)

    users = mongo.find({}, ['chat_id', field_name])
    for user in users:
        key = user['chat_id']
        value = user[field_name]
        result_dict[key] = value

    return result_dict

def set_to_database(chat_id: int, field_name: str, data: any):
    mongo = get_database()
    result = mongo.update_one({'chat_id': chat_id}, {'$set': {field_name: data}}, upsert=True)

    return result
