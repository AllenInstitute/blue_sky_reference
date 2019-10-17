from flask import Flask
from celery import Celery
from workflow_engine.signatures import submit_task_signature

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://blue_sky_user:blue_sky_user@message_queue:5672'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

r = submit_task_signature.apply_async((10,))

print(r)
