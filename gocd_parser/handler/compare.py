import re
import logging
logger = logging.getLogger(__name__)

from lxml import html, etree

from gocd_parser.retriever import url

class CompareException(Exception):
    pass

class Compare(object):
    '''Extract repository and pipeline diff information from the GoCD
    comparison pages.

    A comparison URL example is:
        http://localhost:8153/go/compare/DeployProduction/12/with/13
    '''

    material_regexes = {
            #  Git - URL: https://github.com/greenmoss/gocd_source, Branch: master
            'git': re.compile('^ Git - URL: ([^,]+), Branch: (\S+)'),
            #  Pipeline - UserAcceptance
            'pipeline': re.compile('^ Pipeline - (\S+)'),
            }

    def __init__(self, go_server, pipeline_name, label1, label2):
        '''Currently we are able to parse git and pipeline materials.'''
        self.go_server = go_server

        self.materials = []

        logger.debug("handling comparison")

        path = '/compare/'+pipeline_name+'/'+label1+'/with/'+label2
        retrieved = url.URL( self.go_server, path)

        self.set_materials(retrieved)

    def set_materials(self, retrieved):
        '''Set the materials, using an xpath search of the page.'''

        tree = html.fromstring(''.join(retrieved.contents))
        materials = tree.xpath(
                '//div[@id="tab-content-of-checkins"]/descendant::div[@class="material_title"]/strong/../..'
                )
        for index, material in enumerate(materials):
            title = material.find('div').find('strong').text
            logger.debug('parsing %s',title)

            changes = material.find('table').findall('tr[@class="change"]')
            logger.debug('found changes: %d',len(changes))

            matched = False
            for material_type, regex in Compare.material_regexes.items():
                matches = regex.match(title)
                if not matches: continue

                matched = True
                m = getattr(self, 'get_'+material_type)(matches)
                for change in changes:
                    m.add_change(change)
                self.materials.append(m)
                break
            
            if not matched:
                raise CompareException("Material does not match any known types in Compare.material_regexes!")

    def get_git(self, matches):
        return GitMaterial(matches.group(1), matches.group(2))

    def get_pipeline(self, matches):
        return PipelineMaterial(matches.group(1))

class GitMaterial(object):
    '''Add information about a git commit from a GoCD material.'''
    def __init__(self, name, branch):
        self.name = name
        self.branch = branch
        self.type = 'git'

        logger.debug('adding GitMaterial: %s, branch %s', self.name, self.branch)

        self.changes = []

    def add_change(self, change):
        self.changes.append(GitChange(change))

class PipelineMaterial(object):
    '''Add information about a pipeline from a GoCD material.'''
    def __init__(self, name):
        self.name = name
        self.type = 'pipeline'

        logger.debug('adding PipelineMaterial: %s', self.name)

        self.changes = []

    def add_change(self, change):
        self.changes.append(PipelineChange(change))

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
