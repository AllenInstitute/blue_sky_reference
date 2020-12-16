from workflow_engine.ingest.ingest_client import IngestClient

client = IngestClient('blue_sky__blue', 'mock_workflow')
client.configure_celery_app()

calibration_ids = dict()

for offset in range(2):
    response = client.send({ 'offset': (offset - 100 * 0.001) }, fix_option=['calibration'])
    calibration_ids[offset] = response['calibration_id']

for measurement in range(20):
    calibration_index = int(measurement / 10)
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



