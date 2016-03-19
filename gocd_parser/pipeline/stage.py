import logging
logger = logging.getLogger(__name__)

from gocd_parser.pipeline import job, common

class StagesException(Exception):
    pass

class Stages(common.History):
    '''Read in data for stages of history as returned by history_page
    parser.'''

    def __init__(self, data):

        # don't set_scalars; we are a list
        self.stages = []
        for stage in data:
            self.stages.append(Stage(stage))

    def get_first(self):
        return self.stages[0]

    def get_first_failed(self):
        for stage in self.stages:
            if stage.is_passing():
                continue
            return stage
        raise StagesException('no stages failed')

class Stage(common.History):
    '''Read in data for one stage of history as returned by history_page
    parser.'''

    def __init__(self, data):
        self.data = data

        self.set_scalars()
        self.jobs = job.Jobs(data['jobs'])

    def is_passing(self):
        if self.result == 'Passed':
            return True
        return False
