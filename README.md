# AnyLog-API
The AnyLog API is intended to act an easy-to-use interface between AnyLog and third-party applications via REST.

## Node Setup
1. Download AnyLog-API
```shell
cd $HOME ; git clone https://github.com/AnyLog-co/AnyLog-API
```

2. Install Requirements
   * ast 
   * dotenv 
   * json 
   * os 
   * requests 
   * yaml
```shelll
python3.9 -m pip install -r $HOME/AnyLog-API/python_rest/requirements.txt
 ```

## Base Code
```python3
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('README.md')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector

# connect to AnyLog 
anylog_conn = AnyLogConnector(conn='127.0.0.1:32049', auth='username,password', timeout=30)

"""
using methods in python_rest, easily communicate with the AnyLog node via REST 
"""
```