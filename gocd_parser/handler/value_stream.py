import json
import logging
logger = logging.getLogger(__name__)

import networkx as nx

from gocd_parser.retriever import url

class ValueStream(object):
    '''Retrieve json from the hidden GoCD Value Stream! Return a networkx
    DiGraph object containing all the pipeline and repo information. Pipelines
    and repos are connected to each other by "depends_on" and "parent_of"
    edges.'''

    def __init__(self, go_server, pipeline_name, label):
        self.go_server = go_server
        self.pipeline_name = pipeline_name
        self.label = label

        logger.debug("handling value stream")

        self.graph = nx.DiGraph(pipeline=self.pipeline_name, label=self.label)

        path = '/pipelines/value_stream_map/'+pipeline_name+'/'+label+'.json'
        retrieved = url.URL( self.go_server, path)
        data = json.loads(retrieved.contents[0])

        # populate nodes
        for level_index, level_info in enumerate(data['levels']):
            for node in level_info['nodes']:
                id = node['id']
                self.graph.add_node(node['id'])
                self.graph.node[node['id']] = node
                self.graph.node[node['id']]['level'] = level_index

        # populate edges
        for level in data['levels']:
            for node in level['nodes']:
                my_id = node['id']
                for parent_id in node['parents']:
                    self.graph.add_edge(parent_id, my_id, relationship='parent_of', parent_of=True)
                # node['dependents'] contains same connection in reverse
                # to keep things simple, we will only set a parent relationship

        # create a sub-graph with only the pipelines
        self.pipeline_graph = self.filter_by_type('PIPELINE')

        logger.debug('graph nodes are %s',self.graph.nodes())
        logger.debug('graph edges %s',self.graph.edges(data='relationship'))

    def filter_by_type(self, node_types):
        '''Return a subgraph containing only the desired node types.'''

        # allow a single type, or multiple
        if type(node_types) is str:
            node_types = (node_types)

        ids = []
        for node_id in self.graph.nodes():
            node = self.graph.node[node_id]
            if node['node_type'] in node_types:
                ids.append(node_id)

        return self.graph.subgraph(ids)

    def leaf_nodes(self, subgraph = None):
        '''Find all leaf nodes: any node that is a parent of one child, and has
        no dependents. Optionally restrict search to a subgraph.'''
        nodes = []
        for node in self.graph.nodes_iter():
            if subgraph is None:
                thegraph = self.graph
            else:
                thegraph = subgraph

            # must have children
            outd = thegraph.out_degree(node) 
            if outd == 0:
                continue

            # must not have parents
            ind = thegraph.in_degree(node) 
            if ind > 0:
                continue

            nodes.append(node)

        return nodes

