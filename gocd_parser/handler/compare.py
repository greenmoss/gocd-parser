import logging
logger = logging.getLogger(__name__)

from lxml import html, etree

from gocd_parser.retriever import url

class Compare(object):
    '''Extract repository and pipeline diff information from the GoCD
    comparison pages.

    A comparison URL example is:
        http://localhost:8153/go/compare/DeployProduction/12/with/13
    '''

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
            logger.debug('material %d: %s', index, etree.tostring(material, pretty_print=True))
            self.materials.append(Material())

class Material(object):
    '''This contains common code for different kinds of GoCD materials.'''
    pass
