import logging
import json
from datetime import datetime

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
        self.go_server = go_server

        self.logger = logging.getLogger(__name__+'.Cctray')
        self.logger.debug("handling cctray.xml")

        retrieved = url.URL( self.go_server, '/cctray.xml')

        self.metrics = {}

        doc = xmltodict.parse("\n".join(retrieved.contents))
        projects = doc['Projects']['Project']

        self.logger.debug(json.dumps(projects, sort_keys=True,
            indent=2))

        pipelines = {}
        stages = 0
        jobs = 0
        status_totals = {}
        total_age = 0

        for project in projects:
            name_parts = project['@name'].split(' :: ')
            self.logger.debug(name_parts)
            pipeline_name = name_parts[0]

            # record pipeline total
            pipelines[pipeline_name] = int(
                    project['@lastBuildLabel'].split(' :: ')[0])

            # it's a stage
            if len(name_parts) == 2:
                # add to stage total
                stages += 1

                # add to status totals
                if project['@lastBuildStatus'] in status_totals:
                    status_totals[project['@lastBuildStatus']] += 1
                else:
                    status_totals[project['@lastBuildStatus']] = 1

                # add to age totals
                build_date = datetime.strptime(
                        project['@lastBuildTime']+'UTC',
                        '%Y-%m-%dT%X%Z')
                age = datetime.now() - build_date
                total_age += age.days * 3600 + age.seconds

        builds = 0
        for pipeline, count in iteritems(pipelines):
            builds += count

        self.metrics['stages'] = stages
        self.metrics['pipelines'] = len(pipelines)
        self.metrics['builds'] = builds
        self.metrics['status_totals'] = status_totals
        self.metrics['total_age'] = total_age
