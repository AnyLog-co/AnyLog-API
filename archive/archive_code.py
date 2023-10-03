def generate_blockchain_insert(local_publish:bool=True, platform:str=None, ledger_conn:str=None)->str:
    """
    Generate blockchain insert statement
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#the-blockchain-insert-command
    :sample command:
        blockchain insert where policy = !policy and local = true and master = !master_node
        blockchain insert where policy = !policy and local = true and blockchain = ethereum
    :args:
        local_publish:bool - A true/false value to determine an update to the local copy of the ledger
        platform:str - connected blockchain platform
        ledger_conn:str - The IP and Port value of a master node
    :params:
        command:str - generated blockchain insert command
    :return:
        command
    """
    command = 'blockchain insert where policy=!new_policy'
    if local_publish is False:
        command += " and local=false"
    else:
        command += " and local=true"

    if platform in ['ethereum', 'eos', 'jasmy']:
        command += f" and blockchain={platform}"

    if ledger_conn is not None:
        command += f' and master={ledger_conn}'

    return command