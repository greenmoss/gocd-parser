#!/usr/bin/env python
# This script shows an example of how to use the provided Python module
# to check some basic statistics on a GoCD server cctray.xml.
from __future__ import print_function

import json

from gocd_parser.handler import cctray
from gocd_parser.retriever import server
from gocd_parser import gocd_argparse, gocd_logger

logger = gocd_logger.get()

arg_parser = gocd_argparse.get()
args = arg_parser.parse_args()

go_server = server.Server(args.go_url, args.go_user, args.go_password)

# Retrieve the GoCD cctray information
my_handler = cctray.Cctray(go_server)
# Send its metrics to stdout
print(json.dumps(my_handler.metrics, sort_keys=True, indent=2))
