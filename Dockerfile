FROM ubuntu:latest

RUN apt-get update && \
      apt-get -y install sudo

USER root
CMD /bin/bash
