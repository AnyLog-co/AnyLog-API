import anylog_api.anylog_connector as anylog_connector


def run_msg_broker(conn:anylog_connector.AnyLogConnector, broker:str, port:int=None, username:str=None,
                       password:str=None, log:bool=False, topic:bool='*', dbms:str='my_database',
                       table:str='table_name', values:dict={}): # , view_help:bool=False, return_cmd:bool=False,
                       # exception:bool=False):
    cmd = f"<run msg client where broker={broker}"
    if port is not None:
        cmd += f" and port={port}"
    if username is not None:
        cmd += f" and username={username}"
    if password is not None:
        cmd += f" and passwword={password}"
    cmd += " and log=false"
    if log is True:
        cmd = cmd.replace("false", "true")
    cmd += f" and topic=(\n\tname={topic} and \n\tdbms={dbms} and \n\ttable={table} and"
    if values:
        for key, values_dict in values.items():
            if 'value' not in values_dict and 'type' not in values_dict:
                continue
            if values_dict['type'] == 'timestamp':
                cmd += f"\n\tcolumn.{key}.timestamp={values_dict["value"]} and"
                if "bring" in values_dict["value"]:
                    cmd = cmd.replace(values_dict["value"], f'"{values_dict["value"]}"')
            else:
                cmd += f"\n\tcolumn.{key}=("
                for param, param_value in values_dict.items():
                    cmd += f"{param}={param_value} and "
                    if "bring" in param_value:
                        cmd = cmd.replace(param_value, f'"{param_value}"')
                cmd = cmd.rstrip(" and ") +')'
        cmd = cmd.rstrip(" and") + "\n)>"

    print(cmd)


if __name__ == '__main__':
    run_msg_broker(conn=None, broker='local', values={"timestamp": {"type": "timestamp", "value": "now()"}, "col1": {"type": "float", "value": "bring [col1]", "optional": 'true'}})
