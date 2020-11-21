from copy import deepcopy
from collections import defaultdict
from telegram.ext import DictPersistence
from database import get_from_database, set_to_database
from jobs import restart_user_jobs


class MongoPersistence(DictPersistence):
    def __init__(self, *args, job_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_queue = job_queue

    def get_chat_data(self):
        if not self.chat_data:
            self._chat_data = get_from_database('chat_data')

        return deepcopy(self.chat_data)

    def update_chat_data(self, chat_id: int, data: dict):
        if self._chat_data is None:
            self._chat_data = defaultdict(dict)
        if self._chat_data.get(chat_id) == data:
            return
        if self._chat_data.get(chat_id) is None or self._chat_data.get(chat_id).get('settings') != data.get('settings'):
            restart_user_jobs(chat_id, data, self.job_queue)

        self._chat_data[chat_id] = data
        set_to_database(chat_id, 'chat_data', data)
