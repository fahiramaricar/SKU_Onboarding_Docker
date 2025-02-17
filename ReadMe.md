# Streamlit app Docker Image

## 1. Login with your AWS console and launch an EC2 instance
## 2. Run the following commands

Note: Do the port mapping to this port:- 8501

```bash
sudo apt-get update -y

sudo apt-get upgrade

#Install Docker

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker
```

```bash
git clone https://github.com/fahiramaricar/SKU_Onboarding_Docker.git
```
```
docker login -u fahimaricar
```

```bash
docker build -t fahimaricar/skuapp:latest . 
```

```bash
docker images -a  
```

```bash
docker run -d -p 8501:8501 fahimaricar/skuapp 
```





Additional Debugging:




```bash
docker ps  
```

```bash
docker stop container_id
```

```bash
docker rm $(docker ps -a -q)
```

```bash
docker login 
```

```bash
docker push fahimaricar/skuapp:latest 
```

```bash
docker rmi fahimaricar/skuapp:latest
```

```bash
docker pull fahimaricar/skuapp
```
## 3. Alternatively create docker image locally, push to dockerhub and then launch EC2  instance 
Run the following command in windows WSL to push the local docker image to dockerhub
```bash
sudo apt-get update -y

sudo apt-get upgrade

#Install Docker

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker fahira (Ubuntu username)

newgrp docker
```
Then continue the same procedure as other approach
To troubleshoot docker image built issue:

```bash
sudo service docker status

```
```bash
docker push fahimaricar/skuapp:latest 
```
To pull the image in the instance, connect the instance and run the following commands

```bash
#Install Docker

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker
```
```bash
docker login -u fahimaricar
```
```bash
docker pull fahimaricar/skuapp
```
```bash
docker run -d -p 8501:8501 fahimaricar/skuapp 
```



