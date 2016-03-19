import logging
logger = logging.getLogger(__name__)

from gocd_parser.handler import history, status
from gocd_parser.pipeline import stage

class Pipeline(object):
    def __init__(self, name, go_server):
        self.name = name
        self.go_server = go_server

        self.set_history()

        self.status = status.Status(self.go_server, self.name)
        self.set_status()

        # We will not retrieve the group unless asked
        # since this may be set separately
        self.group = None

        self.parent_names = self.history.get_parent_names(
                self.history.first)
        logger.debug('parents: %s'%self.parent_names)

    def set_history(self):
        all_history = history.HistoryPager(self.go_server, self.name)
        self.history = all_history.merged

    def set_status(self):
        self.human_status = 'passing'
        self.stopped_duration = None
        self.failing_duration = None
        self.problem_duration = None
        self.passing_duration = None

        if self.status.paused:
            self.human_status = 'stopped'
            self.stopped_duration = self.history.get_duration_since(
                    self.history.last_completed)
            self.problem_duration = self.stopped_duration
            logger.debug('pipeline status: paused')

        if not self.history.passing:
            self.human_status = 'failing'
            self.failing_duration = self.history.failure_duration
            self.problem_duration = self.failing_duration
            logger.debug('pipeline status: failing')

        if self.is_stopped() and self.is_failing():
            if self.failing_duration > self.stopped_duration:
                self.problem_duration = self.failing_duration
            else:
                self.problem_duration = self.stopped_duration
            logger.debug('pipeline status: paused and failing')

        if self.human_status == 'passing':
            self.passing_duration = self.history.get_duration_since(
                    self.history.last_completed)
            logger.debug('pipeline status: passing')

    def set_from_groups_handler(self, groups_handler):
        '''Given groups as returned by the pipeline_groups handler, set
        the group I am in.'''
        self.group = groups_handler.get_pipeline(self.name)

    def get_duration(self, in_seconds=False):
        '''Return the amount of time since we have been having a
        problem. If we are passing, return the amount of time since the
        last pipeline start. If seconds are requested, return an int,
        otherwise return a human-readable duration string'''

        duration = self.problem_duration
        if self.problem_duration is None:
            duration = self.passing_duration

        if in_seconds is True:
            return(int(duration.total_seconds()))

        weeks = int(duration.days / 7)
        if weeks > 0:
            if weeks == 1:
                return '1 week'
            return '%d weeks'%weeks

        days = int(duration.days)
        if days > 0:
            if days == 1:
                return '1 day'
            return '%d days'%days

        hours = int(duration.seconds / 3600)
        if hours > 0:
            if hours == 1:
                return '1 hour'
            return '%d hours'%hours

        minutes = int(duration.seconds / 60)
        if minutes > 0:
            if minutes == 1:
                return '1 minute'
            return '%d minutes'%minutes

        return '<1 minute'

    def get_url_paths(self):
        '''Return the URL paths of the pipeline.

        If it passed or is paused, link to the overview page.
        For example: /pipelines/pipeline_name/...

        If it failed, link to the pages of the failing jobs.
        For example: /tab/build/detail/pipeline_name/...

        Since we may return multiple URLs, always return a list.'''

        paths = { 'failing': [] }

        path = 'pipelines/%s/'%self.name
        path += self.get_last_passing()['label'] + '/'

        stages = stage.Stages(self.get_last_passing()['stages'])
        first = stages.get_first()
        path += first.name + '/' + first.counter
        paths['passing'] = path

        if self.is_passing() or self.is_stopped():
            return paths

        logger.debug('setting failing stage paths')

        failing_paths = []
        path = 'tab/build/detail/%s/'%self.name
        path += self.get_last_completed()['label'] + '/'

        stages = stage.Stages(self.get_last_completed()['stages'])
        failed = stages.get_first_failed()
        path += failed.name + '/' + failed.counter + '/'

        for job in failed.jobs.get_failed():
            failing_paths.append(path + job.name)
        paths['failing'] = failing_paths

        return paths

    def get_status(self):
        '''Return a data structure containing this pipeline's status.'''
        return({
                'seconds':
                    self.get_duration(in_seconds=True),
                'human_time': self.get_duration(),
                'my_group': self.group,
                'status': self.human_status,
                'passing_label': self.get_last_passing()['label'],
                'paths': self.get_url_paths(),
                })

    def get_last_completed(self):
        return(self.history.last_completed)

    def get_last_passing(self):
        return(self.history.last_passing)

    def is_stopped(self):
        return(self.human_status == 'stopped')

    def is_failing(self):
        return(self.human_status == 'failing')

    def is_passing(self):
        return(self.human_status == 'passing')

