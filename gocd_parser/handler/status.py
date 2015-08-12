import logging
import json

from gocd_parser.retriever import url

class Status(object):
    '''A handler for status api calls.'''

    def __init__(self, go_server, pipeline_name):
        '''Convert a string of status json into python. From this, gather
        various metrics.
        An example status API url:
            http://gocd.your.org:8080/go/api/pipelines/your-pipeline/status'''

        self.go_server = go_server

        self.logger = logging.getLogger(__name__+'.Status')
        self.logger.debug("handling status")

        my_url = '/api/pipelines/' + pipeline_name + \
                '/status/'
        retrieved = url.URL( self.go_server, my_url)

        data = json.loads(retrieved.contents[0])
        self.locked = bool(data['locked'])
        self.paused = bool(data['paused'])
        self.schedulable = bool(data['schedulable'])

        self.logger.debug('%s status: paused %s, schedulable %s' %
                (pipeline_name, self.paused, self.schedulable))
