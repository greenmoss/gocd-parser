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

        logger.info('cctray metrics are inaccurate and will be deprecated soon!')
        self.metrics = {}
        self.metrics['stages'] = 0
        self.metrics['status_totals'] = {}
        self.metrics['total_age'] = 0
        self.metrics['builds'] = 0

        self.parse()
        self.metrics['pipelines'] = len(self.pipelines)

    def parse(self):
        for project in self.projects:
            self.parse_project(project)

    def parse_project(self, project):
        name_parts = project['@name'].split(' :: ')
        logger.debug('name_parts: %s', name_parts)
        pipeline_name = name_parts[0]

        if not self.pipelines.has_key(pipeline_name):
            # assume *first* stage's info is canonical for the pipeline
            self.parse_pipeline(project, pipeline_name)

        pipeline = self.pipelines[pipeline_name]

        if len(name_parts) == 2:
            stage = self.parse_stage(project)
            pipeline['stages'][name_parts[1]] = stage

            # set pipeline info from this stage
            if pipeline['lastBuildEpoch'] is None:
                self.copy_stage_to_pipeline(stage, pipeline)
            else:
                if stage['lastBuildEpoch'] > pipeline['lastBuildEpoch']:
                    self.copy_stage_to_pipeline(stage, pipeline)

        # TODO: also parse jobs

    def copy_stage_to_pipeline(self, stage, pipeline):
        for key in ['Status', 'Label', 'Epoch']:
            pipeline['lastBuild'+key] = stage['lastBuild'+key]

    def parse_pipeline(self, project, pipeline_name):
        # TODO: test labels that are not convertible to an int!
        # TODO: deprecate 'build_count', since it's actually a label
        build_count = int( project['@lastBuildLabel'] )
        logger.debug('pipeline %s has build count %d', pipeline_name,
                build_count)

        self.pipelines[pipeline_name] = {
                'stages': {},
                'build_count': build_count,
                'lastBuildLabel': None,
                'lastBuildStatus': None,
                'lastBuildEpoch': None,
                }
        self.metrics['builds'] += build_count

    def parse_stage(self, project):
        # metrics will be deprecated!
        self.metrics['stages'] += 1
        if project['@lastBuildStatus'] in self.metrics['status_totals']:
            self.metrics['status_totals'][project['@lastBuildStatus']] += 1
        else:
            self.metrics['status_totals'][project['@lastBuildStatus']] = 1
        build_date = parse_time(project['@lastBuildTime'])
        age = datetime.now() - build_date
        self.metrics['total_age'] += age.days * 3600 + age.seconds

        attrs = {}
        for key, value in project.items():
            # TODO: parse "breakers" too!
            if type(value) != type(u''): continue

            # the @ symbol denotes an attribute
            # since cctray only uses attributes, we'll strip this symbol
            # to make the attributes easier to access
            attrs[key[1:]] = value
        attrs['lastBuildEpoch'] = parse_epoch(attrs['lastBuildTime'])
        return attrs

def parse_time(datetime_string):
    '''Generic time conversion, from the time formats seen in cctray'''
    return datetime.strptime( datetime_string+'UTC', '%Y-%m-%dT%X%Z')

def parse_epoch(datetime_string):
    '''Convert parsed time to epoch.'''
    dt = parse_time(datetime_string)
    return int((dt - datetime(1970,1,1)).total_seconds())
