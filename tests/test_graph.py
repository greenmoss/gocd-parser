import logging
#logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.value_stream.graph
import gocd_parser.retriever.server

# reduce typing!
g = gocd_parser.retriever.server.Server('http://localhost:8153/go')
f = 'tests/fixtures/cassettes/TestGraph/'
G = gocd_parser.value_stream.graph.Graph

class TestCompare:
    @vcr.use_cassette(f+'failing_stream.yaml')
    def test_failing_stream(self):
        '''Ensure a failing stream gives us expected graph data.'''
        graph = G(g, 'DeployProduction')
        assert graph.tree.base_pipeline == 'DeployProduction'

        tree = graph.tree
        status = tree.get_status_from_base()
        assert len(tree.pipelines) == 5

        logging.debug(status)
        assert status['base_name'] == 'DeployProduction'
        assert status['schema_version'] == '1.1.0'
        assert status['base_status']['status'] == 'passing'
        assert status['base_status']['paths'] == {'passing': u'pipelines/DeployProduction/14/Deploy/1', 'failing': []}
        assert status['base_status']['seconds'] is not None
        assert status['base_status']['my_group'] == 'Production'
        assert status['base_status']['passing_label'] == '14'
        assert status['base_status']['ancestor_groups'] == [u'Development']
        assert status['base_status']['human_time'] is not None
        assert status['blocking']['FunctionalTests']['status'] == 'failing'
        assert status['blocking']['FunctionalTests']['paths'] == {'passing': u'pipelines/FunctionalTests/6/Deploy/1', 'failing': [u'tab/build/detail/FunctionalTests/9/Deploy/1/deployApplications']}
        assert status['blocking']['FunctionalTests']['seconds'] is not None
        assert status['blocking']['FunctionalTests']['my_group'] == 'Development'
        assert status['blocking']['FunctionalTests']['passing_label'] == '6'
        assert status['blocking']['FunctionalTests']['ancestor_groups'] == [u'Development']
        assert status['blocking']['FunctionalTests']['human_time'] is not None

    @vcr.use_cassette(f+'passing_stream.yaml')
    def test_passing_stream(self):
        '''Ensure a passing stream gives us expected graph data.'''
        graph = G(g, 'UserAcceptance')
        assert graph.tree.base_pipeline == 'UserAcceptance'

        tree = graph.tree
        status = tree.get_status_from_base()
        assert len(tree.pipelines) == 2

        logging.debug(status)
        assert status['base_name'] == 'UserAcceptance'
        assert status['schema_version'] == '1.1.0'
        assert status['base_status']['status'] == 'passing'
        assert status['base_status']['paths'] == {'passing': u'pipelines/UserAcceptance/6/Deploy/1', 'failing': []}
        assert status['base_status']['seconds'] is not None
        assert status['base_status']['my_group'] == 'Development'
        assert status['base_status']['passing_label'] == '6'
        assert status['base_status']['ancestor_groups'] == [u'Development']
        assert status['base_status']['human_time'] is not None
        assert status['blocking'] == {}
