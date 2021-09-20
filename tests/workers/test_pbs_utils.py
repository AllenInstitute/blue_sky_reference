import pytest
from mock import Mock, patch
from workflow_engine.pbs_utils import PbsUtils

def test_slurm_script():
    script_generator = PbsUtils()

    mock_executable = Mock()
   
    mock_executable.remote_queue = 'slurm'
    mock_executable.pbs_queue = 'MoCkQuEuENaMe'
    mock_executable.pbs_processor = '--mem=256:--ntasks=20'
    mock_executable.pbs_walltime = 'walltime=1:23:45'
    mock_task = Mock() 
    mock_task.id = 12345
    mock_task.get_task_name = Mock(return_value='task_12345')
    mock_task.log_file = '/path/to/mock.log'
    mock_task.full_executable = '/path/to/full/executable --arg1 value1'
    mock_task.environment_vars = Mock(return_value=['A=B', 'C=D'])
    mock_settings = Mock()
    mock_settings.PBS_CONDA_ENV = 'MoCk_EnViRoNmEnT'
    mock_settings.PBS_RESPONSE_CONDA_ENV = 'MoCk_ReSpOnSe_EnViRoNmEnT'
    mock_settings.HPC_RESPONSE_PYTHONPATH = 'HpC_ReSpOnSe_PyThOnPaTh'
    mock_settings.BLUE_SKY_SETTINGS_HPC_RESPONSE = 'BlUe_sKy_SeTtInGs_HpC_rEsPoNsE'
    mock_settings.APP_PACKAGE = 'BlUe_SkY'

    slurm_template = script_generator.get_template(
        mock_executable,
        mock_task,
        mock_settings
    )

    assert script_generator is not None

    for line in [
        '#SBATCH -p MoCkQuEuENaMe',
        '#SBATCH --mem=256',
        '#SBATCH --ntasks=20',
        '#SBATCH --time 1:23:45',
        '#SBATCH --job-name task_12345',
        '#SBATCH -o /path/to/mock.log',
        'source activate MoCk_ReSpOnSe_EnViRoNmEnT',
        'python -m workflow_engine.mini_response --action finished 12345 --app-name BlUe_SkY',
        'export TMPDIR="/scratch/capacity/${SLURM_JOBID}/"',
        'export SPARK_LOCAL_DIRS="/scratch/capacity/${SLURM_JOBID}/"',
        'export BLUE_SKY_SETTINGS=BlUe_sKy_SeTtInGs_HpC_rEsPoNsE',
        'export A=B',
        'export C=D',
        'export PYTHONPATH=${PYTHONPATH}:HpC_ReSpOnSe_PyThOnPaTh', 
        'source activate MoCk_ReSpOnSe_EnViRoNmEnT',
        'python -m workflow_engine.mini_response --action running 12345 --app-name BlUe_SkY',
        'source activate MoCk_EnViRoNmEnT',
        '/path/to/full/executable --arg1 value1'
    ]:
        assert line in slurm_template
