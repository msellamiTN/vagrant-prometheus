FROM ubuntu:latest

RUN apt-get update && \
      apt-get -y install sudo
      && \
      apt-get -y install nano
      && \
      apt-get -y install curl
       && \
      apt-get install tar -y
       && \
       sudo apt install systemctl -y


ENTRYPOINT ["tail", "-f", "/dev/null"]
