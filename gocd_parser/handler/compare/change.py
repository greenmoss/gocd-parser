from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from dateutil import parser
import pytz

class CommonChange(object):
    '''Common methods for handling material changes.'''
    def set_revision(self):
        self.revision = self.text_from_class('revision')
        logger.debug('adding change revision %s',self.revision)

    def text_from_class(self, class_name):
        '''Get joined, stripped text from a td with the named class.'''
        return(
                ''.join(self.change.find(
                    'td[@class="'+class_name+'"]'
                    ).itertext()).strip()
                )

class GitChange(CommonChange):
    '''Add information about a git change from a GoCD material.'''
    def __init__(self, change):
        self.change = change

        self.set_revision()
        self.comment = self.text_from_class('comment')

class PipelineChange(CommonChange):
    '''Add information about a pipeline change from a GoCD material.'''
    def __init__(self, change):
        self.change = change

        self.set_revision()
        self.label = self.text_from_class('label')

        completed = self.text_from_class('completed_at')
        parsed_date = parser.parse(completed)
        # strftime('%s') is not portable?
        # http://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
        self.completed = int((parsed_date - datetime(1970,1,1).replace(tzinfo = pytz.utc)).total_seconds())
        logger.debug('completed at %s, epoch %d',completed, self.completed)
