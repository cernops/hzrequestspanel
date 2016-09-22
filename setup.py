#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'hzrequestspanel',
    version = '1.0',
    description = 'A plugin for OpenStack Dashboard Panel SNOW requests',
    author='Cloud Infrastructure Team',
    author_email='cloud-infrastructure-3rd-level@cern.ch',
    packages=['hzrequestspanel', 'hzrequestspanel/content', 'hzrequestspanel/api'],
    include_package_data = True,
)
