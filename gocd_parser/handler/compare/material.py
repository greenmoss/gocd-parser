import logging
logger = logging.getLogger(__name__)

from . import change

class GitMaterial(object):
    '''Add information about a git commit from a GoCD material.'''
    def __init__(self, name, branch):
        self.name = name
        self.branch = branch
        self.type = 'git'

        logger.debug('adding GitMaterial: %s, branch %s', self.name, self.branch)

        self.changes = []

    def add_change(self, c):
        self.changes.append(change.GitChange(c))

class PipelineMaterial(object):
    '''Add information about a pipeline from a GoCD material.'''
    def __init__(self, name):
        self.name = name
        self.type = 'pipeline'

        logger.debug('adding PipelineMaterial: %s', self.name)

        self.changes = []

    def add_change(self, c):
        self.changes.append(change.PipelineChange(c))
