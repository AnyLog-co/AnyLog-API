# AnyLog API 

**Goal**: 
1. User installs pip AnyLog API via pip 
```shell
python3 -m pip install --upgrade pip 
python3 -m pip install --upgrade anylog_api
```

2. Connect to AnyLog
```python3
from anylog_api.anylog_rest_api import AnyLogRest

anylog_conn = AnyLogRest()
```