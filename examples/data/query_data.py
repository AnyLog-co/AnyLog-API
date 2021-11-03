import argparse
import import_packages
import_packages.import_dirs()
import anylog_api
import get_cmd

def main():
    """
    Example of querying AnyLog data, the set values can be used to query AnyLog's demo network using 239.12.151:2049
    :positional arguments:
        rest_conn             REST connection information
    :optional arguments:
        -h, --help            show this help message and exit
        -a AUTH, --auth AUTH  REST authentication information (default: None)
        -t TIMEOUT, --timeout TIMEOUT   REST timeout period (default: 30)
    :params:
        anylog_conn:anylog_api.AnyLocConnect - connection to AnyLog API
        dbms:str - logical database name
        query:str - SELECT query to execute
        format:str - The format of the result set	(options: json, table)
        stat:bool - whether or not to print the statistics
        timezone:str - used for time values in the result set	local (options: utc, local)
        include:list - comma separated list of tables to query against

    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='23.239.12.151:2049', help='REST connection information')
    parser.add_argument('-a', '--auth', type=tuple, default=(), help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='REST timeout period')
    args = parser.parse_args()

    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    dbms = "litsanleandro"
    query = "SELECT min(timestamp), max(timestamp), min(value), max(value), avg(value), count(*) FROM percentagecpu_sensor WHERE timestamp >= NOW() - 1 day"
    timezone = "local"
    include = "ping_sensor"

    # Table format with statistics
    format="table"
    stat=True
    output = get_cmd.execute_query_print(conn=anylog_conn, dbms=dbms, query=query,  format=format, stat=stat,
                                         timezone=timezone, include=include, exception=True)
    print(output + "\n")

    # JSON format without statistics
    format = "json"
    stat = False
    output = get_cmd.execute_query_print(conn=anylog_conn, dbms=dbms, query=query, format=format, stat=stat,
                                         timezone=timezone, include=include, exception=True)
    for row in output['Query']:
        print(row)


if __name__ == '__main__':
    main()