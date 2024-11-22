# import requests
#
# CONN = '192.168.86.220:2148'
#
# try:
#     r = requests.get(url=f'http://{CONN}', headers={'command': 'get dictionary', 'User-Agent':'AnyLog/1.23'})
# except requests.RequestException as error:
#     print(error)
# except Exception as error:
#     print(error)
# else:
#     if not 200 <= int(r.status_code) < 300:
#         print(r.status_code)
#     else:
#         print(r.text.replace('\n', '').replace('\r','').split('anylog_server_port')[-1].split(""))

k = {'TCP' : {'Status' : 'Running',
          'Details' : 'Listening on: 192.168.86.220:2048, Threads Pool: 6'},
 'REST' : {'Status' : 'Running',
           'Details' : 'Listening on: 73.202.142.172:2148 and 192.168.86.220:2148, Threa'
                       'ds Pool: 6, Timeout: 30, SSL: False'},
 'Operator' : {'Status' : 'Not declared'},
 'Blockchain Sync' : {'Status' : 'Not declared'},
 'Scheduler' : {'Status' : 'Running',
                'Details' : 'Schedulers IDs in use: [0 (system)]'},
 'Blobs Archiver' : {'Status' : 'Not declared'},
 'MQTT' : {'Status' : 'Not declared'},
 'Message Broker' : {'Status' : 'Not declared',
                     'Details' : 'No active connection'},
 'SMTP' : {'Status' : 'Not declared'},
 'Streamer' : {'Status' : 'Not declared'},
 'Query Pool' : {'Status' : 'Running',
                 'Details' : 'Threads Pool: 3'},
 'Kafka Consumer' : {'Status' : 'Not declared'},
 'gRPC' : {'Status' : 'Not declared'},
 'Publisher' : {'Status' : 'Not declared'},
 'Distributor' : {'Status' : 'Not declared'},
 'Consumer' : {'Status' : 'Not declared'}}
print(list(k))