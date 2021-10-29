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

    def docker_login(self, password:str, exception:bool=False)->bool:
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

    # Image support functions - update, validate, remove
    def update_image(self, image_name:str, exception:bool=True)->docker.models.images.Image:
        """
        Pull image oshadmon/anylog
        :args:
            image_name:str image with build

        :params:
            status:bool
        :return:
            if fails return False, else True
        """
        try:
            image = self.docker_client.images.pull(repository=image_name)
        except Exception as e:
            image = None
            if exception is True:
                print('Failed to pull image %s (Error: %s)' % (image_name, e))
        else:
            image = self.validate_image(image_name=image_name)
            if image is None and exception is True:
                print('Failed to pull image for an unknown reason...' % image_name)

        return image

    def validate_image(self, image_name:str)->docker.models.images.Image:
        """
        Check if Image exists
        :args:
            image_name:str - image name (with build)
        :params:
            image
        :return:
            return image object, if fails return None
        """
        try:
            image = self.docker_client.images.get(name=image_name)
        except Exception as e:
            image = None

        return image

    def remove_image(self, image_name:str, exception:bool=True)->bool:
        """
        Remove image from docker
        :args:
            image_name:str - image name with version
            exception:bool - whether or not to print exceptions
        :params:
            image_obj:docker.models.images.Image - Image object
            status:bool
        :return:
            status
        """
        status = True

        try:
            self.docker_client.images.remove(image=image_name)
        except Exception as e:
            status = False
            if exception is True:
                print('Failed to remove image %s (Error: %s)' % (image_name, e))
        else:
            if validate_image(image_name=image_name) is not None:
                status = False
                if exception is True:
                    print('Failed to remove image: %s' % image_name)


        return status

    # Volume support functions - create, validate, remove
    def create_volume(self, volume_name:str, exception:bool=True)->docker.models.containers.Container:
        """
        Create volume (if not exists)
        :args:
            volume_name:str - volume name
            exception:bool - whether to print exception
        :params:
            volume:docker.models.containers.Container - volume object
        :return:
            volume
        """
        try:
            volume = self.docker_client.volumes.create(name=volume_name, driver='local')
        except Exception as e:
            volume = None
            if exception is True:
                print('Failed to create volume %s (Error: %s)' % (volume_name, e))
        else:
            volume = self.validate_volume(volume_name=volume_name)
            if volume is None and exception is True:
                print('Failed to create volume for %s' % volume_name)

        return volume

    def validate_volume(self, volume_name:str)->docker.models.containers.Container:
        """
        Validate if volume exists
        :args:
            volume_name:str - volume name
        :params:
            volume:docker.models.volumes.Volume - volume object
        :return:
            volume if fails return None
        """
        try:
            volume = self.docker_client.volumes.get(volume_id=volume_name)
        except Exception as e:
            volume = None

        return volume

    def remove_volume(self, volume:docker.models.volumes.Volume, exception:bool=True)->bool:
        """
        Remove volume
        :args:
            volume:docker.models.volumes.Volume - volume object
            exception:bool - whether to print exception
        :params:
            status:bool - whether to print exceptions
        :return:
            status
        """
        status = True

        try:
            volume.remove()
        except Exception as e:
            status = False
            if exception is True:
                print('Failed to remove volume for container %s (Error: %s)' % (container.name, e))
        else:
            if self.validate_volume(volume_name=volume) is not None:
                status = False
                if exception is True:
                    print('Failed to remove volume for container %s' % container.name)

        return status


    # Container support functions - run, validate, stop
    def run_container(self, image:str, container_name:str, environment:dict={}, volumes:dict={},
                      exception:bool=False)->docker.models.containers.Container:
        """
        Deploy docker container based on params
        :docker-call:
            docker run --name ${CONTAINER_NAME}
                -e ${ENV_KEY}=${ENV_VALUE}
                ...
                -v ${VOLUME_KEY}:${DIRECTORY_PATH}
                ...
                --host network --rm ${IMAGE}
        :args:
            image:str - image name with build
            container_name:str - container name
            environment:dict - environment params
            volumes:dict - volume params
            exception:bool - whether or not to print exceptions
        :params:
            container:docker.models.containers.Container - docker container object
        :return:
            status
        """
        try:
            container = self.docker_client.containers.run(image=image, auto_remove=True, network_mode='host', detach=True,
                                              stdin_open=True, tty=True, privileged=True, name=container_name,
                                              environment=environment, volumes=volumes)
        except Exception as e:
            container = None
            if exception is True:
                print('Failed to deploy docker container %s against image %s (Error: %s)' % (container_name, image, e))
        else:
            container = self.validate_volume(container_name=container_name)
            if container is None and exception is True:
                print('Failed to validate docker container %s' % container_name)

        return container

    def validate_container(self, container_name:str)->docker.models.containers.Container:
        """
        Validate container was deployed
        :args:
            container_name:str - container name
            exception:bool - whether to print exception
        :params:
            container:docker.models.containers.Container - container object
        :return:
            container object, else None
        """
        try:
            container = self.docker_client.containers.get(container_id=container_name)
        except Exception as e:
            container = None

        return container

    def stop_container(self, container:docker.models.containers.Container, exception:bool=False)->bool:
        """
        Stop container based on name
        :args:
            container:docker.models.containers.Container - container object
            exception:bool - whether to print exception
        :params:
            status:bool
        :return:
            status
        """
        status = True

        try:
            container.stop()
        except Exception as e:
            status = False
            if exception is True:
                print('Failed to remove container %s (Error: %s)' % (container.name, e))
        else:
            if self.validate_container(container_name=container.name) is not None:
                status = False
                if exception is True:
                    print('Failed to remove container %s' % container.name)

        return status

    # Deploy containers
    def deploy_anylog_container(self, docker_password:str, update_image:bool=False, container_name:str='anylog-test-node',
                                build:str='predevelop', external_ip:str=None, local_ip:str=None,
                                server_port:int=2048, rest_port:int=2049, broker_port:int=None,
                                authentication:str='off', auth_type:str='admin', username:str='anylog',
                                password:str='demo', expiration:str=None, exception:bool=True)->bool:
        """
        Deploy an AnyLog of type rest
        :args:
            docker_password:str - docker password to download AnyLog container
            update_image:bool - whether to update the image (if exists)
            container_name:str - name of the container
            build:str - version of AnyLog image to download
            server_port:int - TCP server port
            rest_port:int - REST server port
            authentication:str - whether to enable authentication
            exception:bool - whether or not to print exceptions
            # Optional configs
            external_ip:str - IP address that's different than the default external IP
            local_ip:str - IPs address that's different  than the default loccal IP
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
        if external_ip is not None:
            environment['EXTERNAL_IP'] = external_ip
        if local_ip is not None:
            environment['IP'] = local_ip
        if broker_port is not None:
            environment['ANYLOG_BROKER_PORT'] = broker_port

        volume_paths = {
            '%s-anylog' % container_name: '/app/AnyLog-Network/anylog',
            '%s-blockchain' % container_name: '/app/AnyLog-Network/blockchain',
            '%s-data' % container_name: '/app/AnyLog-Network/data',
            '%s-local-scripts' % container_name: '/app/AnyLog-Network/local_scripts'
        }
        volumes = {}

        # Prepare volumes
        for volume in volume_paths:
            if self.validate_volume(volume_name=volume) is None:
                if self.create_volume(volume_name=volume, exception=exception) is not None:
                    volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}
            else:
                volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}

        # login
        if update_image is True or self.validate_image(image_name='oshadmon/anylog:%s' % build) is None:
            status = self.docker_login(password=docker_password, exception=exception)

        # Update image
        if status is True and update_image is True:
            status = self.update_image(build='oshadmon/anylog:%s' % build, exception=exception)

        # deploy AnyLcg container
        if status is True:
            if self.validate_container(container_name=container_name) is None:
                if not self.run_container(image='oshadmon/anylog:%s' % build, container_name=container_name,
                                          environment=environment, volumes=volumes, exception=exception):
                    status = False

        return status

    def deploy_grafana_container(self, exception:bool=True)->bool:
        """
        Deploy a Grafana v 7.5.7 as a docker container
        :args:
            exception:bool - whether to print exceptions or not
        :params:
            status:bool
        :return:
            status
        """
        status = True

        environment = {
            'GF_INSTALL_PLUGINS': 'simpod-json-datasource,grafana-worldmap-panel'
        }
        volume_paths = {
            'grafana-data': '/var/lib/grafana',
            'grafana-log': '/var/log/grafana',
            'grafana-config': '/etc/grafana'
        }

        for volume in volume_paths:
            if self.validate_volume(volume_name=volume) is None:
                if self.create_volume(volume_name=volume, exception=exception) is not None:
                    volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}
            else:
                volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}

        if self.validate_container(container_name='grafana') is None:
            if not self.run_container(image='grafana/grafana:7.5.7', container_name='grafana', environment=environment,
                                      volumes=volumes, exception=exception):
                status = False

        return status

    def deploy_psql_container(self, conn_info:str, exception:bool=True)->bool:
        """
        Deploy Postgres
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

        environment = {
            'POSTGRES_USER': conn_info.split('@')[0],
            'POSTGRES_PASSWORD': conn_info.split(':')[-1]
        }

        volume_paths = {'pgdata': '/var/lib/postgresql/data'}

        for volume in volume_paths:
            if self.validate_volume(volume_name=volume) is None:
                if self.create_volume(volume_name=volume, exception=exception) is not None:
                    volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}
            else:
                volumes[volume] = {'bind': volume_paths[volume_name], 'mode': 'rw'}

        if self.validate_container(container_name='postgres-db') is None:
            if not self.run_container(image='postgres:14.0-alpine', container_name='postgres-db',
                                      environment=environment, volumes=volumes, exception=exception):
                status = False

        return status

    def stop_anylog_container(self, container_name:str, remove_volume:bool=False, remove_image:bool=False,
                              build:str='predevelop', exception:bool=False)->bool:
        """
        Stop & clean AnyLog container
        :args:
            container_name:str - container name
            remove_volume:bool - whether to remove correlated volume
            remove_image:bool - whether to remove correleated image
            build:str - AnyLog version to remove
            exception:bool - whether to print exceptions
        :params:
            status:bool
        :return:
            status
        """
        status = True

        if self.validate_container(container_name=container_name) is not None:
            status = self.stop_container(container=container_name)

        if status is True:
            if remove_volume is True:
                volume_status = []
                for volume_name in ['%s-anylog' % container_name, '%s-blockchain' % container_name,
                                    '%s-data' % container_name, '%s-local-scripts' % container_name]:
                    volume = self.validate_volume(volume_name=volume_name)
                    if volume is not None:
                        volume_status.append(self.remove_volume(volume=volume, exception=exception))
                if False in volume_status:
                  status = False
            if remove_image is True:
                image = self.validate_image(image_name='oshadmon/anylog:%s' % build)
                if image is not None and self.remove_image(image_name='oshadmon/anylog:%s' % build,
                                                           exception=exception) is False:
                    status = False
        return status

    def stop_grafana_container(self, remove_volume:bool=False, remove_image:bool=False, exception:bool=False)->bool:
        """
        Stop & clean Grafana container
        :args:
            remove_volume:bool - whether to remove Grafana related volumes
            remove_image:bool - whether to removee Grafana imae
            exception:bool - whethher to print exceptions
        :params:
            status:bool
            container_name:str - name of the Grafana container
        :return:
            status
        """
        status = True
        container_name = 'grafana'

        if self.validate_container(container_name=container_name) is not None:
            status = self.stop_container(container=container_name)

        if status is True:
            if remove_volume is True:
                volume_status = []
                for volume_name in ['grafana-data', 'grafana-log', 'grafana-config']:
                    volume = self.validate_volume(volume_name=volume_name)
                    if volume is not None:
                        volume_status.append(self.remove_volume(volume=volume, exception=exception))
                if False in volume_status:
                  status = False
            if remove_image is True:
                image = self.validate_image(image_name='grafana/grafana:7.5.7' % build)
                if image is not None and self.remove_image(image_name='grafana/grafana:7.5.7',
                                                           exception=exception) is False:
                    status = False
        return status


    def stop_postgres_container(self, remove_volume:bool=False, remove_image:bool=False, exception:bool=False)->bool:
        """
        Stop & clean Grafana container
        :args:
            remove_volume:bool - whether to remove Grafana related volumes
            remove_image:bool - whether to removee Grafana imae
            exception:bool - whethher to print exceptions
        :params:
            status:bool
            container_name:str - name of the Grafana container
        :return:
            status
        """
        status = True
        container_name = 'postgres-db'

        if self.validate_container(container_name=container_name) is not None:
            status = self.stop_container(container=container_name)

        if status is True:
            if remove_volume is True:
                volume_status = []
                for volume_name in ['pgdata']:
                    volume = self.validate_volume(volume_name=volume_name)
                    if volume is not None:
                        volume_status.append(self.remove_volume(volume=volume, exception=exception))
                if False in volume_status:
                  status = False
            if remove_image is True:
                image = self.validate_image(image_name='grafana/grafana:7.5.7' % build)
                if image is not None and self.remove_image(image_name='grafana/grafana:7.5.7',
                                                           exception=exception) is False:
                    status = False
        return status







if __name__ == '__main__':
    da = DeployAnyLog()
    da.validate_image(image_name='postgres:14.0-alpine')