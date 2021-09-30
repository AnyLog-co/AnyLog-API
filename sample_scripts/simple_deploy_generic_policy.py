import json

import __init__
import anylog_api
import errors

LOCATIONS = {
    'Los Angeles, CA': '33.8121, -117.91899', # LA
    'San Francisco, CA': '37.786163522, -122.404498382', # SF
    'Seattle, WA': '47.620182, -122.34933', # Seattle
    'Philadelphia, PN': '39.949566, -75.15026', # Phili
    'Arlington, VA': '38.870983,  -77.05598', # Arlington
    'Washington DC': '38.89773, -77.03653', # DC
    'New York City, NY': '40.758595, -73.98447', # NYC
    'Orlando, FL': '28.37128, -81.51216', # Orlando
    'Houston, TX': '29.97980499267578, -95.56627655029297', # Houston
    'Las Vegas': '36.1147, -115.1728' # Las Vegas
}


def main():
    """
    The following is an example of adding an hierarchy of personalized policise to the AnyLog blockchain.
    :params:
        rest_conn:str - REST IP and PORT to connect to
        master_node:str - TCP master node information
        auth:tuple - REST authentication information
        timeout:int - REST timeout period
        policies:dict - dict of personalized policies
    """
    rest_conn='10.0.0.80:2049'
    master_node='10.0.0.80:2048'
    auth=None
    timeout=30

    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=rest_conn, auth=auth, timeout=timeout)

    # personalized hierarchy
    policy = { 'panel': {
        'name': None,
        'city': None,
        'loc': None,
        'owner': 'AFG'
    }}

    for location in LOCATIONS:
        policy['panel']['name'] = 'Panel %s' % str(int(list(LOCATIONS).index(location)) + 1)
        policy['panel']['city'] = location
        policy['panel']['loc'] = LOCATIONS[location]
        send_policy = "<policy=%s>" % json.dumps(policy)
        r, error = anylog_conn.post_policy(policy=send_policy, master_node=master_node)
        errors.post_error(conn=anylog_conn, command="blockchain post policy: " % policy, r=r, error=error, exception= True)

if __name__ == '__main__':
    main()