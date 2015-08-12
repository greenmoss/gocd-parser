import logging
import pprint

from six import iteritems

class Tree(object):
    '''This object contains a tree of pipelines, expanding out from a
    base pipeline.'''

    def __init__(self, base_pipeline):
        self.base_pipeline = base_pipeline
        self.logger = logging.getLogger(__name__+'.Tree')

        self.failing = []
        self.stopped = []

        self.centrality = {}
        self.ancestors = {}
        self.ancestor_groups = {}
        self.pipelines = {}

    def add_pipeline(self, pipeline):
        assert pipeline.name not in self.pipelines

        self.pipelines[pipeline.name] = pipeline

        if pipeline.is_stopped():
            self.stopped.append(pipeline.name)

        if pipeline.is_failing():
            self.failing.append(pipeline.name)

    def get_pipeline_blockers(self, pipeline_name):
        '''Find out which pipelines are blocking a given pipeline.'''
        assert pipeline_name in self.pipelines.keys()

        blockers = []
        for ancestor_name in self.ancestors[pipeline_name]:

            # ignore leaves; they only block themselves
            # TODO: look at code repo ancestors too! If a code repo
            # ancestor is shared across leaf pipelines, a leaf failure
            # *could* block!
            if self.centrality[ancestor_name] is 0: continue

            ancestor = self.pipelines[ancestor_name]

            if ancestor.is_stopped() or ancestor.is_failing():
                blockers.append(ancestor)

        return(blockers)

    def get_status_from_base(self, pipeline_name=None):
        '''Return a data structure containing this tree's status. If no
        base pipeline name is given, get the status from the base
        pipeline.'''
        if pipeline_name is None:
            pipeline_name = self.base_pipeline

        pipeline = self.pipelines[pipeline_name]
        base_status = pipeline.get_status()
        base_status['ancestor_groups'] = self.ancestor_groups[pipeline.name]
        info = {
                'base_name': pipeline_name,
                'base_status': base_status,
                'blocking': {},
                'schema_version': '1.1.0',
                }

        blockers = self.get_pipeline_blockers(pipeline_name)
        for ancestor in blockers:
            status = ancestor.get_status()
            status['ancestor_groups'] = self.ancestor_groups[ancestor.name]
            info['blocking'][ancestor.name] = status

        human_status = 'passing'
        if len(info['blocking']) > 0:
            human_status = 'blocked'
        if pipeline.is_failing():
            human_status = 'failing'
        info['status'] = human_status

        return info

    def __repr__(self):
        string = ''
        string += 'ancestors: %s\n'% pprint.pformat(
                self.ancestors)
        string += 'centrality: %s\n'% pprint.pformat(
                self.centrality)
        string += 'failing: %s\n'% pprint.pformat(
                self.failing)
        string += 'stopped: %s\n'% pprint.pformat(
                self.stopped)
        string += 'ancestor_groups: %s\n'% pprint.pformat(
                self.ancestor_groups)
        return(string)
