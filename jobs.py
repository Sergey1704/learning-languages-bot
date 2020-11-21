from datetime import datetime, time, timedelta
from telegram.ext import Updater, JobQueue
from database import set_to_database, get_from_database
from words import send_word


def restart_user_jobs(chat_id: int, chat_data: dict, job_queue: JobQueue):
    current_jobs = job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    settings = chat_data.get('settings')
    num_of_words = settings.get('num_of_words')
    start_time = time.fromisoformat(settings.get('start_time'))
    end_time = time.fromisoformat(settings.get('end_time'))

    time_interval = None
    days = 0 if start_time <= end_time else 1
    if num_of_words > 0:
        time_interval = timedelta(days=days, hours=end_time.hour - start_time.hour,
                                  minutes=end_time.minute - start_time.minute) / num_of_words

    job_times = []
    for i in range(num_of_words):
        job_datetime = datetime.combine(datetime.utcnow(), start_time) + i * time_interval
        job_time = job_datetime.timetz()

        job_queue.run_daily(send_word, job_time, context={'chat_id': chat_id}, name=str(chat_id),
                            job_kwargs={'misfire_grace_time': 10*60})

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
                                        job_kwargs={'misfire_grace_time': 10*60})

            count_jobs += 1
        count_users += 1

    print(f'Restored {count_jobs} jobs for {count_users} users.')

    return count_jobs
