# Based on: https://www.ibm.com/docs/en/eam/4.5?topic=nodes-horizon-apis
import json
import re
import requests


def get_data(url:str):
    try:
        r = requests.get(url=url)
    except Exception as error:
        print(f"Failed to get data from {url} (Error; {error})")
        exit(1)
    else:
        if not 200 <= int(r.status_code) <= 299:
            print(f"Failed to get data from {url} (Network Error; {r.status_code}")
            exit(1)

    try:
        return r.json()
    except Exception as error:
        print(f"Failed to extract result from {url} (Error: {error})")


def parse_worker_status(content):
    output = []
    log_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+)$')

    if len(content) >= 1:
        for line in content:
            match = log_pattern.match(line)
            if match:
                row = {'timestamp': None, 'log': None}
                row['timestamp'], row['log'] = match.groups()
                output.append(row)
            else:
                output.append({'content': line})

    return output


def main(url:str):
    data = {}
    output = get_data(url=url)
    for key in output:
        if 'worker_status' in key:
            data[key] = parse_worker_status(output[key])
        else:
            for table in output[key]:
                if table not in data:
                    data[table] = {}
                for column in output[key][table]:
                    if column == 'name':
                        pass
                    elif isinstance(output[key][table][column], list):
                        data[table][column] = parse_worker_status(output[key][table][column])
                    elif isinstance(output[key][table][column], dict):
                        for sub_column in output[key][table][column]:
                            data[table][f'{column}_{sub_column}'] = output[key][table][column][sub_column]
                    else:
                        data[table][column] = output[key][table][column]

    for table in data:
        print(f"Table Name: {table} | Data: {json.dumps(data[table])}")


if __name__ == '__main__':
    """
    Original Data:
        {"workers":{
            "AgBot":{"name":"AgBot","status":"terminated","subworker_status":{}},
            "Agreement":{"name":"Agreement","status":"initialized","subworker_status":{"NodePolicyWatcher":"started"}},
            "Container":{"name":"Container","status":"initialized","subworker_status":{}},
            "Download":{"name":"Download","status":"initialized","subworker_status":{}},
            "ExchangeChanges":{"name":"ExchangeChanges","status":"initialized","subworker_status":{}},
            "ExchangeMessages":{"name":"ExchangeMessages","status":"initialized","subworker_status":{}},
            "Governance":{"name":"Governance","status":"initialized","subworker_status":{"ContainerGovernor":"started","MicroserviceGovernor":"started","NodeStatus":"started","SurfaceExchErrors":"started"}},
            "ImageFetch":{"name":"ImageFetch","status":"initialized","subworker_status":{}},
            "Kube":{"name":"Kube","status":"initialized","subworker_status":{}},
            "NodeManagement":{"name":"NodeManagement","status":"initialized","subworker_status":{"NMPMonitor":"started"}},
            "Resource":{"name":"Resource","status":"initialized","subworker_status":{}}},
            "worker_status_log":["2024-09-10 18:09:55 Worker AgBot: started.","2024-09-10 18:09:55 Worker AgBot: initialization failed.","2024-09-10 18:09:55 Worker Agreement: started.","2024-09-10 18:09:55 Worker Governance: started.","2024-09-10 18:09:55 Worker Governance: subworker NodeStatus added.","2024-09-10 18:09:55 Worker Governance: subworker SurfaceExchErrors added.","2024-09-10 18:09:55 Worker Governance: subworker ContainerGovernor added.","2024-09-10 18:09:55 Worker Governance: subworker MicroserviceGovernor added.","2024-09-10 18:09:55 Worker ExchangeMessages: started.","2024-09-10 18:09:55 Worker ExchangeMessages: initialized.","2024-09-10 18:09:55 Worker Governance: subworker NodeStatus started.","2024-09-10 18:09:55 Worker Governance: subworker SurfaceExchErrors started.","2024-09-10 18:09:55 Worker Governance: subworker ContainerGovernor started.","2024-09-10 18:09:55 Worker Governance: subworker MicroserviceGovernor started.","2024-09-10 18:09:55 Worker Container: started.","2024-09-10 18:09:55 Worker Resource: started.","2024-09-10 18:09:55 Worker ImageFetch: started.","2024-09-10 18:09:55 Worker ImageFetch: initialized.","2024-09-10 18:09:55 Worker Kube: started.","2024-09-10 18:09:55 Worker Kube: initialized.","2024-09-10 18:09:55 Worker AgBot: terminated.","2024-09-10 18:09:55 Worker ExchangeChanges: started.","2024-09-10 18:09:55 Worker NodeManagement: started.","2024-09-10 18:09:55 Worker NodeManagement: subworker NMPMonitor added.","2024-09-10 18:09:55 Worker NodeManagement: subworker NMPMonitor started.","2024-09-10 18:09:55 Worker Download: started.","2024-09-10 18:09:55 Worker Download: initialized.","2024-09-10 18:09:55 Worker Resource: initialized.","2024-09-10 18:09:58 Worker Container: initialized.","2024-09-10 18:10:01 Worker ExchangeChanges: initialized.","2024-09-10 18:10:11 Worker Agreement: subworker NodePolicyWatcher added.","2024-09-10 18:10:11 Worker Agreement: initialized.","2024-09-10 18:10:11 Worker Agreement: subworker NodePolicyWatcher started.","2024-09-10 18:10:15 Worker Governance: initialized.","2024-09-10 18:10:15 Worker NodeManagement: initialized."]
            }
        }
    
    Formatted output: 
    Table Name: AgBot | Data: {"status": "terminated"}
    Table Name: Agreement | Data: {"status": "initialized", "subworker_status_NodePolicyWatcher": "started"}
    Table Name: Container | Data: {"status": "initialized"}
    Table Name: Download | Data: {"status": "initialized"}
    Table Name: ExchangeChanges | Data: {"status": "initialized"}
    Table Name: ExchangeMessages | Data: {"status": "initialized"}
    Table Name: Governance | Data: {"status": "initialized", "subworker_status_ContainerGovernor": "started", "subworker_status_MicroserviceGovernor": "started", "subworker_status_NodeStatus": "started", "subworker_status_SurfaceExchErrors": "started"}
    Table Name: ImageFetch | Data: {"status": "initialized"}
    Table Name: Kube | Data: {"status": "initialized"}
    Table Name: NodeManagement | Data: {"status": "initialized", "subworker_status_NMPMonitor": "started"}
    Table Name: Resource | Data: {"status": "initialized"}
    Table Name: worker_status_log | Data: [{"timestamp": "2024-09-10 18:09:55", "log": "Worker AgBot: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker AgBot: initialization failed."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Agreement: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker NodeStatus added."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker SurfaceExchErrors added."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker ContainerGovernor added."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker MicroserviceGovernor added."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker ExchangeMessages: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker ExchangeMessages: initialized."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker NodeStatus started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker SurfaceExchErrors started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker ContainerGovernor started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Governance: subworker MicroserviceGovernor started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Container: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Resource: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker ImageFetch: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker ImageFetch: initialized."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Kube: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Kube: initialized."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker AgBot: terminated."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker ExchangeChanges: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker NodeManagement: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker NodeManagement: subworker NMPMonitor added."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker NodeManagement: subworker NMPMonitor started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Download: started."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Download: initialized."}, {"timestamp": "2024-09-10 18:09:55", "log": "Worker Resource: initialized."}, {"timestamp": "2024-09-10 18:09:58", "log": "Worker Container: initialized."}, {"timestamp": "2024-09-10 18:10:01", "log": "Worker ExchangeChanges: initialized."}, {"timestamp": "2024-09-10 18:10:11", "log": "Worker Agreement: subworker NodePolicyWatcher added."}, {"timestamp": "2024-09-10 18:10:11", "log": "Worker Agreement: initialized."}, {"timestamp": "2024-09-10 18:10:11", "log": "Worker Agreement: subworker NodePolicyWatcher started."}, {"timestamp": "2024-09-10 18:10:15", "log": "Worker Governance: initialized."}, {"timestamp": "2024-09-10 18:10:15", "log": "Worker NodeManagement: initialized."}]
    """
    print(main(url="http://172.232.157.208:8510/status/workers"))

