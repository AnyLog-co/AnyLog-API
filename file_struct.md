* anylog_connector (class)
* anylog_connector_support (execution)
* __support__
  * JSON functions
* generic
    * GET
      * status
      * dictionary
      * node name
      * hostname
      * version
    * POST
      * dictionary
    * logs
      * reset error
      * reset event
      * start/stop echo queue
      * get error
      * get log
      * get echo queue 
      * get processes
    * networking
      * network_connection - connection to TCP, REST, msg broker
      * get connections
      * get rest calls
    * geolocation (module to get geolocation of a node)
* data
  * database
    * connect / create
    * disconnect
    * view databases
    * check if database exists 
    * drop database
  * table
    * create table
    * get tables
    * check if table exists
    * drop table
    * drop partition
    * gt virtuaal tables
  * publish_data
    * PUT data 
    * POST data 
    * run msg client
    * get msg client
    * exit msg client
    * run operator 
    * get operator
    * exit operator
    * run publisher
    * get publisher
    * exit publisher
  * streaming
    * get streaming
    * get data nodes
  * Query
* blockchain
  * create policy
    * cluster
    * node
    * config
  * prepare
  * publish
  * query
  * authentication
    * disable authentication