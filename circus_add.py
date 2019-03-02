from circus.client import CircusClient

client = CircusClient(endpoint='tcp://127.0.0.1:5655')

command = '/opt/conda/envs/circus/bin/python -c \'from time import sleep; sleep(60)\''
name = 'dummy'


for i in range(50):
    print(client.call(
    {
        "command": "add",
        "properties": {
            "cmd": command,
            "name": name + str(i),
            "options": {
            "copy_env": True,
            },
            "start": True
        }
    }))
