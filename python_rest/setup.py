from setuptools import setup
from Cython.Build import cythonize
from tqdm import tqdm
import os.path
import sys

ROOT_PATH = os.path.expanduser(os.path.expanduser(os.path.abspath(__file__)))
REQUIREMENTS = os.path.join(ROOT_PATH, 'requirements.txt')
SOURCE_PATH = os.path.join(ROOT_PATH, 'src')

DIR_LIST = []
PACKAGES = []

for dirname in os.listdir(SOURCE_PATH):
    dir_path = os.path.join(SOURCE_PATH, dirname)
    if os.path.isdir(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path) and filename.rsplit('.')[-1] == 'py':
                DIR_LIST.append(file_path)

if os.path.isfile(REQUIREMENTS):
    with open(REQUIREMENTS, 'r') as f:
        for line in f.readlines():
            if '>=' in line and line[0] != "#":
               PACKAGES.append(line.split('>')[0])

extensions = cythonize(
    DIR_LIST,
    language_level=sys.version_info.major
)

# initialize the progress bar
with tqdm(total=len(extensions)) as pbar:
    for i, ext in enumerate(extensions):
        ext.name = ext.name.replace(".py", ".so")
        setup(
            name="anylog_api",
            author_email="info@anylog.co",
            description="Copywrite by AnyLog Co.",
            long_description="API Development Tool",
            url="https://anylog.co",
            #packages=PACKAGES,
            ext_modules=[ext]
        )
        pbar.update(1)  # increment the progress bar by 1 unit

