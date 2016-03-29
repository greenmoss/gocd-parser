import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.stream_status
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger')
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

        external = status.dump()
        assert external['base_name'] == 'DeployProduction'
        assert external['schema_version'] == '1.2.0'
        assert external['status'] == 'blocked'

        assert external['base_status']['status'] == 'passing'
        assert external['base_status']['paths'] == {'passing': u'pipelines/DeployProduction/14/Deploy/2', 'failing': []}
        assert external['base_status']['seconds'] is not None
        assert external['base_status']['my_group'] == 'Production'
        assert external['base_status']['passing_label'] == '14'
        assert external['base_status']['ancestor_groups'] == [u'Development']
        assert external['base_status']['human_time'] is not None

        assert external['blocking']['FunctionalTests']['status'] == 'failing'
        assert external['blocking']['FunctionalTests']['paths'] == {'passing': u'pipelines/FunctionalTests/6/Deploy/1', 'failing': [u'tab/build/detail/FunctionalTests/10/Deploy/1/deployApplications']}
        assert external['blocking']['FunctionalTests']['seconds'] is not None
        assert external['blocking']['FunctionalTests']['my_group'] == 'Development'
        assert external['blocking']['FunctionalTests']['passing_label'] == '6'
        assert external['blocking']['FunctionalTests']['ancestor_groups'] == [u'Development']
        assert external['blocking']['FunctionalTests']['human_time'] is not None
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['name'] == 'Kurt Yoder'
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['email'] == 'ktygithub@yoderhome.com'
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['commit_count'] == 4
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['first_commit_epoch'] == 1458423314
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['first_commit_message'] == 'Fail the AD branch'
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['first_commit_revision'] == 'ef7b1cb587f01646ecd3022150b0ba4b5dbddd58'
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['first_commit_repo'] == 'https://github.com/greenmoss/gocd_source'
        assert external['blocking']['FunctionalTests']['changes']['committers'][0]['first_commit_branch'] == 'AD'
        assert external['blocking']['FunctionalTests']['changes']['pipelines'][0]['name'] == 'AppDevelopment'
        assert external['blocking']['FunctionalTests']['changes']['pipelines'][0]['run_count'] == 2

        assert external['blocking']['UserAcceptance']['status'] == 'stopped'
        assert external['blocking']['UserAcceptance']['paths'] == {'passing': u'pipelines/UserAcceptance/7/Deploy/1', 'failing': []}
        assert external['blocking']['UserAcceptance']['seconds'] is not None
        assert external['blocking']['UserAcceptance']['my_group'] == 'Development'
        assert external['blocking']['UserAcceptance']['passing_label'] == '7'
        assert external['blocking']['UserAcceptance']['ancestor_groups'] == [u'Development']
        assert external['blocking']['UserAcceptance']['human_time'] is not None
        assert external['blocking']['UserAcceptance']['paused']['paused_by'] == 'chester'
        assert external['blocking']['UserAcceptance']['paused']['pause_reason'] == 'reasons'
