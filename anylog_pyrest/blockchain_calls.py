from anylog_connection import AnyLogConnection
import support

def blockchain_sync(anylog_conn:AnyLogConnection, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, exception:bool=False)->bool:
    """
    Enable automatic blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20configuration.md#synchronize-the-blockchain-data-with-a-local-copy-every-30-seconds
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        blockchain_source:str - source where data is coming from (default: master node)
        blockchain_destination:str - destination where data will be stored locally (default: file)
        sync_time:str - how often to sync
        ledger_conn:str - connection to blockchain ledger (for master use IP:Port)
        exception:bool - Whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        "command": f"run blockchain sync where source={blockchain_source} and time={sync_time} and dest={blockchain_destination} and connection={ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True and r is False:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status

def create_generic_policy(policy_type:str, name:str, company:str, hostname:str, external_ip:str, local_ip:str,
                          anylog_server_port:int, anylog_rest_port:int, location:str="Unknown", country:str="Unknown",
                          state:str="Unknown", city:str="Unknown", exception:bool=False)->str:
    """
    Create policy for Master, Publisher or Query
    """
    policy = {
        policy_type: {
            "name": name,
            "company": company,
            "hostname": hostname,

        }
    }