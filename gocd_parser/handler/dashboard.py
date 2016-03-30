import json
import logging
logger = logging.getLogger(__name__)

from gocd_parser.retriever import url

class Dashboard(object):
    def __init__(self, go_server):
        self.go_server = go_server

        path = '/api/dashboard/'
        retrieved = url.URL( self.go_server, path, headers={'Accept':
            'application/vnd.go.cd.v1+json'})

        data = json.loads(''.join(retrieved.contents))

        self.pipelines = {}
        
        for group in data['_embedded']['pipeline_groups']:
            for pipeline in group['_embedded']['pipelines']:
                name = pipeline['name']
                logger.debug('adding dashboard pipeline %s',name)
                assert name not in self.pipelines
                self.pipelines[name] = pipeline

    def paused(self, pipeline_name):
        assert pipeline_name in self.pipelines
        return self.pipelines[pipeline_name]['pause_info']['paused']

    def passing(self, pipeline_name):
        assert pipeline_name in self.pipelines
        for instance in self.pipelines[pipeline_name]['_embedded']['instances']:
            for stage in instance['_embedded']['stages']:
                if stage['status'] == 'Failed': return False
        return True

    def completed(self, pipeline_name):
        assert pipeline_name in self.pipelines
        for instance in self.pipelines[pipeline_name]['_embedded']['instances']:
            for stage in instance['_embedded']['stages']:
                if stage['status'] == 'Unknown': return False
        return True
