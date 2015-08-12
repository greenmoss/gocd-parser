import logging

from gocd_parser.value_stream import tree
from gocd_parser import pipeline

from . import node

class ParentRecursor(object):
    '''Recurse through the tree structure created by pipelines in a
    value stream. We are looking "leftwards" only: ancestors, not
    children.'''

    def __init__(self, go_server, pipeline_name, pipeline_groups):
        self.go_server = go_server
        self.pipeline_groups = pipeline_groups

        self.logger = logging.getLogger(__name__+'.ParentRecursor')

        self.tree = tree.Tree(pipeline_name)
        self.traverse_pipeline(pipeline_name)

    def traverse_pipeline(self, pipeline_name):
        '''Recursively get the status of a pipeline and all its
        ancestors. Before you invoke it, set self.tree to a tree.Tree()
        object.'''

        this_pipeline = pipeline.Pipeline(pipeline_name, self.go_server)
        this_pipeline.set_from_groups_handler(self.pipeline_groups)

        self.tree.add_pipeline(this_pipeline)

        this_node = node.Node(self.pipeline_groups, self.tree)

        for parent_name in this_pipeline.parent_names:
            if parent_name in self.tree.pipelines:
                self.logger.debug('skipping already-traversed parent: %s'%parent_name)

            else:
                self.logger.info('traversing parent: %s'%parent_name)
                self.traverse_pipeline(parent_name)

            this_node.from_parent(parent_name)

        this_node.add_to_tree(self.tree, pipeline_name)
