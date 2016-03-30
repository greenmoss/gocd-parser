#!/usr/bin/env python
# This script uses the built-in Python module to check whether a given
# pipeline is passing, failing, or blocked. To check for a blocked
# pipeline, it looks through all upstream pipelines for any that are
# failing or paused.
from __future__ import print_function

import json

import gocd_parser.stream_status
from gocd_parser.retriever import server
from gocd_parser import gocd_argparse, gocd_logger

# uncomment to set a default "INFO" logger
#logger = gocd_logger.get()

arg_parser = gocd_argparse.get()
arg_parser.add_argument(
        '-n', '--pipeline_name',
        required=True,
        help='The name of the pipeline to check',
        )
args = arg_parser.parse_args()

go_server = server.Server(args.go_url, args.go_user, args.go_password)

# Retrieve the graph of the value stream
status = gocd_parser.stream_status.StreamStatus(go_server, args.pipeline_name)
# Send its blocker info to stdout
print( json.dumps( status.dump(), sort_keys=True, indent=2))
