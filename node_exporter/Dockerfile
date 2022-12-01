FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install sudo && \
    apt-get -y install nano && \
    apt-get -y install curl && \
    apt-get install tar -y && \
    apt install systemctl -y 

#!/usr/bin/env bash

#ajouter utilisateur necessaires

RUN sudo useradd --no-create-home --shell /bin/false node_exporter

#telecharger le tar node_exporter

RUN cd ~

RUN curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.1.0/node_exporter-1.1.0.linux-amd64.tar.gz


# extraire le tar
RUN tar xvf node_exporter-1.1.0.linux-amd64.tar.gz

# copier les fichiers binaires au repertoires necessaires

RUN sudo cp node_exporter-1.1.0.linux-amd64/node_exporter /usr/local/bin 

#ajouter les permissions necessaires
RUN sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
 

 

ENTRYPOINT ["tail", "-f", "/dev/null"]
