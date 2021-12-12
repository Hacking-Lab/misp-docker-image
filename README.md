# misp-docker-image
This repository is intended to use with the official Hacking Lab Live CD.

Official docker images from this repository can be found on https://hub.docker.com/r/hackinglab/misp

## Setup your MISP instance
This is a short step by step guide on how to get your MISP instance running.  

### Clone repository
Please keep in mind that only the offical Hacking Lab Live CD is officially supported.  
Use the following commands to get the required repository from GitHub.  

```bash
cd /home/hacker/
git clone https://github.com/Hacking-Lab/misp-docker-image.git
```

### Starting the MISP instance
Start the docker container with the following command.  

```bash
cd /home/hacker/misp-docker-image
docker-compose up
```

After a few minutes four instances of MISP should be available. The hostnames are:  
http://misp.localhost  
http://instance-a.misp.localhost  
http://instance-b.misp.localhost  
http://instance-e.misp.localhost  

These four instances have different purposes and will be used for different labs.  
Please wait until you are able to see the Hacking-Lab icon.

---

The admin user is present on all instances.
User: `admin@misp-lab.com`  
Password: `compass`  

The compass for all other users is also `compass`.
For example:
User: `investigator@misp-labX.com`  
Password: `compass`  


_The **X** in the email address has to be replaced with the lab number (for example **1**)_.


