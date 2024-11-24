import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.post import network_connection


def network_connect(conn=anylog_connector.AnyLogConnector, params:dict={}, tcp_conn:bool=False, rest_conn:bool=False,
                    broker_conn:bool=False, destination:str=None, return_cmd:bool=False, view_help:bool=False,
                    exception:bool=False):

    external_ip = params['external_ip']
    internal_ip = params['ip']
    if 'overlay_ip' in params and params['overlay_ip']:
        internal_ip = params['overlay_ip']

    if tcp_conn is True:
        port = params['anylog_server_port']
        bind = params['tcp_bind']
        threads = params['tcp_threads']
        network_connection(conn=conn, service_type='tcp', external_ip=external_ip, internal_ip=internal_ip, port=port,
                           bind=bind, threads=threads, destination=destination, return_cmd=return_cmd,
                           view_help=view_help, exception=exception)

    if rest_conn is True:
        port = params['anylog_rest_port']
        bind = params['rest_bind']
        threads = params['rest_threads']
        timeout = params['rest_timeout']
        network_connection(conn=conn, service_type='rest', external_ip=external_ip, internal_ip=internal_ip, port=port,
                           bind=bind, threads=threads, timeout=timeout, destination=destination, return_cmd=return_cmd,
                           view_help=view_help, exception=exception)

    if broker_conn is True:
        port = params['anylog_broker_port']
        bind = params['broker_bind']
        threads = params['broker_threads']
        network_connection(conn=conn, service_type='broker', external_ip=external_ip, internal_ip=internal_ip, port=port,
                           bind=bind, threads=threads, destination=destination, return_cmd=return_cmd,
                           view_help=view_help, exception=exception)


