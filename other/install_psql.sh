if [ $# -eq 2 ]
then
   DB_USR=$1
   DB_PASSWD=$2 
else 
   echo "Postgres user & password required" 
   exit 1 
fi 

docker volume create pgdata 
docker run -d --network host --name anylog-psql -e POSTGRES_USER=${DB_USR} -e POSTGRES_PASSWORD=${DB_PASSWD} -v pgdata:/var/lib/postgresql/data --rm postgres:latest 

