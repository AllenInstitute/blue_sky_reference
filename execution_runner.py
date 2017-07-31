from celery import Celery
import os
import pika
import paramiko

MESSAGE_QUEUE_HOST = 'TODO_SET_MESSAGE_QUEUE_HOST'
MESSAGE_QUEUE_NAME = 'TODO_SET_MESSAGE_QUEUE_NAME'

app = Celery('execution_runner', backend='rpc://', broker='pyamqp://guest@' + MESSAGE_QUEUE_HOST + '//')

app.conf.task_default_queue = 'celery'

SUCCESS_EXIT_CODE = 0
ERROR_EXIT_CODE = 1
ZERO = 0
FIRST = 0

@app.task
def check_environment_variables():
	if "QMASTER_USERNAME" not in os.environ:
		raise Exception('Please set QMASTER_USERNAME environment variable')

	if "QMASTER_PASSWORD" not in os.environ:
		raise Exception('Please set QMASTER_PASSWORD environment variable')

@app.task
def run_pbs(full_executable, task_id):
	exit_code = SUCCESS_EXIT_CODE

	try:
		check_environment_variables()

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect("qmaster", username=os.environ['QMASTER_USERNAME'], password=os.environ['QMASTER_PASSWORD'])

		stdin, stdout, stderr = client.exec_command(full_executable)
		stdout_message = stdout.readlines()

		pbs_id = stdout_message[FIRST].strip().replace(".corp.alleninstitute.org", "")

		publish_message('PBS_ID', task_id, pbs_id)

	except Exception as e:
		print('something went wrong: ' + str(e))
		exit_code = ERROR_EXIT_CODE
		publish_message('FAILED_EXECUTION', task_id)

	return exit_code

@app.task
def run_normal(full_executable, task_id, logfile):
	exit_code = os.system(full_executable)

	if exit_code == SUCCESS_EXIT_CODE:
		publish_message('FINISHED_EXECUTION', task_id)

		with open(logfile, "a") as log:
			log.write("SUCCESS - execution finished successfully for task " + str(task_id))

	else:
		publish_message('FAILED_EXECUTION', task_id)

		with open(logfile, "a") as log:
			log.write("FAILURE - execution failed for task " + str(task_id))

	return exit_code

@app.task
def publish_message(body, task_id, optional_body=None):
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=MESSAGE_QUEUE_HOST))
	channel = connection.channel()
	channel.queue_declare(queue=MESSAGE_QUEUE_NAME)
	if optional_body != None:
		channel.basic_publish(exchange='', routing_key=MESSAGE_QUEUE_NAME, body= body + ',' + str(task_id) + ',' + str(optional_body))
	else:
		channel.basic_publish(exchange='', routing_key=MESSAGE_QUEUE_NAME, body= body + ',' + str(task_id))
	connection.close()

@app.task
def cancel_task(use_pbs, p_id):
	if use_pbs:
		try:
			pbs_id = p_id
			executable = 'qdel ' + str(pbs_id)
			exit_code = os.system(executable)
		except Exception as e:
			print('something went wrong')

@app.task
def run_celery_task(full_executable, task_id, logfile, use_pbs):
	exit_code = SUCCESS_EXIT_CODE

	try:
		publish_message('RUNNING', task_id)

		if(use_pbs):
			exit_code = run_pbs(full_executable, task_id)
		else:
			exit_code = run_normal(full_executable, task_id, logfile)

	except Exception as e:
		exit_code = ERROR_EXIT_CODE
		publish_message('FAILED_EXECUTION', task_id)

	return exit_code

