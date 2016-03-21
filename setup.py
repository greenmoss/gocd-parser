'''
    The proper way to install this package is use pip to install it. If you
    want to install this local copy, use this command:

        pip install .

    If you don't use pip to install, then 'pip uninstall' won't work as
    expected.
'''

from distutils.core import setup
from setuptools import find_packages
from os import listdir
from os.path import dirname, join, isfile, isdir
import sys

import gocd_parser.version

setup_dir = dirname(__file__)
package_name = 'gocd_parser'

scripts = []
for thing in listdir('bin'):
    path = join('bin', thing)
    if isfile(path):
        scripts.append(path)

def req(file_name):
    return open(join(setup_dir, file_name)).readlines()

setup(
    name=package_name,
    version=gocd_parser.version.__version__,
    description='Libraries for parsing GoCD APIs',
    author='Kurt Yoder',
    author_email='kyoder@gmail.com',
    url='https://github.com/greenmoss/gocd-parser',
    package_dir={ package_name: 'gocd_parser' },
    packages=find_packages(),
    install_requires=req('requirements.txt'),
    scripts=scripts,
    tests_require=req('requirements-testing.txt'),
    test_suite='py.test',
    )
