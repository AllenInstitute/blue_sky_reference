TEST_CONFIG_YAML_ONE_NODE = u"""
executables:
    mock:
        name: 'Mock Executable'
        path: '/data/aibstemp/timf/example_data/bin/mock_executable'
        pbs_queue: 'lims2'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
workflows:
    test_workflow:
        ingest: "blue_sky.strategies.mock_ingest.MockIngest"
        states:
            - key: "start"
              label: "Start"
              class: "blue_sky.strategies.mock_analyze.MockAnalyze"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
        graph:
            - [ "start", [ ] ]
"""

TEST_CONFIG_YAML_TWO_NODES = u"""
executables:
    mock:
        name: 'Mock Executable'
        path: 'python'
        args: [ '-m', 'mock_executable' ]
        remote_queue: 'mock'
        pbs_queue: 'test'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
workflows:
    test_workflow:
        ingest: "blue_sky.strategies.mock_ingest.MockIngest"
        states:
            - key: "ingest_mock"
              label: "Ingest Mock"
              class: "blue_sky.strategies.mock_ingest.MockIngest"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 100
            - key: "mock_preprocess"
              label: "Mock Preprocess"
              class: "blue_sky.strategies.mock_preprocess.MockPreprocess"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 100
        graph:
            - [ "ingest_mock", [ "mock_preprocess" ] ]
"""
