"""
1. The following is not currently used, but may be added in the futrue
2. Should change to docker via Python
    - PyPi - https://pypi.org/project/docker/
    - GitHub: https://github.com/docker/docker-py
"""

import docker
import os

class DeployAnyLog:
    def __init__(self, password:str, version:str='predevelop',
                 docker_client_path:str='unix://var/run/docker.sock', exception:bool=True):
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
        else:
            self.password = password
            self.version = version

    def check_image(self, exception:bool=True)->bool:
        """
        Based on build type, check if image exists
        :params:
            status:bool
            img_list:list - list of images
        :return:
            if `'oshadmon/anylog:%s' % version` exists return True, if not Falses
        """
        status = False
        try:
            img_list = self.docker_client.images.list()
        except Exception  as e:
            if exception is True:
                print('Failed to pull list of images (Error: %s)' % e)
        else:
            for img in img_list:
                try:
                    if 'oshadmon/anylog:%s' % self.version in str(img):
                        status = True
                except:
                    pass

        return status

    def pull_image(self, exception:bool=True)->bool:
        """
        Pull image oshadmon/anylog
        :args:
            passwd:str - login docker password
            version:str - version to build
        :params:
            status:bool
        :return:
            if fails return False, else True
        """
        # login into docker
        status = True
        try:
            self.docker_client.login(username='oshadmon', password=self.password)
        except Exception as e:
            if exception is True:
                print('Failed to log into docker with password: %s (Error: %s)' % (self.password, e))
            status = False

        else:
            # pull image
            try:
                self.docker_client.images.pull(repository='oshadmon/anylog:%s' % self.version)
            except Exception as e:
                if exception is True:
                    print('Failed to pull image oshadmon/anylog:%s (Error: %s)' % (self.version, e))
                status = False
            else:
                if not self.check_image(exception=exception):
                    if exception is True:
                        print('Failed to pull image oshadmon/anylog:%s for an unknown reason...' % self.version)
                    status = False

        return status

    def deploy_anylog_container(self, node_name:str='anylog-test-node', server_port:int=2048, rest_port:int=2049,
                                external_ip:str=None, local_ip:str=None, broker_port:int=None, exception:bool=True):
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
        :params:
            environment:dict - environment variables for docker based on arguments
        """

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

        self.docker_client.containers.run(image='oshadmon/anylog:%s' % self.version, auto_remove=True,
                                          network_mode='host', detach=False, name=node_name,
                                          environment=environment,
                                          volumes={
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


if __name__ == '__main__':
    da = DeployAnyLog(password='docker4AnyLog!')
    img_status = da.check_image()
    if img_status is False:
        img_status = da.pull_image()

    if img_status is True:
        da.deploy_anylog_container()



