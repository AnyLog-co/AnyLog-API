# AnyLog-API
The AnyLog API is intended to act an easy-to-use interface between AnyLog and third-party applications. Currently, 
the code provides only support specifically for deploying a standalone node, but can easily be evolved to provide more functionality overtime. 

## Key Files
```commandline
$HOME/AnyLog-API
├── README.md
├── REST
│   ├── anylog_connection.py    <-- Python class that allows for GET, PUT and POST commands
│   ├── authentication.py       <-- authentication related functions 
│   ├── blockchain_calls.py     <-- blockchain functions (ex. GET, Declare, Drop) 
│   ├── database_calls.py       <-- Database + Partitioning functions
│   ├── deployment_calls.py     <-- Generic deployment calls (ex. `run operator`and `run mqtt client`)
│   ├── generic_get_calls.py    <-- Generic GET commands (ex. `get status`, `get event log`) 
│   ├── generic_post_calls.py   <-- Generic POST commands
│   └── support.py              <-- non-REST support functions 
└── anylog_scripts
    ├── autoexec.json                 <-- JSON used to declare varibles  
    ├── part1.py                      <-- Deploy node to act as an “Operator” node with an MQTT client  
    ├── part2.py                      <-- Declare polciies for a standalone node 
    └── combined_parts.py             <-- scripts part1.py and part2.py as a signle process 
```

## Deployment
**Step 1**: Start AnyLog with configuration based on autoexec.json and TCP/REST connections
```commandline
python3.9 $HOME/AnyLog-Network/source/cmd/user_cmd.py \
process $HOME/AnyLog-API/anylog_scripts/autoexec.json \
    and run tcp server !external_ip !anylog_server_port !ip !anylog_server_port \ 
    and run rest server !ip !anylog_rest_port
```

**Step 2**: Deploy node to act as an “Operator” node with an MQTT client  
```commandline
python3.9 $HOME/AnyLog-API/anylog_scripts/part1.py
```

**Step 3**: Declare Policies against blockchain – execute only once
```commandline
python3.9 $HOME/AnyLog-API/anylog_scripts/part2.py
```


**Note**: Alternatively to Steps 1 and 2, user can just run the following: 
```commandline
python3.9 $HOME/AnyLog-API/anylog_scripts/combined_parts.py
```

