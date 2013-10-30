#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tellfl',
    version='0.1',
    description='Analyse TfL Oyster journey history reports',
    author='William Mayor',
    author_email='mail@tellfl.co.uk',
    url='www.tellfl.co.uk',
    packages=['tellfl'],
    scripts=['scripts/tellfl'],
    package_data={
        'tellfl': ['assets/schema.sql']
    },
    install_requires=['docopts']
)
