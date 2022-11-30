FROM ubuntu:latest

RUN apt-get update && \
      apt-get -y install nano

ENTRYPOINT ["tail", "-f", "/dev/null"]
