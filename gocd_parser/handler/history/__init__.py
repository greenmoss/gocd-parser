import logging

from gocd_parser.handler.history import history_page

class HistoryPagerException(Exception):
    pass

class HistoryPager(object):
    '''A handler for retrieving multiple pages of history. Note that this does
    NOT retrieve ALL pages of history. It ONLY retrieves pages until it finds
    the first passing history.'''

    def __init__(self, go_server, pipeline_name):
        self.go_server = go_server
        self.pipeline_name = pipeline_name

        self.logger = logging.getLogger(__name__+'.HistoryPager')

        self.get_pages()

        self.merged = self.pages[0]

    def get_pages(self):
        self.pages = []
        previous_page = None

        success = False
        offset = 0
        while not success:
            # look for first successful completion
            success = self.get_page(offset)
            previous_page = self.pages[-1]
            self.logger.debug('pagination: %s', previous_page.pagination)
            if not success:
                offset += previous_page.pagination['page_size']
                if offset > previous_page.pagination['total']:
                    raise HistoryPagerException('Ran out of history pages')

        assert previous_page is not None

        self.merge_onto_first()

    def merge_onto_first(self):
        '''Merge all history together, on to the first page. Note that
        this destroys "fidelity"; you would not want to look at
        self.pages after doing this.'''

        if len(self.pages) > 1:
            return

        for index in range(1, len(self.pages)):
            self.pages[0].add(self.pages[index])

    def get_page(self, offset=0):
        self.logger.debug('getting page: %d', offset)

        handler = history_page.HistoryPage(self.go_server,
                self.pipeline_name, str(offset))
        self.pages.append(handler)

        try:
            handler.set_info()
        except HistoryPagerException:
            self.logger.debug('Failed; will look for another page.')
            return False

        return True
