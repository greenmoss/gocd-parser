import logging
logging.basicConfig(level=logging.DEBUG)

import pytest
import vcr

import gocd_parser.retriever.url
import gocd_parser.retriever.server

# reduce typing!
f = 'tests/fixtures/cassettes/TestURL/'
U = gocd_parser.retriever.url.URL

class TestURL:
    @vcr.use_cassette(f+'api_authentication.yaml')
    def test_api_authentication(self):
        '''Ensure authentication on an api URL succeeds (user chester, pass badger).'''
        g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger')
        u = U(g, '/api/pipelines/AppDevelopment/status/')
        assert u.contents[0] == '{"paused":false,"schedulable":true,"pausedBy":"","pausedCause":"","locked":false}'
        assert len(u.contents) == 1
        logging.debug(u.contents)
        assert u.path_parts == ['', 'go', 'api', 'pipelines', 'AppDevelopment', 'status']
        assert u.file_path == '/go/api/pipelines/AppDevelopment'

    @vcr.use_cassette(f+'api_authentication_failed.yaml')
    def test_api_authentication_failed(self):
        '''Ensure authentication failure on an api URL (user chester, pass badger1).'''
        g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger1')
        with pytest.raises(gocd_parser.retriever.url.URLException):
            c = U(g, '/api/pipelines/AppDevelopment/status/')

    @vcr.use_cassette(f+'authenticated_vsm.yaml')
    def test_authenticated_vsm(self):
        '''Ensure authenticated user can retrieve value stream map .json file.'''
        g = gocd_parser.retriever.server.Server('http://localhost:8153/go', 'chester', 'badger')
        u = U(g, '/pipelines/value_stream_map/AppDevelopment/7.json')
        assert u.contents[0][0:50] == '{"current_pipeline":"AppDevelopment","levels":[{"n'
        assert len(u.contents) == 1
        assert u.path_parts == ['', 'go', 'pipelines', 'value_stream_map', 'AppDevelopment', '7.json']
        assert u.file_path == '/go/pipelines/value_stream_map/AppDevelopment'
