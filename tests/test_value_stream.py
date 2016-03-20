import logging
logging.basicConfig(level=logging.DEBUG)

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
