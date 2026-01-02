import os
import json

ROOT_DIR = os.path.dirname(__file__)
with open(os.path.join(ROOT_DIR, 'NETWORK_ERRORS_GENERIC.json'), 'r') as f:
    print(json.load(f))
