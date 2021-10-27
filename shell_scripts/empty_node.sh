# Deploy an AnyLog instance with nothing running on it

if [ $# -eq 1 ]
then
   BUILD=${1:-predevelop}
else
   echo "Postgres user & password required"
   exit 1
fi
NODE_NAME=anylog-empty-node

docker run --network host --name ${NODE_NAME} \
    -e NODE_TYPE=none \
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
    -d -it --detach-keys='ctrl-d' --rm oshadmon/anylog:${BUILD}

