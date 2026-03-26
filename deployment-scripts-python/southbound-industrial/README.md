# Southbound Industrial 

When ingesting data from industrial devices such as OPC-UA, Modbus, or EtherIP, the process involves two main steps.

AnyLog/EdgeLake stores incoming industrial data per-table, per data point, ensuring each data point is uniquely tracked 
and managed.

1. **Create a Policy for Each Data Point** - A policy defines how a specific industrial data point should be stored and 
processed. This is created once for each data point via the AnyLog CLI, generating a unique blockchain policy.


**Command**:
```anylog
proces deployment-scripts/southbound-industrial/etherip_tags.al 
```

**Sample Policy**:
```json
{'tag' : {
    'dbms' : 'opcua_demo',
    'table' : 't1',
    'protocol' : 'opcua',
    'class' : 'variable',
    'ns' : 2,
    'node_sid' : 'D1001VFDStop',
    'datatype' : 'Double',
    'parent' : 'VFD_CNTRL_TAGS',
    'path' : 'Root/Objects/DeviceSet/WAGO 750-8210 PFC200 G2 4ETH XTR/Resources/Application/GlobalVars/VFD_CNTRL_TAGS/D1001VFDStop',
    'id' : 'b48e075ce41e0333619b95366aac5e5a',
    'date' : '2025-07-15T01:08:31.457608Z',
    'ledger' : 'global'
  }
}
```

2. **Begin Data Ingestion** - Once the policies are created, data ingestion can begin.

**Command**:
```anylog
proces deployment-scripts/southbound-industrial/etherip_client.al 
```

For convenience, this entire two-step process can be automated using: [industrial_policy.al](../southbound-industrial/industrial_policy.al). 