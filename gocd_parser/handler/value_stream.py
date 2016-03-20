import json
import logging
logger = logging.getLogger(__name__)

import networkx as nx

from gocd_parser.retriever import url

class ValueStream(object):
    '''Retrieve json from the hidden GoCD Value Stream! Return a networkx graph
    object containing all the pipelin and repo information.'''

    def __init__(self, go_server, pipeline_name, label):
        self.go_server = go_server
        self.pipeline_name = pipeline_name
        self.label = label

        logger.debug("handling value stream")

        self.graph = nx.DiGraph()

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

        logger.debug('graph is %s',self.graph.nodes())
