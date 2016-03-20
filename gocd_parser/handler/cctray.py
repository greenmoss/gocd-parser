import json
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

import xmltodict

from six import iteritems

from gocd_parser.retriever import url

class Cctray(object):
    '''A handler for cctray xml files.'''

    def __init__(self, go_server):
        '''Convert a string of cctray xml into python. From this, gather
        various metrics.
        An example cctray url:
            http://gocd.your.org:8080/go/cctray.xml'''

        logger.debug("handling cctray.xml")

        retrieved = url.URL( go_server, '/cctray.xml')
        doc = xmltodict.parse("\n".join(retrieved.contents))

        self.projects = doc['Projects']['Project']
        self.pipelines = {}
        self.metrics = {}

        self.parse()

    def parse(self):
        self.metrics['stages'] = 0
        self.metrics['status_totals'] = {}
        self.metrics['total_age'] = 0
        self.metrics['builds'] = 0

        for project in self.projects:
            self.parse_project(project)

        self.metrics['pipelines'] = len(self.pipelines)

    def parse_project(self, project):
        name_parts = project['@name'].split(' :: ')
        logger.debug('name_parts: %s', name_parts)
        pipeline_name = name_parts[0]

        if not self.pipelines.has_key(pipeline_name):
            # assume *first* stage's info is canonical for the pipeline
            self.parse_pipeline(project, pipeline_name)

        pipeline = self.pipelines[pipeline_name]

        if len(name_parts) == 2:
            self.parse_stage(project)

    def parse_pipeline(self, project, pipeline_name):
        # TODO: test labels that are not convertible to an int!
        # TODO: deprecate 'build_count', since it's actually a label
        build_count = int( project['@lastBuildLabel'] )
        logger.debug('pipeline %s has build count %d', pipeline_name,
                build_count)

        self.pipelines[pipeline_name] = {
                'stages': {},
                'build_count': build_count,
                'lastBuildLabel': project['@lastBuildLabel']
                }
        self.metrics['builds'] += build_count

    def parse_stage(self, project):
        # add to stage total
        self.metrics['stages'] += 1

        # add to status totals
        if project['@lastBuildStatus'] in self.metrics['status_totals']:
            self.metrics['status_totals'][project['@lastBuildStatus']] += 1
        else:
            self.metrics['status_totals'][project['@lastBuildStatus']] = 1

        # add to age totals
        build_date = datetime.strptime( project['@lastBuildTime']+'UTC',
                '%Y-%m-%dT%X%Z')
        age = datetime.now() - build_date
        self.metrics['total_age'] += age.days * 3600 + age.seconds
