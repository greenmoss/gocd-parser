import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.handler.compare
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestCompare/'
C = gocd_parser.handler.compare.Compare

class TestCompare:
    @vcr.use_cassette(f+'commits_and_pipelines.yaml')
    def test_commits_and_pipelines(self):
        '''All expected git commits and pipelines appear in the list of changes.'''
        c = C(g, 'DeployProduction', '12', '13')
        assert len(c.materials) == 10
