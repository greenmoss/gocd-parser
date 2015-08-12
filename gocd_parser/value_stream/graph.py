import logging

from gocd_parser.handler import pipeline_groups
from gocd_parser.value_stream import tree, recurse

class GraphException(Exception):
    pass

class Graph(object):
    '''This is a graph of pipelines that are connected to a given
    pipeline. For now, we are only looking at ancestors.'''

    def __init__(self, go_server, pipeline_name):
        self.go_server = go_server
        self.pipeline_name = pipeline_name

        self.logger = logging.getLogger(__name__+'.Graph')

        self.pipeline_groups = pipeline_groups.PipelineGroups(
                self.go_server)

        self.set_parent_tree()

    def set_parent_tree(self):
        self.logger.info('recursing from root pipeline: %s' %
                self.pipeline_name)
        recursor = recurse.ParentRecursor(self.go_server,
                self.pipeline_name, self.pipeline_groups)
        self.tree = recursor.tree

        self.logger.debug(self.tree)
