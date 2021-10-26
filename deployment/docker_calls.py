"""
1. The following is not currently used, but may be added in the futrue
2. Should change to docker via Python
    - PyPi - https://pypi.org/project/docker/
    - GitHub: https://github.com/docker/docker-py
    - docs: https://docker-py.readthedocs.io/en/stable/client.html
"""
try:
    import docker
except:
    pass


class DeployAnyLog:
    def __init__(self, exception:bool=True):
        """
        Connect to docker client
        :args:
            docker_client_path:str - path to docker socket
        :params:
            self.docker_client:docker.client.DockerClient - connection to docker
            self.password:str - docker password credentials to download AnyLog
            self.version:str - image version to use for deployment
        """
        try:
            self.docker_client = docker.DockerClient()
        except Exception as e:
            if exception is True:
                print('Failed to set docker client (Error: %s)' %  e)


    def __validate_container(self, name:str):
        """
        Validate container was deployed
        :args:
            name:str - container name
            exception:bool - whether to print exception
        :params:
            status:bool
        :return:
            if found return True, else False
        """
        status = True

        try:
            if not isinstance(self.docker_client.containers.get(container_id=name), docker.models.containers.Container):
                status = False
        except Exception as e:
            status = False

        return status

    def __validate_volume(self, name:str)->bool:
        """
        Validate if volume exists, if not create volume
        :args:
            name:str - volume name
        :params:
            is_volume:bool - whether a volume already exists
        :return:
            is_volume
        """
        try:
            is_volume =  self.docker_client.volumes.get(volume_id=name)
        except:
            is_volume = False
        if not is_volume:
            try:
                self.docker_client.volumes.create(name=name, driver='local')
            except:
                is_volume = False
            else:
                try:
                    is_volume = self.docker_client.volumes.get(volume_id=name)
                except:
                    is_volume = False

        return is_volume

    def docker_login(self, password:str, exception:bool=False):
        """
        login into docker to download AnyLog
        :args:
            password:str - docker login password
            exception:bool - whether to print exception
        :params:
            status:bool
        :return:
            status
        """
        status = True
        try:
            self.docker_client.login(username='oshadmon', password=password)
        except Exception as e:
            if exception is True:
                print("Failed to log into docker with password: '%s' (Error: %s)" % (password, e))
            status = False

        return status

    def update_image(self, build:str='predevelop', exception:bool=True)->bool:
        """
        Pull image oshadmon/anylog
        :args:
            passwd:str - login docker password
            build:str - version to build
        :params:
            status:bool
        :return:
            if fails return False, else True
        """
        # login into docker
        status = True

        try:
            self.docker_client.images.pull(repository='oshadmon/anylog:%s' % build)
        except Exception as e:
            if exception is True:
                print('Failed to pull image oshadmon/anylog:%s (Error: %s)' % (build, e))
            status = False
        else:
            if not self.check_image(exception=exception):
                if exception is True:
                    print('Failed to pull image oshadmon/anylog:%s for an unknown reason...' % build)
                status = False

        return status

    def deploy_anylog_container(self, node_name:str='anylog-test-node', build:str='predevelop', external_ip:str=None, local_ip:str=None,
                                server_port:int=2048, rest_port:int=2049, broker_port:int=None, authentication='off', auth_type='admin',
                                username:str='anylog', password:str='demo', expiration:str=None, exception:bool=True)->bool:
        """
        Deploy an AnyLog of type rest
        :sample-call:
            docker run \
                --network host \
                --name ${NODE_NAME} \
                -e NODE_TYPE=rest \
                -e ANYLOG_SERVER_PORT=${SERVER_PORT} \
                -e ANYLOG_REST_PORT=${REST_PORT} \
                -e ANYLOG_BROKER_PORT=${BROKER_PORT} \
                -e AUTHENTICATION=${$AUTHENTICATION} \
                -e AUTH_TYPE=${AUTH_TYPE} \
                -e USERNAME=${USERNAME} \
                -e PASSWORD=${PASSWORD} \
                -e EXPIRATION=${EXPIRATION} \
                -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
                -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
                -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
                -it --detach-keys="ctrl-d" --rm anylog:${BUILD}
        :args:
            node_name:str - name of the container / node
            server_port:int - TCP server port
            rest_port:int - REST server port
        :optional args:
            external_ip:str / local_ip:str - IPs are configured by default. However if the node is in a closed network
                or has multiple IPs, the user may want to use something different than the defaults.
            broker_port:int - MQTT message broker port
            username:str - authentication username
            password:str - authentication password
        :params:
            status:bool
            volume_paths:dict - key: volume_name | value: path within AnyLog
            volumes:dict - volumes related to AnyLog
            environment:dict - environment variables for docker based on arguments
        :return:
            status
        """
        status = True
        print('Deploy AnyLog')
        environment = {
            'NODE_TYPE': 'rest',
            'NODE_NAME': node_name,
            'ANYLOG_SERVER_PORT': server_port,
            'ANYLOG_REST_PORT': rest_port,
            'AUTHENTICATION': authentication,
            'AUTH_TYPE': auth_type,
            'USERNAME': username,
            'PASSWORD': password,
            'EXPIRATION': expiration
        }
        volume_paths = {
            '%s-anylog' % node_name: '/app/AnyLog-Network/anylog',
            '%s-blockchain' % node_name: '/app/AnyLog-Network/blockchain',
            '%s-data' % node_name: '/app/AnyLog-Network/data',
            '%s-local-scripts' % node_name: '/app/AnyLog-Network/local_scripts'
        }

        if external_ip is not None:
            environment['EXTERNAL_IP'] = external_ip
        if local_ip is not None:
            environment['IP'] = local_ip
        if broker_port is not None:
            environment['ANYLOG_BROKER_PORT'] = broker_port

        if not self.__validate_container(name=node_name):
            volumes = {}
            for volume in volume_paths:
                if self.__validate_volume(name=volume) is not False:
                    volumes[volume] = {'bind': volume_paths[volume], 'mode': 'rw'}

            try:
                self.docker_client.containers.run(image='oshadmon/anylog:%s' % build, auto_remove=True,
                                                  network_mode='host', detach=True, stdin_open=True, tty=True,
                                                  privileged=True, name=node_name, environment=environment,
                                                  volumes=volumes)
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy an AnyLog container (Error: %s)' % e)
            else:
                if not self.__validate_container(name=node_name):
                    status = False

        return status

    def deploy_grafana_container(self, exception:bool=True)->bool:
        """
        Deploy a Grafana v 7.5.7 as a docker container
        :sample-call:
            docker run -d -p 3000:3000 --name=grafana \
                -v grafana-data:/var/lib/grafana \
                -v grafana-log:/var/log/grafana \
                -v grafana-config:/etc/grafana \
                -e "GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel" \
                --rm grafana/grafana:7.5.7
        :args:
            exception:bool - whether to print exceptions or not
        :params:
            status:bool
        :return:
            status
        """
        status = True
        print('Deploying Grafana')
        environment = {
            'GF_INSTALL_PLUGINS': 'simpod-json-datasource,grafana-worldmap-panel'
        }
        volume_paths = {
            'grafana-data': '/var/lib/grafana',
            'grafana-log': '/var/log/grafana',
            'grafana-config': '/etc/grafana'
        }
        if not self.__validate_container(name='grafana'):
            volumes = {}
            for volume in volume_paths:
                if self.__validate_volume(name=volume) is not False:
                    volumes[volume] = {'bind': volume_paths[volume], 'mode': 'rw'}
            try:
                self.docker_client.containers.run(image='grafana/grafana:7.5.7', auto_remove=True, network_mode='host',
                                                  detach=True, stdin_open=True, tty=True, privileged=True,
                                                  name='grafana', environment=environment, volumes=volumes)
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy Grafana container (Error: %s)' % e)
            else:
                if not self.__validate_container(name='grafana'):
                    status = False

        return status

    def deploy_psql_container(self, conn_info:str, db_port:int=5432, exception:bool=True)->bool:
        """
        Deploy Postgres
        :sample-call:
            docker run \
               --network host \
               --name anylog-psql \
               -e POSTGRES_USER=${DB_USR} \
               -e POSTGRES_PASSWORD=${DB_PASSWD} \
               -p ${PORT}:${PORT} \
               -v pgdata:/var/lib/postgresql/data \
               --rm postgres:14.0-alpine
        :args:
            conn_info:str - connection information (user@ip:passwd)
            db_port:int - database port
            password:str psql password correlated to user
        :params:
            status:bool
        :return:
            status
        """
        status = True
        print('Deploying Postgres')
        if not self.__validate_container(name='anylog-psql'):
            if self.__validate_volume(name='pgdata') is False:
                volumes = {}
            else:
                volumes = {'pgdata': {'bind': '/var/lib/postgresql/data', 'mode': 'rw'}}

            try:
                self.docker_client.containers.run(image='postgres:14.0-alpine',  auto_remove=True, network_mode='host',
                                                  detach=True, stdin_open=True, tty=True, privileged=True,
                                                  name='anylog-psql',
                                                  environment={
                                                      'POSTGRES_USER': conn_info.split('@')[0],
                                                      'POSTGRES_PASSWORD': conn_info.split(':')[-1]
                                                  },
                                                  volumes=volumes
                                                  )
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy Postgres container (Error: %s)' % e)
            else:
                if not self.__validate_container(name='anylog-psql'):
                    status = False

        return status

    def stop_docker_container(self, container_name:str, exception:bool=True)->bool:
        """
        Stop docker container based on name
        :args:
            container_name:str - container name
            exception:bool - whether to print exception
        :params:
            status:bool
        :return:
            status
        """
        status = True
        try:
            container = self.client.containers.get(name=container_name)
        except:
            container = None
        print(container)




