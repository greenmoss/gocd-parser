gocd-parser
===========

This Python library parses [Thoughtworks GoCD server](http://www.go.cd)
APIs.

# Usage

## Scripts
Run the scripts in `bin` with option `--help`.

All of these scripts output json. So they should be usable by any other
scripts on your system, without needing to import as a Python module.

## Modules
You can also import the modules and use them directly. For examples of
how to do this, refer to the scripts in the `bin` directory.

# Installation

* See `requirements.txt`.

## Ubuntu

* `apt-get install libz-dev liblz-dev libxslt1-dev python-dev`

# Testing

## Automated
* `pip install -r requirements-testing.txt`
* `py.test`

## As a user
* Follow the [Thoughtworks instructions to set up a testing GoCD server](http://www.go.cd/2014/09/09/Go-Sample-Virtualbox.html)
* Run your tests against [the test VM](http://localhost:8153/go)
    * Example invocation: `get_value_stream_status.py -g http://localhost:8153/go -n Deploy_Consumer`
* To test value stream status detection, pause the `Consumer_Website`
  pipeline.
* Now `get_value_stream_status.py` will show the above pipeline is
  blocking.

# Authors

* Kurt Yoder (kyoder@gmail.com)
* Dustin Spicuzza (dustin@virtualroadside.com)
