from datetime import datetime, time, timedelta
from typing import Dict, Union

from telegram.ext import JobQueue, Updater

from database import get_from_database, set_to_database
from words import send_word


def restart_user_jobs(chat_id: int, chat_data: Dict[str, Dict[str, Union[int, str, dict]]], job_queue: JobQueue):
    current_jobs = job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    settings = chat_data.get('settings')
    assert isinstance(settings, dict)

    num_of_words = settings.get('num_of_words')
    str_start_time = settings.get('start_time')
    str_end_time = settings.get('end_time')
    assert isinstance(num_of_words, int)
    assert isinstance(str_start_time, str)
    assert isinstance(str_end_time, str)

    start_time = time.fromisoformat(str_start_time)
    end_time = time.fromisoformat(str_end_time)

    time_interval = timedelta()
    days = 0 if start_time <= end_time else 1
    if num_of_words > 0:
        time_interval = timedelta(days=days, hours=end_time.hour - start_time.hour,
                                  minutes=end_time.minute - start_time.minute) / num_of_words

    job_times = []
    for i in range(num_of_words):
        job_datetime = datetime.combine(datetime.utcnow(), start_time) + i * time_interval
        job_time = job_datetime.timetz()

        job_queue.run_daily(send_word, job_time, context={'chat_id': chat_id}, name=str(chat_id),
                            job_kwargs={'misfire_grace_time': 20 * 60})

        job_times.append({'time': job_time.isoformat()})

    set_to_database(chat_id, 'jobs', job_times)

    return num_of_words


def start_saved_jobs(updater: Updater):
    user_jobs = get_from_database('jobs')

    count_users, count_jobs = 0, 0
    for chat_id, jobs in user_jobs.items():
        for job in jobs:
            job_time = time.fromisoformat(job.get('time'))
            updater.job_queue.run_daily(send_word, job_time, context={'chat_id': chat_id}, name=str(chat_id),
                                        job_kwargs={'misfire_grace_time': 20 * 60})
            count_jobs += 1
        count_users += 1

    print(f'Restored {count_jobs} jobs for {count_users} users.')

    return count_jobs
