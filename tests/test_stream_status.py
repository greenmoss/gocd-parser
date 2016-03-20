import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.stream_status
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestStreamStatus/'
S = gocd_parser.stream_status.StreamStatus

class TestStreamStatus:
    @vcr.use_cassette(f+'failing_stream.yaml')
    def test_failing_stream(self):
        '''Ensure a failing stream gives us expected status.'''
        status = S(g, 'DeployProduction')
        assert status.pipeline.name == 'DeployProduction'
        assert status.label == '14'
        assert len(status.value_stream.graph) == 11
        assert len(status.value_stream.graph.edges()) == 11
