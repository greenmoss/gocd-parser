import logging

from gocd_parser.pipeline import common

class Jobs(common.History):
    '''Read in data for jobs of a stage as returned by history_page
    parser.'''

    def __init__(self, data):
        self.logger = logging.getLogger(__name__+'.Jobs')

        # no set_scalars; we are a list
        self.jobs = []
        for job in data:
            self.jobs.append(Job(job))

    def get_failed(self):
        failed = []
        for job in self.jobs:
            if job.passed():
                continue
            failed.append(job)
        return failed

class Job(common.History):
    '''Read in data for one job of a stage as returned by history_page
    parser.'''

    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(__name__+'.Job')

        self.set_scalars()

    def passed(self):
        if self.result == 'Passed':
            return True
        return False
