FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install sudo && \
    apt-get -y install nano && \
    apt-get -y install curl && \
    apt-get install tar -y && \
    apt install systemctl -y 
#ajouter utilisateur necessaires

RUN sudo useradd --no-create-home --shell /bin/false prometheus
RUN sudo useradd --no-create-home --shell /bin/false node_exporter
# creer deux repertoires prometheus sous etc et var/lib

RUN sudo mkdir /etc/prometheus
RUN sudo mkdir /var/lib/prometheus

#accorder les permissions necessaires a ces dossiers à l'utilisateur prometheus
RUN sudo chown prometheus:prometheus /etc/prometheus
RUN sudo chown prometheus:prometheus /var/lib/prometheus

#telecharger le tar prometheus

RUN cd ~
RUN curl -LO https://github.com/prometheus/prometheus/releases/download/v2.24.1/prometheus-2.24.1.linux-amd64.tar.gz



# extraire le tar
RUN tar xvf prometheus-2.24.1.linux-amd64.tar.gz
# copier les fichiers binaires au repertoires necessaires

RUN sudo cp prometheus-2.24.1.linux-amd64/prometheus /usr/local/bin/
RUN sudo cp prometheus-2.24.1.linux-amd64/promtool /usr/local/bin/
#ajouter les permissions necessaires
RUN sudo chown prometheus:prometheus /usr/local/bin/prometheus
RUN sudo chown prometheus:prometheus /usr/local/bin/promtool
#copier les dossiers
RUN sudo cp -r prometheus-2.24.1.linux-amd64/consoles /etc/prometheus
RUN sudo cp -r prometheus-2.24.1.linux-amd64/console_libraries /etc/prometheus


#ajouter les permissions necessaires aux dossiers 

RUN sudo chown -R prometheus:prometheus /etc/prometheus/consoles
RUN sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
 

ENTRYPOINT ["tail", "-f", "/dev/null"]
