"""
The following compiles code in source/ directory to .c and .io files respectivly 
"""
import os
import re
import shutil

from distutils.core import Extension, setup
from Cython.Build import cythonize

# user changeable parameters 
__NAME__ = 'anylogapi'
__VERSION__ = '1.0'
__DESCRIPTION__ = 'Connection to AnyLog via python REST connection'
__URL__ = 'https://github.com/AnyLog-co/AnyLog-API'
__AUTHOR__ = 'Ori Shadmon'
__EMAIL__ = 'info@anylog.co'
__REQUIREMENTS__ = ['requests']
__LANGUAGE_LEVEL__ = 3


FILE_PATH = os.path.join(os.path.join(os.path.expanduser(os.path.expandvars(__file__))).split('compile_io.py')[0], 'anylog_pyrest')

for fname in os.listdir(FILE_PATH):
    print(fname)
    if fname != '__pycache__':
        file_path = os.path.join(FILE_PATH, fname)
        extensions = Extension(name=fname.split('.')[0], sources=[file_path])
        setup(
            name=__NAME__,
            version=ANYLOG_VERSION,
            description=__DESCRIPTION__,
            url=__URL__,
            author=__AUTHOR__,
            author_email=__EMAIL__,
            license=__LICENSE__,
            install_requires=__REQUIREMENTS__,
            include_package_data=True,
            ext_modules=cythonize(
                    extensions,
                    compiler_directives={
                        "language_level": __LANGUAGE_LEVEL__,
                        "always_allow_keywords": True,
                    },
                    build_dir=os.path.join(dir_path, "build"), # needs to be explicitly set, otherwise pollutes package sources
                )
            )


