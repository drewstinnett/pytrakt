#!/usr/bin/env python

from setuptools import setup

readme = open('README.md', 'r')
README_TEXT = readme.read()
readme.close()


setup(
    name='pytrakt',
    version='0.1',
    description='Python helper to trakt.tv API',
    long_description=readme,
    author='Drew Stinnett',
    author_email='drew@drewlink.com',
    url='https://github.com/drewstinnett/pytrakt',
    packages=['pytrakt'],
    test_suite='nose.collector',
    tests_require=['nose'],
    scripts=[
        'bin/rate_movies_cli.py',
    ],
    license='BSD',
)
