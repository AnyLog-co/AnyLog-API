<<COMMENT
The following deploys AnyLog with nothing running on it
COMMENT

if [ $# -eq 1 ]
then
    BUILD=$1
else: 
    BUILD=predevelop
    echo "Build type is set to predevelop" 
fi

NODE_NAME=empty-anylog-node 

docker run --network host --name ${NODE_NAME} \
    -e NODE_TYPE=none \
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
    -d -it --detach-keys="ctrl-d" --rm oshadmon/anylog:${BUILD}

