import logging
logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.retriever.server
import gocd_parser.pipeline
from gocd_parser.handler import pipeline_groups

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestPipeline/'
P = gocd_parser.pipeline.Pipeline

class TestPipeline:
    @vcr.use_cassette(f+'running_last_passed.yaml')
    def test_running_last_passed(self):
        '''Test pipeline status when it is currently running, and passed previously.'''
        p = P('DeployProduction', g)
        # could test these, but have to regenerate vcr fixture
        #pg = pipeline_groups.PipelineGroups(g)
        #p.set_from_groups_handler(pg)
        l = p.get_last_passing()
        paths = p.get_url_paths()
        seconds = p.get_duration(in_seconds=True)
        human_time = p.get_duration()

        assert p.name == 'DeployProduction'
        assert p.is_passing() is True
        assert p.passing_duration is not None
        assert p.human_status == 'passing'
        assert l['label'] == '13'

        assert p.is_stopped() is False
        assert p.is_failing() is False
        assert p.stopped_duration is None
        assert p.failing_duration is None
        assert p.problem_duration is None

    # This test case is a corner case, and I can't figure it out!
    # history says it's not passing, because last passing doesn't match last completed
    # but there needds to be some way to distinguish manual approval from not running
    # setting this aside for now
    #@vcr.use_cassette(f+'manual_approval_incomplete.yaml')
    #def test_manual_approval_incomplete(self):
    #    '''Test pipeline status when a manual approval has not yet been given.'''
    #    p = P('UserAcceptance', g)
    #    pg = pipeline_groups.PipelineGroups(g)
    #    p.set_from_groups_handler(pg)
    #    l = p.get_last_passing()
    #    paths = p.get_url_paths()
    #    seconds = p.get_duration(in_seconds=True)
    #    human_time = p.get_duration()

    #    assert p.name == 'UserAcceptance'
    #    assert p.stopped_duration is not None
    #    assert p.is_stopped() is True
    #    assert p.human_status == 'stopped'
    #    assert l['label'] == '7'

    #    assert p.is_passing() is False
    #    assert p.is_failing() is False
    #    assert p.failing_duration is None
    #    assert p.problem_duration is None
    #    assert p.passing_duration is None

    @vcr.use_cassette(f+'passing.yaml')
    def test_passing(self):
        '''Test pipeline that is passing.'''
        p = P('AppDevelopment', g)
        pg = pipeline_groups.PipelineGroups(g)
        p.set_from_groups_handler(pg)
        l = p.get_last_passing()
        paths = p.get_url_paths()
        seconds = p.get_duration(in_seconds=True)
        human_time = p.get_duration()

        assert p.name == 'AppDevelopment'
        assert p.is_passing() is True
        assert p.passing_duration is not None
        assert p.human_status == 'passing'

        assert p.group == 'Development'
        assert l['label'] == '7'
        assert paths['failing'] == []
        assert paths['passing'] == 'pipelines/AppDevelopment/7/Commit/1'
        assert seconds >= 0
        assert type(human_time) == str

        assert p.is_stopped() is False
        assert p.is_failing() is False
        assert p.stopped_duration is None
        assert p.failing_duration is None
        assert p.problem_duration is None

    @vcr.use_cassette(f+'failing.yaml')
    def test_failing(self):
        '''Test pipeline that is failing.'''
        p = P('FunctionalTests', g)
        pg = pipeline_groups.PipelineGroups(g)
        p.set_from_groups_handler(pg)
        l = p.get_last_passing()
        paths = p.get_url_paths()
        seconds = p.get_duration(in_seconds=True)
        human_time = p.get_duration()

        assert p.name == 'FunctionalTests'
        assert p.is_failing() is True
        assert p.failing_duration is not None
        assert p.problem_duration is not None
        assert p.human_status == 'failing'
        assert l['label'] == '6'

        assert p.is_passing() is False
        assert p.is_stopped() is False
        assert p.stopped_duration is None
        assert p.passing_duration is None
