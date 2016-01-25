import logging
import json
from datetime import datetime
import pprint

from gocd_parser.retriever import url

class HistoryPageException(Exception):
    pass

class HistoryPage(object):
    '''A handler for history api calls.'''

    def __init__(self, go_server, pipeline_name, offset):
        '''Convert a string of history json into python. From this, gather
        various metrics.
        An example history API url:
            http://gocd.your.org:8080/go/api/pipelines/your-pipeline/history'''
        self.go_server = go_server
        self.pipeline_name = pipeline_name
        self.offset = offset

        my_url = '/api/pipelines/' + self.pipeline_name + \
                '/history/' + offset

        retrieved = url.URL( self.go_server, my_url)

        self.logger = logging.getLogger(__name__+'.HistoryPage')
        self.logger.debug("handling history")

        data = json.loads(retrieved.contents[0])
        self.pagination = data['pagination']

        self.pipelines = data['pipelines']
        self.first = self.pipelines[0]
        self.logger.debug('%s first pipeline: %s'%
                (self.first['name'], pprint.pformat(self.first)))

    def add(self, new, accept_failure = True):
        self.pipelines.extend(new.pipelines)
        self.first = self.pipelines[0]
        try:
            self.set_info()
        except:
            self.logger.debug(
                    'failed to get full info on added page %s',
                    new.pagination)
            if accept_failure is False:
                raise HistoryPageException("unable to add page!")

    def set_info(self):
        self.last_completed = self.get_last_completed()
        self.last_passing = self.get_last_passing()

        if self.last_passing['label'] == self.last_completed['label']:
            self.passing = True
        else:
            self.passing = False

        self.first_of_current_failures = self.get_first_failing()
        self.failure_duration = None
        if not self.passing:
            self.failure_duration = self.get_duration_since(
                    self.first_of_current_failures)

    def get_first_failing(self):
        if self.passing: return None
        current_failing = self.first
        for pipeline in self.pipelines:
            if self.pipeline_passed(pipeline):
                return current_failing
            current_failing = pipeline
        raise HistoryPageException("unable to find any passing pipelines!")

    def get_last_completed(self):
        for pipeline in self.pipelines:
            if self.pipeline_completed(pipeline):
                return pipeline
        raise HistoryPageException(
                "unable to find any completed pipelines!")

    def get_last_passing(self):
        for pipeline in self.pipelines:
            if self.pipeline_passed(pipeline):
                return pipeline
        raise HistoryPageException("unable to find any passing pipelines!")

    def get_duration_since(self, pipeline):
        epoch = pipeline['stages'][0]['jobs'][0]['scheduled_date'] / 1000
        duration = datetime.now() - datetime.fromtimestamp(epoch)
        assert duration.total_seconds() >= 0
        return duration

    def pipeline_completed(self, pipeline, status=['Unknown']):
        for stage in pipeline['stages']:
            if stage['scheduled'] and stage['result'] in status:
                return False
        return True

    def pipeline_passed(self, pipeline, status=['Passed']):
        for stage in pipeline['stages']:
            if not stage.has_key('result'):
                return False
            if stage['result'] not in status:
                return False
        return True

    def get_parent_names(self, pipeline):
        names = []
        revs = pipeline['build_cause']['material_revisions']
        for revision in revs:
            if revision['material']['type'] != 'Pipeline': continue
            names.append(revision['material']['description'])
        return(names)
