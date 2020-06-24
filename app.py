import os
import time

from celery import Celery
from celery.result import AsyncResult
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'something hard to guess')


def make_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    celery_app.conf.update(flask_app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


celery = make_celery(app)


@celery.task()
def launch_new_test(tc_id):
    print(f'Provisioning environment for {tc_id}...')
    # Simulate the test execution process
    time.sleep(5)
    print(f'{tc_id} is completed!')
    return {"result": 'pass',
            "build": "1.0.0"}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.form['submit'] == 'Launch':
        tc_id = request.form['test_case_id']
        result = launch_new_test.delay(tc_id)
        summary = {"taskId": result.id,
                   "location": str(url_for('get_task_state', task_id=result.id))
                   }
        return jsonify(summary), 202


@app.route('/tasks/<string:task_id>/state')
def get_task_state(task_id):
    result = AsyncResult(task_id, app=celery)
    summary = {
        "state": result.state,
        "result": result.result,
        "id": result.id,
    }
    return jsonify(summary), 200
