import os
import sys

slash_char = '/'
if sys.platform.startswith('win'):
    slash_char = '\\'

full_path = os.getcwd().split('AnyLog-API')[0] + 'AnyLog-API'
rest_dir = full_path + slash_char + 'rest'
sys.path.insert(0, rest_dir)
