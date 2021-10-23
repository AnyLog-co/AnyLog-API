import json

import __init__
import anylog_api

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
    rest_conn='45.33.41.185:2049'
    master_node='45.33.41.185:2048'
    auth=None
    timeout=30

    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=rest_conn, auth=auth, timeout=timeout)

    # personalized hierarchy
    policy = { 'nwe_policy': {
        'city': None,
        'loc': None,
        'Company': 'AFG'
    }}

    for location in LOCATIONS:
        policy['location']['city'] = location
        policy['location']['loc'] = LOCATIONS[location]
        send_policy = "<policy=%s>" % json.dumps(policy)
        anylog_conn.post_policy(policy=send_policy, master_node=master_node)

    print(list(LOCATIONS))


if __name__ == '__main__':
    main()