import logging
logger = logging.getLogger(__name__)

import networkx as nx

import gocd_parser.pipeline
import gocd_parser.handler.cctray
from gocd_parser.handler import pipeline_groups
from gocd_parser.handler import value_stream

class StreamStatus(object):
    '''Get the status of a pipeline's value stream: passing, blocked, or
    failing. If blocking, get the information about the blockers.'''

    def __init__(self, go_server, pipeline_name, label = None):
        self.go_server = go_server
        self.pipeline = gocd_parser.pipeline.Pipeline(pipeline_name, go_server)

        if label is None:
            # get the last passing pipeline
            label = self.pipeline.get_last_passing()['label']
        self.label = label

        self.value_stream = value_stream.ValueStream(
                self.go_server, self.pipeline.name, self.label)
        self.ancestors = nx.ancestors(self.value_stream.pipeline_graph,
                self.pipeline.name)

        self.cctray = gocd_parser.handler.cctray.Cctray(go_server)
        self.pipeline_groups = pipeline_groups.PipelineGroups(go_server)
        self.pipeline.set_from_groups_handler(self.pipeline_groups)
        self.pipeline.set_failing_comparison()

        self.blockers = {}
        for blocker_name in self.get_blocker_names():
            logger.debug('getting blocker info for %s', blocker_name)
            pipeline = gocd_parser.pipeline.Pipeline(blocker_name, self.go_server)
            pipeline.set_from_groups_handler(self.pipeline_groups)
            pipeline.set_failing_comparison()
            self.blockers[blocker_name] = pipeline

        self.status = 'passing'
        if len(self.blockers) > 0:
            self.status = 'blocked'
        if self.pipeline.is_failing():
            self.status = 'failing'

    def get_pipeline_dump_info(self, pipeline):
        '''Set information that will be needed in dump() for this pipeline.'''
        info = {
                'status': pipeline.human_status,
                'paths': pipeline.get_url_paths(),
                'seconds': pipeline.get_duration(in_seconds=True),
                'my_group': pipeline.group,
                'passing_label': pipeline.get_last_passing()['label'],
                'ancestor_groups': self.get_ancestor_groups(pipeline.name),
                'human_time': pipeline.get_duration(),
                }

        if not pipeline.is_failing(): return info

        info['changes'] = {'committers': [], 'pipelines': []}
        logger.debug('pipeline %s with changes: %s', pipeline.name, info)

        committers = {}
        pipelines = {}

        for material in pipeline.failing_comparison.materials:
            if material.type == 'git':
                for change in material.changes:
                    name = change.modifier_name
                    email = change.modifier_email
                    id = name+'|'+email
                    time = change.modifier_time
                    if not committers.has_key(id):
                        committers[id] = {
                                'name': name,
                                'email': email,
                                'commit_count': 0,
                                }
                    committers[id]['commit_count'] += 1

            else:
                for change in material.changes:
                    name = material.name
                    label = change.label
                    time = change.completed
                    if not pipelines.has_key(name):
                        pipelines[name] = {
                                'name': name,
                                'run_count': 0,
                                }
                    pipelines[name]['run_count'] += 1

        for committer_id, committer_info in committers.items():
            info['changes']['committers'].append(committer_info)
        for pipeline_name, pipeline_info in pipelines.items():
            info['changes']['pipelines'].append(pipeline_info)

        return info

    def get_blocker_names(self):
        '''Look through cctray for any failing pipelines that are my ancestors.'''
        blockers = []
        for pipeline_name, pipeline_info in self.cctray.pipelines.items():
            if pipeline_info['lastBuildStatus'] == 'Success': continue
            if pipeline_name not in self.ancestors: continue
            blockers.append(pipeline_name)
        return blockers

    def get_ancestor_groups(self, pipeline_name):
        groups = []
        for ancestor in self.ancestors:
            logger.debug('ancestor of %s: %s', pipeline_name, ancestor)
            groups.append(self.pipeline_groups.pipelines[ancestor][0])
        return list(set(groups))

    def dump(self):
        '''Output stream status so it can be serialized.'''
        out = {
                'base_name': self.pipeline.name,
                'schema_version': '1.1.0',
                'base_status': self.get_pipeline_dump_info(self.pipeline),
                'status': self.status,
                'blocking': {},
                }

        for blocker_name, pipeline in self.blockers.items():
            out['blocking'][blocker_name] = self.get_pipeline_dump_info(pipeline)

        return out
