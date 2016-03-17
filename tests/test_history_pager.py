import pytest
import vcr

import gocd_parser.handler.history
import gocd_parser.retriever.server

import logging
#logging.basicConfig(level=logging.DEBUG)

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestHistoryPager/'
HP = gocd_parser.handler.history.HistoryPager

class TestHistoryPager:
    @vcr.use_cassette(f+'passing_previous_page.yaml')
    def test_passing_previous_page(self):
        '''Pipeline passed, but the passing run was on the previous history page.'''
        p = HP(g, 'DeployStaging')
        assert len(p.pages) == 2
        assert p.pages[0].first['name'] == 'DeployStaging'
        assert len(p.pages[0].pipelines) == 12
        assert p.pages[0].passing is False
        assert p.pages[0].last_completed['counter'] == 12
        assert p.pages[0].last_passing['counter'] == 1
        assert p.pages[0].first_of_current_failures is not None
        assert p.pages[0].first_of_current_failures['counter'] == 2
        assert p.pages[0].failure_duration is not None
