"""
The following is based on: https://github.com/shuds13/pyexample

To run:
python3.9 setup.py bdist_wheel
"""

import os
from setuptools import setup

__NAME__ = 'anylogapi'
__VERSION__ = 'beta'
__DESCRIPTION__ = 'Connection to AnyLog via python REST connection'
__URL__ = 'https://github.com/AnyLog-co/AnyLog-API'
__AUTHOR__ = 'Ori Shadmon'
__EMAIL__ = 'info@anylog.co'
__INSTALL_REQUIRES__ = ['requests']
__CLASSIFIERS__ = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
]

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anylog_pyrest')

try:
    setup(
        name=__NAME__,
        version=__VERSION__,
        description=__DESCRIPTION__,
        url=__URL__,
        author=__AUTHOR__,
        author_email=__EMAIL__,
        license='BSD 2-clause',
        packages=[PACKAGE_DIR],
        install_requires=__INSTALL_REQUIRES__,
        classifiers=__CLASSIFIERS__
    )
except Exception as e:
    print(f"Failed to compile {PACKAGE_DIR} (Error: {e})")
