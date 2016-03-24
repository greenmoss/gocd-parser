import six
from six.moves.urllib.parse import urlsplit
import logging
logger = logging.getLogger(__name__)

import requests

class URLException(Exception):
    pass

class URL(object):
    '''Retrieve from a Go server.'''

    def __init__(self, go_server, path=''):
        self.go_server = go_server

        self.contents = []

        full_url = go_server.url + path
        logger.debug("reading url %s"%full_url)

        if self.go_server.user and self.go_server.password:
            logger.debug("logging in as %s"%self.go_server.user)
            r = requests.get(full_url, auth=(self.go_server.user,
                self.go_server.password))
        else:
            r = requests.get(full_url)

        # TODO: return r instead! Let objects just use this as is!

        if r.status_code != 200:
            raise URLException('Retrieval of %s failed with code %d', full_url,
                    r.status_code)

        for line in r.iter_lines():
            self.contents.append(line)

        path_parts = urlsplit(full_url).path.split('/')
        last = path_parts[-1]

        # /path/to/something/
        if last is '':
            path_parts.pop()
            last = path_parts[-1]

        self.path_parts = path_parts
        self.file_name = last
        self.file_path = '/'.join(path_parts[0:-1])
