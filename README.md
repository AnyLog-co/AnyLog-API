# AnyLog API 

The AnyLog API enables seamless interaction with _AnyLog_ or _EdgeLake_ nodes to manage distributed data seamlessly. 
This README provides setup instructions and sample usage for initializing a node, inserting data, and querying data.

The code supports both [asynchronous requests](anylog_api/async_anylog_connector.py) using _aiohttp_ library, and 
[synchronous](anylog_api/anylog_connector.py) using standard _requests_ library. 

## Install pip package 
1. download repository 
```shell
cd $HOME/ ; git clone https://github.com/AnyLog-co/AnyLog-API ; cd $HOME/AnyLog-API/
```

2. prepare python3 
```shell
python3 -m pip install --upgrade pip wheel setuptools
```

3. Create pip package 
```shell
python setup.py sdist bdist_wheel
```

4. On a different venv install AnyLog 
```shell
# create venv
cd $HOME
python3 -m venv venv 

# Install AnyLog-API 
python3 -m pip install $HOME/AnyLog-API/dist/anylog_api-0.0.0-py2.py3-none-any.whl 
```

5. Use AnyLog-API based on [examples](examples/)