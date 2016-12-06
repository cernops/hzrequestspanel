#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = 'hzrequestspanel',
    version = '1.2',
    description = 'A plugin for OpenStack Dashboard Panel SNOW requests',
    author='Cloud Infrastructure Team',
    author_email='cloud-infrastructure-3rd-level@cern.ch',
    classifiers = [
        'Environment :: OpenStack',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=find_packages(),
    include_package_data = True,
)
