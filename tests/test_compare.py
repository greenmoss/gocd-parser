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
        assert c.materials[0].name == 'https://github.com/greenmoss/gocd_source'
        assert c.materials[0].branch == 'master'
        assert c.materials[0].type == 'git'
        assert len(c.materials[0].changes) == 2
        assert c.materials[0].changes[0].revision == 'dd154416726d3e813145777baef747f411dc1fca'
        assert c.materials[0].changes[0].modifier_name == 'Kurt Yoder'
        assert c.materials[0].changes[0].modifier_email == 'ktygithub@yoderhome.com'
        assert c.materials[0].changes[0].modifier_time == 1458403792
        assert c.materials[0].changes[0].comment == 'Get diagnostic output from run.sh'

        assert c.materials[9].name == 'AppDevelopment'
        assert c.materials[9].type == 'pipeline'
        assert len(c.materials[9].changes) == 4
        assert c.materials[9].changes[0].revision == 'AppDevelopment/5/Package/1'
        assert c.materials[9].changes[0].revision_url == '/go/pipelines/AppDevelopment/5/Package/1'
        assert c.materials[9].changes[0].label == '5'
        assert c.materials[9].changes[0].label_url == '/go/pipelines/value_stream_map/AppDevelopment/5'
        assert c.materials[9].changes[0].completed == 1458404255

    @vcr.use_cassette(f+'unknown_material.yaml')
    def test_none_passing(self):
        '''Unrecognized material should raise an exception.'''
        with pytest.raises(gocd_parser.handler.compare.CompareException):
            c = C(g, 'DeployProduction', '12', '13')
