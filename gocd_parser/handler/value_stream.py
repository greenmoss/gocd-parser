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

        self.graph = nx.Graph()

        path = '/pipelines/value_stream_map/'+pipeline_name+'/'+label+'.json'
        retrieved = url.URL( self.go_server, path)
        data = json.loads(retrieved.contents[0])

        # populate nodes
        for level in data['levels']:
            for node in level['nodes']:
                n = Node(node['id'], node['name'])
                self.graph.add_node(n)

        logger.debug('graph is %s',self.graph.nodes())

class Node(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
