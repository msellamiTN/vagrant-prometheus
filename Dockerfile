FROM ubuntu:latest

RUN apt-get update && \
      apt-get -y install nano
      && \
      apt-get -y install sudo

ENTRYPOINT ["tail", "-f", "/dev/null"]
