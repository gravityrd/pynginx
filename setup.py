#!/usr/bin/env python
"""Setup file for pynginx package"""
 
from setuptools import setup
setup(name='pynginx',
      version='0.0.1',
      description='pynginx - programmatically control Nginx config files (parse, generate, modify)',
      long_description = "pynginx a python module for accessing nginx configuration (parses the main configuration files, and the included ones too, allows you to access the whole configuration as an object tree, modify it on-the-fly, test it (save as a new config file and run nginx configtest on it)).",
      author='Pas',
      author_email='pas@gravityrd.com',
      url='http://github.com/',
      #packages=[ 'pynginx', ],
      py_modules=[ 'pynginx', ],
 
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
        ),
      license="MIT"
     )
