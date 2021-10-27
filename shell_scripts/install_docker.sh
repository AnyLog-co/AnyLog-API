#!/bin/bash
# Install Docker deployment tool for Debian-based OS. For other version please use: https://docs.docker.com/engine/install/

for CMD in update upgrade update ; do sudo apt-get -y install ${CMD} ; done

# Allow apt over HTTP
sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release

# Official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg


# download .deb package based on CPU type
TYPE=`uname -a`
if [[ ${TYPE} == "x86_64" ]] || [[ ${TYPE} == "amd64" ]]
then
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
elif [[ ${TYPE} == "arm64" ]]
then
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
else
    echo "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
fi

# Install docker
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

# Permissions
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# validate docker works
docker ps -a