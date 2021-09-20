from workflow_engine.ingest.ingest_client import IngestClient

client = IngestClient('blue_sky__blue', 'mock_workflow')
client.configure_celery_app()

GROUP_COUNT = 5
GROUP_SIZE = 2
OBSERVATION_COUNT=GROUP_SIZE*GROUP_COUNT
OBSERVATIONS_PER_CALIBRATION=2
CALIBRATION_COUNT=int(OBSERVATION_COUNT/OBSERVATIONS_PER_CALIBRATION)

calibration_ids = dict()

for offset in range(CALIBRATION_COUNT):
    response = client.send({ 'offset': (offset - 100 * 0.001) }, fix_option=['calibration'])
    calibration_ids[offset] = response['calibration_id']

for measurement in range(OBSERVATION_COUNT):
    calibration_index = int(measurement / GROUP_SIZE)
    print(calibration_index)
    calibration_id = calibration_ids[calibration_index]

    client.send(
        {
            'arg1': measurement,
            'arg2': 'something',
            'arg3': 'whatever',
            'calibration_id': calibration_id
        },
        fix_option=['observation']
    )
