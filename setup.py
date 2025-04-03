import os
import setuptools
import configparser

ROOT_PATH = os.path.abspath(__file__).split(os.path.basename(__file__))[0]
README_FILE = os.path.join(ROOT_PATH, 'README.md')
CONFIG_FILE = os.path.join(ROOT_PATH, 'setup.cfg')
REQUIREMENTS_FILE = os.path.join(ROOT_PATH, 'requirements.txt')

# Read requirements from requirements.txt
REQUIREMENTS_LIST = []
if os.path.isfile(REQUIREMENTS_FILE):
    with open(REQUIREMENTS_FILE, 'r') as f:
        REQUIREMENTS_LIST = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read metadata from setup.cfg
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

PKG_NAME = config['metadata'].get('name', 'anylog-api')
PKG_VERSION = config['metadata'].get('version', '0.0.1')
PKG_AUTHOR = config['metadata'].get('author', 'AnyLog Co.')
PKG_CONTACT = config['metadata'].get('contact', 'info@anylog.co')
PKG_DESCRIPTION = config['metadata'].get('description', 'Tool for AnyLog / EdgeLake RESTful API')

# Define the entry point for running the package (if applicable)
ENTRY_POINTS = {
    'console_scripts': [
        'anylog-api = anylog_api.anylog_connector:main',  # Update if there's a CLI entry point
    ],
}

setuptools.setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    author=PKG_AUTHOR,
    author_email=PKG_CONTACT,
    description=PKG_DESCRIPTION,
    long_description=open(README_FILE).read() if os.path.isfile(README_FILE) else "",
    long_description_content_type="text/markdown",
    url=config["metadata"].get("source", "https://github.com/AnyLog-co/AnyLog-API"),
    packages=setuptools.find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=REQUIREMENTS_LIST,  # Installs dependencies from requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    project_urls={
        "Bug Tracker": "https://github.com/AnyLog-co/AnyLog-API/issues",
        "Documentation": config["metadata"].get("docs", "https://github.com/AnyLog-co/documentation"),
        "Source Code": config["metadata"].get("source", "https://github.com/AnyLog-co/AnyLog-API"),
    },
)
