import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import add_conditions
from anylog_api.blockchain.cmds import get_policy
from anylog_api.generic.scheduler import run_schedule_task
from anylog_api.__support__ import json_dumps

def __execute_monitoring(conn:anylog_connector.AnyLogConnector, headers:dict, command:str, monitor_options:dict,
                         view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = {}
    for option in monitor_options:
        if all(True is x for x in [monitor_options[option], return_cmd]):
            output[option] = command % option
        elif option is True and view_help is False:
            headers['command'] = command % option
            output[option] = extract_get_results(conn=conn, headers=headers, exception=exception)
    return output


def get_stats(conn:anylog_connector.AnyLogConnector, service='operator', topic:str='summary', json_format:bool=True,
              destination:str="", return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    Provide statistics on a service enabled omn the node.
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLake
        service:str
        topic:str
        json_format:bool - is JSON format
        destination:str - remote destination to send request
        view_help:bool - print cmd information
        exception:bool - print exceptions
    :params:
        output
        headers:dict - REST headers
    """
    output = None
    headers = {
        "command": "get stats",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if json_format is True:
        add_conditions(headers=headers, service=service, topic=topic, format=json_format)
    else:
        add_conditions(headers=headers, service=service, topic=topic)

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_disk_information(conn:anylog_connector.AnyLogConnector, usage:bool=True, free:bool=True, total:bool=True,
                         used:bool=True, percentage:bool=True, path:str='.', destination:str="", return_cmd:bool=False,
                         view_help:bool=False, exception:bool=False):
    """
    Get information on the status of the disk addressed by the path
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLake
        usage:bool
        free:bool
        total:bool
        used:bool
        percentage:bool
        json_format:bool - is JSON format
        destination:str - remote destination to send request
        view_help:bool - print cmd information
        exception:bool - print exceptions
    :params:
        output
        headers:dict - REST headers
    """
    monitor_options = {
        "usage": usage,
        "free": free,
        "total": total,
        "used": used,
        "percentage": percentage
    }
    command = f"get disk %s {path}"
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'].split("%s")[0], exception=exception)

    output = __execute_monitoring(conn=conn, headers=headers, command=command, monitor_options=monitor_options,
                                  view_help=view_help, return_cmd=return_cmd, exception=exception)
    return output


def get_node_cpu_info(conn:anylog_connector.AnyLogConnector, cpu_percent:bool=True, cpu_times:bool=True,
                      cpu_times_percent:bool=True, getloadavg:bool=True, destination:str="", return_cmd:bool=False,
                      view_help:bool=False, exception:bool=False):
    """
    Get information on the status of the disk addressed by the path
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLake
        usage:bool
        free:bool
        total:bool
        used:bool
        percentage:bool
        json_format:bool - is JSON format
        destination:str - remote destination to send request
        view_help:bool - print cmd information
        exception:bool - print exceptions
    :params:
        output
        headers:dict - REST headers
    """
    monitor_options = {
        "cpu_percent": cpu_percent,
        "cpu_times": cpu_times,
        "cpu_times_percent": cpu_times_percent,
        "getloadavg": getloadavg
    }
    command = f"get node info %s"
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'].split("%s")[0], exception=exception)

    output = __execute_monitoring(conn=conn, headers=headers, command=command, monitor_options=monitor_options,
                                  view_help=view_help, return_cmd=return_cmd, exception=exception)

    return output


def get_disk_io_counters(conn:anylog_connector.AnyLogConnector, read_count:bool=True, write_count:bool=True,
                         read_bytes:bool=True, write_bytes:bool=True, write_time:str="", destination:str=None,
                         return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    output = None
    monitor_options = {
        "read_count": read_count,
        "write_count": write_count,
        "read_bytes": read_bytes,
        "write_bytes": write_bytes,
        "write_time": write_time
    }
    command = f"get node info disk_io_counters %s"
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'].split("%s")[0], exception=exception)
    if all(False is monitor_options[x] for x in monitor_options):
        headers['command'] = headers['command'].split("%s")[0]
        if return_cmd is True:
            output = headers['command']
        elif view_help is False:
            output = extract_get_results(conn=conn, headers=headers, exception=exception)
    else:
        output = __execute_monitoring(conn=conn, headers=headers, command=command, monitor_options=monitor_options,
                                      view_help=view_help, return_cmd=return_cmd, exception=exception)

    return output


def get_swap_memory(conn:anylog_connector.AnyLogConnector, total:bool=True, used:bool=True, free:bool=True,
                    percent:bool=True, sin:bool=True, sout:bool=True, destination:str="", return_cmd:bool=False,
                    view_help:bool=False, exception:bool=False):
    output = None
    monitor_options = {
        "total": total,
        "used": used,
        "free": free,
        "percent": percent,
        "sin": sin,
        "sout": sout
    }
    command = f"get node info swap_memory %s"
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'].split("%s")[0], exception=exception)
    if all(False is monitor_options[x] for x in monitor_options):
        headers['command'] = headers['command'].split("%s")[0]
        if return_cmd is True:
            output = headers['command']
        elif view_help is False:
            output = extract_get_results(conn=conn, headers=headers, exception=exception)
    else:
        output = __execute_monitoring(conn=conn, headers=headers, command=command, monitor_options=monitor_options,
                                      view_help=view_help, return_cmd=return_cmd, exception=exception)

    return output


def get_net_io_counters(conn:anylog_connector.AnyLogConnector, bytes_sent:bool=True, bytes_recv:bool=True,
                        packets_sent:bool=True, packets_recv:bool=True, errin:bool=True, errout:bool=True,
                        dropin:bool=False,  dropout:bool=False, destination:str="", return_cmd:bool=False,
                        view_help:bool=False, exception:bool=False):
    """
    Get information on the status of the disk addressed by the path
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLake
        usage:bool
        free:bool
        total:bool
        used:bool
        percentage:bool
        json_format:bool - is JSON format
        destination:str - remote destination to send request
        view_help:bool - print cmd information
        exception:bool - print exceptions
    :params:
        output
        headers:dict - REST headers
    """
    monitor_options = {
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
        "packets_sent": packets_sent,
        "packets_recv": packets_recv,
        "errin": errin,
        "errout": errout,
        "dropin": dropin,
        "dropout": dropout,
    }
    command = f"get node info %s"
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'].split("%s")[0], exception=exception)

    output = __execute_monitoring(conn=conn, headers=headers, command=command, monitor_options=monitor_options,
                                  view_help=view_help, return_cmd=return_cmd, exception=exception)

    return output
