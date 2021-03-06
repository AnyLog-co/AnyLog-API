import os
import sys


def import_dirs():
    slash_char = '/'
    if sys.platform.startswith('win'):
        slash_char = '\\'

    full_path = os.getcwd().split('AnyLog-API')[0] + slash_char + 'AnyLog-API'

    rest_dir = full_path + slash_char + 'rest'
    sys.path.insert(0, rest_dir)

    support_dir = full_path + slash_char + 'support'
    sys.path.insert(0, support_dir)
