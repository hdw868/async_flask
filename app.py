import os

from celery.result import AsyncResult
from flask import Flask, render_template, request, jsonify, url_for

from tasks import celery_app, launch_new_test

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'something hard to guess')


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
    result = AsyncResult(task_id, app=celery_app)
    summary = {
        "state": result.state,
        "result": result.result,
        "id": result.id,
    }
    return jsonify(summary), 200
