import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.handler.value_stream
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestValueStream/'
V = gocd_parser.handler.value_stream.ValueStream

class TestValueStream:
    @vcr.use_cassette(f+'only_upstream.yaml')
    def test_only_stream(self):
        '''Ensure a value stream with only upstream nodes gives us expected data.'''
        vsm = V(g, 'DeployProduction', '14')
        assert len(vsm.graph) == 11

        node = vsm.graph.node['DeployStaging']
        assert node['name'] == 'DeployStaging'
        assert node['locator'] == '/go/tab/pipeline/history/DeployStaging'
        assert node['level'] == 3
        assert node['depth'] == 1
        assert node['node_type'] == 'PIPELINE'
        assert node['instances'][0]['counter'] == 15
        assert node['instances'][0]['stages'][0]['status'] == 'Passed'

        node = vsm.graph.node['93c90510b74bdc41e0a15b8f2ebfd470f445089651b50238857f6b17819bb0ee']
        assert node['name'] == 'https://github.com/gocd-demo/webinar-code.git'
        assert node['locator'] == ''
        assert node['level'] == 0
        assert node['depth'] == 1
        assert node['node_type'] == 'GIT'
        assert node['instances'][0]['comment'] == 'Update triggerfile.txt'
