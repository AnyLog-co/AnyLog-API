import anylog_api.anylog_connector as anylog_connector
from anylog_api.blockchain.cmds import get_policy
from anylog_api.blockchain.cmds import post_policy

OPERATOR = "172.105.112.207:32149"
MASTER = "45.79.74.39:32049"
MASTER_TCP = "10.10.1.10:32048"

operator = anylog_connector.AnyLogConnector(conn=OPERATOR, auth=None, timeout=30)
master = anylog_connector.AnyLogConnector(conn=MASTER, auth=None, timeout=30)

cluster_policies = get_policy(conn=operator, policy_type='cluster')
for policy in cluster_policies:
    post_policy(conn=master, policy=policy, ledger_conn=MASTER_TCP, exception=True)
