
from six.moves.urllib.request import (
    install_opener,
    build_opener,
    HTTPBasicAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    urlopen
)

import logging
import six
from six.moves.urllib.parse import urlsplit

class URL(object):
    '''Retrieve from a Go server.'''

    def __init__(self, go_server, path=''):
        self.go_server = go_server

        self.logger = logging.getLogger(__name__+'.URL')

        self.contents = []

        full_url = go_server.url + path

        if self.go_server.user and self.go_server.password:
            self.logger.debug("logging in as %s"%self.go_server.user)
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, full_url,
                    self.go_server.user,
                    self.go_server.password)
            install_opener(build_opener(HTTPBasicAuthHandler(passman)))

        self.logger.debug("reading url %s"%full_url)

        file_handle = urlopen(full_url)
        if six.PY2:
            for line in file_handle:
                self.contents.append(line)
        else:
            for line in file_handle:
                self.contents.append(line.decode())
        self.logger.debug('line count: %d'%len(self.contents))

        file_handle.close()

        path_parts = urlsplit(full_url).path.split('/')
        last = path_parts[-1]

        # /path/to/something/
        if last is '':
            path_parts.pop()
            last = path_parts[-1]

        self.path_parts = path_parts
        self.file_name = last
        self.file_path = '/'.join(path_parts[0:-1])
