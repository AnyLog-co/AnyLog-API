import os
import re
import shutil
from setuptools import setup

ROOT_PATH = os.path.join(os.path.join(os.path.expanduser(os.path.expandvars(__file__.split('convert_wheel.py')[0]))), 'anylog_api')
PYX_PATH = os.path.join(ROOT_PATH, 'pyx')
if not os.path.isdir(PYX_PATH):
    os.makedirs(PYX_PATH)
shutil.copyfile(os.path.join(ROOT_PATH, 'python_api.py'), os.path.join(PYX_PATH, 'python_api.pyx'))

try:
    setup (
        name='AnyLogAPI',
        version=1,
        description='AnyLog API tool',
        url='https://anylog.co',
        author='AnyLog Team',
        author_email='info@anylog.co',
        license='AnyLog, Co. -  See License Agreement',
        install_requires=[],
        packages=[PYX_PATH],
        classifiers=[
            'Development Status :: 1 - Initial Release',
            'Intended Audience :: AnyLog User(s) with Ai-Ops Development',
            'License :: AnyLog, Co. Copyright 2021 - See License Agreement',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.9',
        ],
    )
except Exception as e:
    print(f"Failed to build AnyLog (Error: {e})")





