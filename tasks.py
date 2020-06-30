import os
import time

from celery import Celery

celery_app = Celery(
    'celery_app',
    backend=os.getenv('REDIS_URI', 'redis://localhost:6379/0'),
    broker=os.getenv('REDIS_URI', 'redis://localhost:6379/0')
)


@celery_app.task()
def launch_new_test(tc_id):
    print(f'Provisioning environment for {tc_id}...')
    # Simulate the test execution process
    time.sleep(30)
    print(f'{tc_id} is completed!')
    return {"result": 'pass',
            "testCaseId": tc_id
            }
