#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

install_requires = [
    'requests>=2.6.0',
    'elasticsearch>=1.3.0',
    'cython>=0.22',
    'thriftpy>=0.2.0',
    'xylose'
    ]

test_requires = []

setup(
    name="Publication Stats Thrift",
    version='0.1.2',
    description="A SciELO RPC server to retrieve publication statistics from the SciELO Network ",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    license="BSD 2-clause",
    url="http://docs.scielo.org",
    keywords='scielo statistics',
    packages=['publication'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: Services",
    ],
    dependency_links=[
        "git+https://github.com/scieloorg/xylose@v0.5b#egg=xylose"
    ],
    tests_require=test_requires,
    install_requires=install_requires,
    entry_points="""\
    [console_scripts]
    publicationstats_thriftserver = publication.thrift.server:main
    publicationstats_loaddata = processing.loaddata:main
    """,
)