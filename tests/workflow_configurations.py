TEST_CONFIG_YAML_ONE_NODE = """
executables:
    mock:
        name: 'Mock Executable'
        path: '/data/aibstemp/timf/example_data/bin/mock_executable'
        pbs_queue: 'lims2'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
run_states:
    - "PENDING"
    - "QUEUED"
    - "RUNNING"
    - "FINISHED_EXECUTION"
    - "FAILED_EXECUTION"
    - "FAILED"
    - "SUCCESS"
    - "PROCESS_KILLED"
workflows:
    test_workflow:
        ingest: "blue_sky.strategies.mock_ingest.MockIngest"

        states:
            - key: "start"
              label: "Start"
              class: "blue_sky.strategies.mock_analyze.MockAnalyze"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
        graph:
            - [ "start", [ ] ]
"""

TEST_CONFIG_YAML_TWO_NODES = """
executables:
    mock:
        name: 'Mock Executable'
        path: '/data/aibstemp/timf/example_data/bin/mock_executable'
        pbs_queue: 'lims2'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
run_states:
    - "PENDING"
    - "QUEUED"
    - "RUNNING"
    - "FINISHED_EXECUTION"
    - "FAILED_EXECUTION"
    - "FAILED"
    - "SUCCESS"
    - "PROCESS_KILLED"
workflows:
    test_workflow:
        ingest: "development.strategies.lens_correction_ingest.LensCorrectionIngest"

        states:
            - key: "start"
              label: "Start"
              class: "development.strategies.start.Start"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
            - key: "continue"
              label: "Continue"
              class: "development.strategies.continue.Continue"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
        graph:
            - [ "start", [ "continue" ] ]
"""
