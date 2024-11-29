import os
import sys
import setuptools
import configparser

# Read requirements from requirements.txt or provide defaults
REQUIREMENTS_FILE = 'requirements.txt'
REQUIREMENTS_LIST = []
if os.path.isfile(REQUIREMENTS_FILE):
    with open(REQUIREMENTS_FILE, 'r') as f:
        REQUIREMENTS_LIST = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    REQUIREMENTS_LIST = [
        'Cython>=0.0',
        'python-dotenv>=0.0',
        'requests>=0.0'
    ]

# Read metadata from setup.cfg
CONFIG_FILE = 'setup.cfg'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
PKG_NAME = config['metadata']['name']
PKG_VERSION = config['metadata']['version']
PKG_AUTHOR = config['metadata']['author']
PKG_CONTACT = config['metadata']['contact']
PKG_DESCRIPTION = config['metadata']['description']

# Define Cython extensions (if applicable)
EXTENSIONS = []
COMPILER_DIRECTIVES = {
    "language_level": sys.version_info.major,
    "boundscheck": False,
    "wraparound": False,
    "cdivision": True,
    "nonecheck": False,
    "embedsignature": True,
    "binding": False,
    "initializedcheck": False,
    "c_string_type": "unicode",
    "c_string_encoding": "ascii"
}

# Define the entry point for running the package
ENTRY_POINTS = {
    'console_scripts': [
        'anylog-api = anylog_api.__main__:main',  # Entry point to run package from CLI
    ],
}

setuptools.setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    author=PKG_AUTHOR,
    author_email=PKG_CONTACT,
    description=PKG_DESCRIPTION,
    long_description=open('README.md').read() if os.path.isfile('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/yourproject',  # Replace with your project URL
    packages=setuptools.find_packages(where='.', exclude=('tests', 'tests.*')),
    include_package_data=True,
    install_requires=REQUIREMENTS_LIST,
    ext_modules=EXTENSIONS,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Replace with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Adjust minimum required Python version if necessary
    project_urls={
        'Bug Tracker': 'https://github.com/yourusername/yourproject/issues',
        'Source Code': 'https://github.com/yourusername/yourproject',
    },
    entry_points=ENTRY_POINTS,
)
