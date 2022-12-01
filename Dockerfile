FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install sudo && \
    apt-get -y install nano && \
    apt-get -y install curl && \
    apt-get install tar -y && \
    apt install systemctl -y 

COPY boostrap_node_exporter.sh boostrap_node_exporter.sh /home/


ENTRYPOINT ["tail", "-f", "/dev/null"]
