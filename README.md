# misp-docker-image
This repository is intended to use with the official Hacking Lab Live CD.

Official docker images from this repository can be found on https://hub.docker.com/

## Setup your MISP instance
This is a short step by step guide on how to get your MISP instance running.  

### Clone repository
Please keep in mind that only the offical Hacking Lab Live CD is officially supported.  
Use the following commands to get the required repository from GitHub.  

```bash
cd /home/hacker/Desktop/
git clone https://github.com/Hacking-Lab/misp-docker-image.git
```

### Starting the MISP instance
Start the docker container with the following command.  

```bash
cd /home/hacker/Desktop/misp-docker-image
docker-compose up
```

Connect to MISP by opening your preferred web browser and open the url [http://localhost:80](http://localhost/).  

The MISP instance initializes all labs. Please wait until you are able to see the Hacking-Lab icon.

---

Then login with the following credentials.  
User: `investigator@misp-labX.com`  
Password: `compass`  


