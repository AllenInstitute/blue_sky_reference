from workflow_engine.views.enqueueable_job_grid import EnqueueableJobGrid
from blue_sky.models import (
    Observation,
    Calibration,
    ObservationGroup
)
import pandas as pd
from django_pandas.io import read_frame


class DemoJobGrid(EnqueueableJobGrid):
    SERIALIZE_COLUMNS = [
        'z_index',
        'object_state_id',
        'workflow_node',
        'letter_code',
        'job_id',
        'enqueued_object_type',
        'enqueued_object_id',
        'start',
        'end'
    ]
    '''ordered list of columns from the annotated job dataframe to send.
    '''

    def xget_node_order(self):
        '''Override with a specific list of job queue names.
        These will be used in order as the columns of the job grid.

        Returns
        -------
        list of string
        '''
        return [
            # TBD: currently renamed to use default
        ]

    def get_model_classes(self):
        '''Models to be queried for display in the grid.
        Override to provide a specific list of model classes.
        They must implement :class:`workflow_engine.mixins.enqueueable.Enqueueable`
 
        Returns
        -------
        list of Model
            model classes that implement Enqueueable

        Notes
        -----
        By default, immediate subclasses of Enqueueable 
        will be included, but not leaf descendant classes.
        '''
        return [
            Observation,
            Calibration,
            ObservationGroup
        ]

    def xquery_enqueued_object_row_df(self):
        '''Combine row dataframes across
        EMMontageSet, ReferenceSet, Chunk and Load.
        The sub dataframes all share the montage set z index
        as the row coordinate
        '''
        self.enqueued_object_row_df = pd.concat(
            [
                self.query_calibration_row_df(),
                self.query_observation_row_df(),
                self.query_observation_group_df(),
            ]
        ).sort_values('z_index')

        return self.enqueued_object_row_df

    def query_calibration_row_df(self):
        calibration_row_df = read_frame(
            Calibration.objects.values(
                'id',
                'object_state'
            ).filter(
                id__gte=self.row_range[0],
                id__lte=self.row_range[1] 
            )
        )
        calibration_row_df.assign(z_index=calibration_row_df['id'])
        calibration_row_df.columns = [
            'enqueued_object_id',
            'z_index',
            "object_state"
        ]
        calibration_row_df['enqueued_object_type'] = 'calibration'

        return calibration_row_df
