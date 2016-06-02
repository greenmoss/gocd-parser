import pytest
import vcr

import gocd_parser.handler.history.history_page
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestHistoryPage/'
HP = gocd_parser.handler.history.history_page.HistoryPage

class TestHistoryPage:
    @vcr.use_cassette(f+'none_passing.yaml')
    def test_none_passing(self):
        '''Pipeline has never passed.'''
        p = HP(g, 'FunctionalTests', '')
        with pytest.raises(gocd_parser.handler.history.history_page.HistoryPageException):
            p.set_info()

    @vcr.use_cassette(f+'passing.yaml')
    def test_passing(self):
        '''Pipeline is passing now.'''
        p = HP(g, 'FunctionalTests', '')
        p.set_info()
        assert p.first['name'] == 'FunctionalTests'
        assert p.passing is True
        assert p.last_completed['counter'] == 1
        assert p.last_passing['counter'] == 1
        assert p.first_of_current_failures is None
        assert p.failure_duration is None

    @vcr.use_cassette(f+'one_passing_two_failed.yaml')
    def test_one_passing_two_failed(self):
        '''Pipeline passed once, then failed twice.'''
        p = HP(g, 'DeployProduction', '')
        p.set_info()
        assert p.first['name'] == 'DeployProduction'
        assert p.passing is False
        assert p.last_completed['counter'] == 4
        assert p.last_passing['counter'] == 2
        assert p.first_of_current_failures is not None
        assert p.first_of_current_failures['counter'] == 3
        assert p.failure_duration is not None

    @vcr.use_cassette(f+'page_of_failures.yaml')
    def test_page_of_failures(self):
        '''Pipeline passed before, but current page shows only failures.'''
        p = HP(g, 'DeployStaging', '')
        with pytest.raises(gocd_parser.handler.history.history_page.HistoryPageException):
            p.set_info()

    @vcr.use_cassette(f+'two_pages.yaml')
    def test_two_pages(self):
        '''After joining two pages of history into one, the sum of pages has the correct info.'''
        p = HP(g, 'DeployProduction', '')
        p2 = HP(g, 'DeployProduction', '10')
        p.add(p2)
        assert len(p.pipelines) == 11
        assert p.first['counter'] == 11
        assert p.pipelines[0]['counter'] == 11
        assert p.pipelines[-1]['counter'] == 1

    @vcr.use_cassette(f+'two_nonmatching_pages.yaml')
    def test_two_nonmatching_pages(self):
        '''Ensure we can't join two disparate pipeline histories.'''
        p = HP(g, 'DeployProduction', '')
        p2 = HP(g, 'UserAcceptance', '')
        with pytest.raises(gocd_parser.handler.history.history_page.HistoryPageException):
            p.add(p2)

    @vcr.use_cassette(f+'passed_failed_running.yaml')
    def test_passed_failed_running(self):
        '''Pipeline passed, then failed, and is now building.'''
        g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger')
        p = HP(g, 'FunctionalTests', '')
        p.set_info()
        assert p.first['name'] == 'FunctionalTests'
        assert p.passing is False
        assert p.last_completed['counter'] == 15
        assert p.last_passing['counter'] == 13
        assert p.first_of_current_failures is not None
        assert p.first_of_current_failures['counter'] == 14
        assert p.failure_duration is not None
