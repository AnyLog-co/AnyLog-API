# Functions

Every function has an `async_` version and a sync wrapper with the same arguments (`get_status` / `async_get_status`).
Functions that send a command take `remote_destination` (send the request through the connected node to another agent) and `exec_mode` (`ExecMode.EXECUTE` | `COMMAND` | `HELP` | `INFO`).

* [anylog_rest_api](src/core/anylog_rest_api.py) - REST client - the only module that talks HTTP to an AnyLog/EdgeLake node
	* `update_exec_mode` - Change how commands run through this connection behave by default
	* `async_get` / `get` - Generic GET request against AnyLog/EdgeLake
	* `async_post` / `post` - Generic POST request against AnyLog/EdgeLake
	* `async_get_via_post` / `get_via_post` - Execute a GET-style AnyLog command by sending it as an HTTP POST
	* `async_put` / `put` - Generic PUT request against AnyLog/EdgeLake
	* `async_help` / `help` - Print AnyLog's help text - the full command list, or help for one command
* [status](src/generic/status.py) - Node state - status, running services and connectivity to the rest of the network
	* `async_get_status` / `get_status` - Get the node's status
	* `async_get_processes` / `get_processes` - Get the node's services (processes) and their state
	* `async_check_service_status` / `check_service_status` - Check whether a service is running, based on `get processes`
	* `async_test_node` / `test_node` - Test the connected node's TCP / REST services and its connection to the metadata
	* `async_test_network` / `test_network` - Test the connection from the connected node to every node in the network
* [config](src/generic/config.py) - Node configuration - dictionary (variables), setting variables and stopping services
	* `async_get_dictionary` / `get_dictionary` - Get the node's dictionary (AnyLog variables)
	* `async_get_value` / `get_value` - Get a single variable from the node's dictionary
	* `async_set_var` / `set_var` - Set one or more AnyLog variables - one `set` command per key
	* `async_exit_service` / `exit_service` - Stop a specific service - stopping the node itself (`exit node`) isn't supported via REST
* [logs](src/generic/logs.py) - Node logs - error log, event log and echo queue
	* `async_get_error_log` / `get_error_log` - Get the node's error log
	* `async_get_event_log` / `get_event_log` - Get the node's event log
	* `async_reset_error_log` / `reset_error_log` - Clear the node's error log
	* `async_reset_event_log` / `reset_event_log` - Clear the node's event log
	* `async_get_echo_queue` / `get_echo_queue` - Get the node's echo queue
	* `async_reset_echo_queue` / `reset_echo_queue` - Clear the node's echo queue
	* `async_echo_queue_state` / `echo_queue_state` - Enable or disable the echo queue
* [rule_engine](src/generic/rule_engine.py) - Rule engine - schedulers and the tasks that run on them
	* `async_run_scheduler` / `run_scheduler` - Start a scheduler - skipped if it's already declared
	* `async_get_scheduler` / `get_scheduler` - Get one scheduler, or all of them
	* `async_reset_scheduler` / `reset_scheduler` - Reset a scheduler - declares it first if it doesn't exist yet
	* `async_exit_scheduler` / `exit_scheduler` - Stop a scheduler - skipped if it isn't declared
	* `async_run_task` / `run_task` - Schedule a task - declares the scheduler first if one is given and it doesn't exist yet
* [enable_services](src/generic/enable_services.py) - Enable node services
	* `async_enable_operator` / `enable_operator` - Start the operator service - skipped if it's already running
* [dbms](src/data_management/dbms.py) - Logical databases and tables - list, check, connect and create
	* `async_list_databases` / `list_databases` - List the logical databases the node is connected to
	* `async_is_database` / `is_database` - Check whether the node is connected to a logical database
	* `async_connect_dbms` / `connect_dbms` - Connect the node to a logical database - skipped if it's already connected
	* `async_list_tables` / `list_tables` - List the tables of a logical database
	* `async_is_table` / `is_table` - Check whether a table exists locally on the node
	* `async_create_table` / `create_table` - Create a table in a logical database - skipped if it already exists
* [insert](src/data_management/insert.py) - Publish data into AnyLog - POST (through a message client topic) or PUT (directly into a table)
	* `async_post` / `post` - Publish data via POST - routed by the node's message client, mapped by `topic`
	* `async_put` / `put` - Publish data via PUT - written directly into db_name.table_name, no topic mapping needed
* [query](src/data_management/query.py) - SQL queries against AnyLog - build the `sql` command from python values and run it
	* `build_query` - Build the AnyLog `sql` command string without sending it (see `async_query` for the arguments)
	* `async_query` / `query` - Run a SQL query against AnyLog
* [blockchain](src/metadata/blockchain.py) - Blockchain (metadata) - ledger database, querying policies, publishing policies and syncing with the master
	* `async_connect_blockchain` / `connect_blockchain` - Connect the node to the `blockchain` logical database (master nodes) - skipped if it's already connected
	* `async_create_table_ledger` / `create_table_ledger` - Create the `ledger` table in the `blockchain` database - skipped if it already exists
	* `extract_bring` - Local (python-side) equivalent of AnyLog's `bring`
	* `async_blockchain_get` / `blockchain_get` - Get policies from the blockchain, with an optional bring - done either by AnyLog or locally
	* `async_publish_policy` / `publish_policy` - Publish a policy to the blockchain - skipped if a matching policy already exists
	* `async_blockchain_sync_master` / `blockchain_sync_master` - Start syncing the node's copy of the metadata with the master - skipped if the sync is already running
* [policy_definition](src/metadata/policy_definition.py) - Build AnyLog policies as dicts - publish the result separately (blockchain.async_publish_policy)
	* `async_generic_policy` / `generic_policy` - Build a policy of any type, content taken as-is
	* `async_config_policy` / `config_policy` - Build a configuration policy - networking + the scripts a node runs at startup
	* `async_node_policy` / `node_policy` - Build a node policy (master, operator, query, publisher) - node defaults, overridden by the params given
	* `async_cluster_policy` / `cluster_policy` - Build a cluster policy - operators reference it by ID ("cluster" in the operator policy)
	* `async_object_policy` / `object_policy` - Build an object policy - publish it first, then use its ID as `object_id` in the UNS policy
	* `async_uns_policy` / `uns_policy` - Build a UNS (unified namespace) policy that points to an object policy
