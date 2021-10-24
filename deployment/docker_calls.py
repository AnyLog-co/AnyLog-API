"""
1. The following is not currently used, but may be added in the futrue
2. Should change to docker via Python
    - PyPi - https://pypi.org/project/docker/
    - GitHub: https://github.com/docker/docker-py
    - docs: https://docker-py.readthedocs.io/en/stable/client.html
"""

import docker


class DeployAnyLog:
    def __init__(self, docker_client_path:str='unix://var/run/docker.sock', exception:bool=True):
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
            self.docker_client = docker.DockerClient(docker_client_path)
        except Exception as e:
            if exception is True:
                print('Failed to set docker client against %s (Error: %s)' % (docker_client_path, e))
            exit(1)

    def __validate_container(self, name:str, exception:bool=True):
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

    def pull_image(self, password:str, build:str='predevelop', exception:bool=True)->bool:
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
            self.docker_client.login(username='oshadmon', password=password)
        except Exception as e:
            if exception is True:
                print("Failed to log into docker with password: '%s' (Error: %s)" % (password, e))
            status = False

        else:
            # pull image
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

    def deploy_anylog_container(self, node_name:str='anylog-test-node', external_ip:str=None, local_ip:str=None,
                                server_port:int=2048, rest_port:int=2049, broker_port:int=None,
                                username:str=None, password:str=None, exception:bool=True)->bool:
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
                -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
                -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
                -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
                -it --detach-keys="ctrl-d" --rm anylog:predevelop
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
            environment:dict - environment variables for docker based on arguments
        :return:
            status
        """
        status = True
        environment = {
            'NODE_TYPE': 'rest',
            'NODE_NAME': node_name,
            'ANYLOG_SERVER_PORT': server_port,
            'ANYLOG_REST_PORT': rest_port
        }

        if external_ip is not None:
            environment['EXTERNAL_IP'] = external_ip
        if local_ip is not None:
            environment['IP'] = local_ip
        if broker_port is not None:
            environment['ANYLOG_BROKER_PORT'] = broker_port
        if username is not None:
            environment['USERNAME'] = username
            environment['PASSWORD'] = 'anylog'
            if password is not None:
                environment['PASSWORD'] = password

        if not self.__validate_container(name=node_name, exception=exception):
            try:
                self.docker_client.containers.run(image='oshadmon/anylog:%s' % self.version, auto_remove=True,
                                                  network_mode='host', detach=True, stdin_open=True, tty=True,
                                                  privileged=True, name=node_name, environment=environment, volumes={
                                                      'al-%s-anylog' % node_name: {
                                                          'bind': '/app/AnyLog-Network/anylog',
                                                          'mode': 'rw'
                                                      },
                                                      'al-%s-blockchain' % node_name: {
                                                          'bind': '/app/AnyLog-Network/blockchain',
                                                          'mode': 'rw',
                                                      },
                                                      'al-%s-data' % node_name: {
                                                          'bind': '/app/AnyLog-Network/data',
                                                          'mode': 'rw',
                                                      },
                                                      'al-%s-local-scripts' % node_name: {
                                                          'bind': '/app/AnyLog-Network/local_scripts',
                                                          'mode': 'rw',
                                                      },
                                                  })
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy an AnyLog container (Error: %s)' % e)
            else:
                if not self.__validate_container(name=node_name, exception=exception):
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

        if not self.__validate_container(name='grafana', exception=exception):
            try:
                self.docker_client.containers.run(image='grafana/grafana:7.5.7', auto_remove=True, network_mode='host',
                                                  detach=False, name='grafana', port={3000:3000},
                                                  environment={
                                                      'GF_INSTALL_PLUGINS': 'simpod-json-datasource,grafana-worldmap-panel'
                                                  },
                                                  volumes={
                                                      'grafana-data': '/var/lib/grafana',
                                                      'grafana-log': '/var/log/grafana',
                                                      'grafana-config': '/etc/grafana'
                                                  })
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy Grafana container (Error: %s)' % e)
            else:
                if not self.__validate_container(name='grafana', exception=exception):
                    status = False

        return status

    def deploy_psql_container(self, username:str, password:str, exception:bool=True)->bool:
        """
        Deploy Postgres
        :sample-call:
            docker run \
               --network host \
               --name anylog-psql \
               -e POSTGRES_USER=${DB_USR} \
               -e POSTGRES_PASSWORD=${DB_PASSWD} \
               -v pgdata:/var/lib/postgresql/data \
               --rm postgres:14.0-alpine
        :args:
            username:str - psql user
            password:str psql password correlated to user
        :params:
            status:bool
        :return:
            status
        """
        status = True
        if not self.__validate_container(name='anylog-psql', exception=exception):
            try:
                self.docker_client.containers.run(image='postgres:14.0-alpine', auto_remove=True, network_mode='host',
                                                  detach=False, name='anylog-psql',
                                                  environment={'POSTGRES_USER': username, 'POSTGRES_PASSWORD': password},
                                                  volumes={'pgdata': '/var/lib/postgresql/data'})
            except Exception as e:
                status = False
                if exception is True:
                    print('Failed to deploy Postgres container (Error: %s)' % e)
            else:
                if not self.__validate_container(name='anylog-psql', exception=exception):
                    status = False

        return status


