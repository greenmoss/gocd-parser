import logging
logger = logging.getLogger(__name__)

class CommonChange(object):
    '''Common methods for handling material changes.'''
    def set_revision(self):
        self.revision = ''.join(self.change.find('td[@class="revision"]').itertext()).strip()
        logger.debug('adding change revision %s',self.revision)

class GitChange(CommonChange):
    '''Add information about a git change from a GoCD material.'''
    def __init__(self, change):
        self.change = change
        self.set_revision()

class PipelineChange(CommonChange):
    '''Add information about a pipeline change from a GoCD material.'''
    def __init__(self, change):
        self.change = change
        self.set_revision()
