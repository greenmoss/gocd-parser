import json
import logging
import pprint

from gocd_parser.retriever import url

class PipelineGroups(object):
    '''A handler for pipeline groups api calls.'''

    def __init__(self, go_server):
        '''Convert a string of pipeline groups json into python.
        An example pipelines url:
            http://gocd.your.org:8080/go/api/config/pipeline_groups'''
        self.go_server = go_server
        self.logger = logging.getLogger(__name__+'.PipelineGroups')

        retrieved = url.URL( self.go_server, '/api/config/pipeline_groups/')

        self.groups = json.loads(retrieved.contents[0])
        self.logger.debug('pipeline_groups: %s'%
                pprint.pformat(self.groups))

        self.set_pipelines()

    def set_pipelines(self):
        self.pipelines = {}
        for group in self.groups:
            for idx, pipeline in enumerate(group['pipelines']):
                self.pipelines[pipeline['name']] = (group['name'], idx)
        self.logger.debug('pipelines: %s'%
                pprint.pformat(self.pipelines))

    def get_pipeline(self, pipeline_name):
        '''Get the group a pipeline is in.'''

        assert pipeline_name in self.pipelines
        return self.pipelines[pipeline_name][0]
