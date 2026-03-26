# gRPC

## General Steps
1. Access the Docker or Kubernetes volume and compile the relevant `.proto` file(s).
2. Set parameters associated with the gRPC-based process.
3. Declare policy (not needed for `HealthCheck`).
4. Run the gRPC client.

## Example: KubeArmor Integration

This example uses the **KubeArmor** protocol file, which supports both standard telemetry and a `HealthCheck` function.

### Compile the Protocol File 

1. Access the AnyLog / EdgeLake container executable  
```shell
# Docker 
docker exec -it my-operator /bin/sh 

# Kubernetes 
kubectl exec -it my-operator -- /bin/bash
```

2. Compile the protocol file 
```shell
python3 /app/deployment-scripts/gRPC/compile.py /app/deployment-scripts/gRPC/kubearmor/kubearmor.proto
```

### Enable gRPC service  

Attach to the Docker / Kubernetes container
```shell
# Docker 
docker attach --detach-keys=ctrl-d my-operator 

# Kubernetes (ctrl-pq to detach) 
kubectl attach -it pod/anylog-master-deployment-7b4ff75fb7-mnsxf 
```