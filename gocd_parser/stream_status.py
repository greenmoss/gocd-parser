import logging
logger = logging.getLogger(__name__)

import gocd_parser.pipeline
import gocd_parser.value_stream

class StreamStatus(object):
    '''Get the status of a pipeline's value stream: passing, blocked, or
    failing. If blocking, get the information about the blockers.'''

    def __init__(self, go_server, pipeline_name, label = None):
        self.go_server = go_server
        self.pipeline = gocd_parser.pipeline.Pipeline(pipeline_name, go_server)

        if label is None:
            # get the last passing pipeline
            label = self.pipeline.get_last_passing()['label']
        self.label = label

        self.value_stream = gocd_parser.handler.value_stream.ValueStream(
                self.go_server, self.pipeline.name, self.label)

