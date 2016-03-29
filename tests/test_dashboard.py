import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.handler.dashboard
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger')
f = 'tests/fixtures/cassettes/TestDashboard/'
D = gocd_parser.handler.dashboard.Dashboard

class TestDashboard:
    @vcr.use_cassette(f+'basic.yaml')
    def test_basic(self):
        '''Ensure dashboard shows expected results.'''
        d = D(g)
        assert len(d.pipelines) == 6

        assert d.paused('UserAcceptance') is True
        assert d.paused('FunctionalTests') is False
        assert d.passing('DeployProduction') is True
        assert d.passing('FunctionalTests') is False
        assert d.completed('DeployProduction') is True
        assert d.completed('FunctionalTests') is False
