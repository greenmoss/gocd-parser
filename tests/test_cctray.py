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
        assert c.pipelines['AppDevelopment']['build_count'] == 7
        assert c.pipelines['AppDevelopment']['lastBuildLabel'] == '7'
        assert c.pipelines['AppDevelopment']['stages']['UnitTest']['activity'] == 'Sleeping'
        assert c.pipelines['AppDevelopment']['stages']['UnitTest']['lastBuildEpoch'] == 1458423047

        assert c.pipelines['FunctionalTests']['lastBuildStatus'] == 'Failure'
        assert c.pipelines['FunctionalTests']['lastBuildLabel'] == '9'
        assert c.pipelines['FunctionalTests']['lastBuildEpoch'] == 1458437100

        assert c.metrics['stages'] == 18
        assert c.metrics['pipelines'] == 6
        assert c.metrics['builds'] == 53
        assert c.metrics['status_totals']['Failure'] == 1
        assert c.metrics['status_totals']['Success'] == 17
