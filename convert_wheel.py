import os
import re
import shutil
from setuptools import setup

ROOT_PATH = os.path.join(os.path.join(os.path.expanduser(os.path.expandvars(__file__.split('convert_wheel.py')[0]))), 'anylog_api')
# PYX_PATH = os.path.join(ROOT_PATH, 'pyx')
# if not os.path.isdir(PYX_PATH):
#     os.makedirs(PYX_PATH)
# shutil.copyfile(os.path.join(ROOT_PATH, 'python_api.py'), os.path.join(PYX_PATH, 'python_api.pyx'))

try:
    setup (
        name='AnyLog_API',
        version="beta",
        description='AnyLog API tool',
        url='https://anylog.co',
        author='AnyLog Team',
        author_email='info@anylog.co',
        license='AnyLog, Co. -  See License Agreement',
        install_requires=[
            'requests>=2.27.1'
        ],
        packages=[ROOT_PATH],
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
        ]
    )
except Exception as e:
    print(f"Failed to build AnyLog (Error: {e})")





