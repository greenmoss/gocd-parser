import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.handler.cctray
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestCctray/'
C = gocd_parser.handler.cctray.Cctray

class TestCctray:
    @vcr.use_cassette(f+'basic.yaml')
    def test_failing_stream(self):
        '''Ensure cctray shows expected results.'''
        c = C(g)
        assert c.metrics['stages'] == 18
        assert c.metrics['pipelines'] == 6
        assert c.metrics['builds'] == 53
        assert c.metrics['status_totals']['Failure'] == 1
        assert c.metrics['status_totals']['Success'] == 17
