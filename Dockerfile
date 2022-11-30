FROM ubuntu:latest

RUN apt-get update && \
      apt-get -y install nano

CMD ["/bin/bash"]
