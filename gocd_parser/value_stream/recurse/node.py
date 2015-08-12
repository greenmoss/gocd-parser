class Node(object):
    '''While recursing through the value stream map tree, keep the state
    of a pipeline within this object.'''

    def __init__(self, pipeline_groups, tree):
        self.pipeline_groups = pipeline_groups
        self.tree = tree

        self.ancestors = []
        self.centrality = 0
        self.ancestor_groups = []

    def from_parent(self, parent_name):
        parent_group = self.pipeline_groups.pipelines[parent_name][0]
        self.ancestor_groups = list(set(self.ancestor_groups +
            self.tree.ancestor_groups[parent_name] + [parent_group]
            ))

        self.ancestors = list(set(self.ancestors +
            self.tree.ancestors[parent_name] + [parent_name]))

        parent_centrality = self.tree.centrality[parent_name]
        if parent_centrality is 0:
            self.centrality += 1
        else:
            self.centrality += parent_centrality

    def add_to_tree(self, tree, pipeline_name):
        tree.ancestors[pipeline_name] = self.ancestors
        tree.ancestor_groups[pipeline_name] = self.ancestor_groups
        tree.centrality[pipeline_name] = self.centrality
