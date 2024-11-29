import os
import shutil
import glob

# Paths
root_dir = os.getcwd()  # Current directory
dist_dir = os.path.join(root_dir, 'dist')  # Wheel output directory

# Step 1: Move wheel content to root path
if os.path.exists(dist_dir):
    for file in os.listdir(dist_dir):
        full_file_path = os.path.join(dist_dir, file)
        if os.path.isfile(full_file_path):
            shutil.move(full_file_path, root_dir)  # Move files to root directory

# Step 2: Remove unwanted directories and files
dirs_to_remove = ['dist', 'build']
files_to_remove_patterns = ['*.pyc', '*.pyo']

for dir_name in dirs_to_remove:
    dir_path = os.path.join(root_dir, dir_name)
    if os.path.exists(dir_path):
        os.chmod(dir_path, 777)
        shutil.rmtree(dir_path)

for pattern in files_to_remove_patterns:
    for file_path in glob.glob(os.path.join(root_dir, pattern)):
        os.remove(file_path)

# Step 3: Clean up `anylog_api` folder
anylog_api_dir = os.path.join(root_dir, 'anylog_api')
if os.path.exists(anylog_api_dir):
    for file in os.listdir(anylog_api_dir):
        file_path = os.path.join(anylog_api_dir, file)
        if os.path.isfile(file_path) and not file.endswith('.py'):
            os.remove(file_path)

