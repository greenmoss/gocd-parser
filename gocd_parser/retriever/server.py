class Server(object):
    '''A simple object to store The Go server, user, and login
    credentials.'''
    def __init__(self, url, user='', password=''):
        self.url = url
        self.user = user
        self.password = password
