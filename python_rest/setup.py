# based on: https://towardsdatascience.com/how-to-upload-your-python-package-to-pypi-de1b363a1b3
from setuptools import setup, find_packages

def __get_requirements()->dict:
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f.readlines():
            if '>=' in line:
                requirements.append(line.split('>=')[0])
    return requirements


setup(
    name='anylog-network',
    version='1.0',
    license=None,
    author='AnyLog Co.',
    author_email='info@anylog.co',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    keywords='anylog project',
    install_requires=__get_requirements(),
)
