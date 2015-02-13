#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'requests',
    'elasticsearch',
    'thriftpy'
    ]

test_requires = []

setup(
    name="publication",
    version='0.1',
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
    setup_requires=["nose>=1.0", "coverage"],
    tests_require=test_requires,
    test_suite="nose.collector",
    entry_points="""\
    [paste.app_factory]
    main = publication:main
    """,
)