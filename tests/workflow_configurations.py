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
        environment: ['SLEEPTIME=60', 'PYTHONPATH=/blue_sky/bin' ]
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

TEST_CONFIG_YAML_FULL_WORKFLOW = u"""
executables:

    mock:
        name: 'Mock Executable'
        path: '/opt/conda/bin/python'
        args: [ '-m', 'mock_executable' ]
        environment: ['SLEEPTIME=60', 'PYTHONPATH=/blue_sky/bin' ]
        remote_queue: 'mock'
        pbs_queue: 'test'
        pbs_processor: 'nodes=1:ppn=1'
        pbs_walltime: 'walltime=0:10:00'

workflows:
    mock_workflow:
        ingest: "blue_sky.strategies.mock_ingest.MockIngest"

        states:
            - key: "ingest_mock"
              label: "Ingest Mock"
              class: "blue_sky.strategies.mock_ingest.MockIngest"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "mock_preprocess"
              label: "Mock Preprocess"
              class: "blue_sky.strategies.mock_preprocess.MockPreprocess"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "mock_analyze"
              label: "Mock Analyze"
              class: "blue_sky.strategies.mock_analyze.MockAnalyze"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "mock_qc"
              label: "Mock QC"
              class: "blue_sky.strategies.mock_q_c.MockQC"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "mock_calibrate"
              label: "Mock Calibrate"
              class: "blue_sky.strategies.mock_calibrate.MockCalibrate"
              enqueued_class: "blue_sky.models.calibration.Calibration"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "group_assign"
              label: "Group Assignment"
              class: "blue_sky.strategies.mock_group_assignment.MockGroupAssignment"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "process_grouped"
              label: "Process Grouped Observations"
              class: "blue_sky.strategies.mock_process_grouped_observations.MockProcessGroupedObservations"
              enqueued_class: "blue_sky.models.observation.Observation"
              executable: "mock"
              batch_size: 5
              max_retries: 3

            - key: "complete_group"
              label: "Complete Group"
              class: "blue_sky.strategies.mock_complete_group.MockCompleteGroup"
              enqueued_class: "blue_sky.models.observation_group.ObservationGroup"
              executable: "mock"
              batch_size: 5
              max_retries: 3

        graph:
            - [ "ingest_mock", [ "mock_preprocess", "mock_calibrate" ] ]
            - [ "mock_preprocess", [ "mock_analyze" ] ]
            - [ "mock_calibrate", [ "mock_analyze" ] ]
            - [ "mock_analyze", [ "mock_qc" ] ]
            - [ "mock_qc", [ "group_assign" ] ]
            - [ "group_assign", [ "process_grouped" ] ]
            - [ "process_grouped", [ "complete_group" ] ]
"""
