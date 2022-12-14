#!/usr/bin/env bash

#ajouter utilisateur necessaires

sudo useradd --no-create-home --shell /bin/false prometheus
sudo useradd --no-create-home --shell /bin/false node_exporter
# creer deux repertoires prometheus sous etc et var/lib

sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

#accorder les permissions necessaires a ces dossiers à l'utilisateur prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

#telecharger le tar prometheus

cd ~
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.24.1/prometheus-2.24.1.linux-amd64.tar.gz



# extraire le tar
tar xvf prometheus-2.24.1.linux-amd64.tar.gz
# copier les fichiers binaires au repertoires necessaires

sudo cp prometheus-2.24.1.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.24.1.linux-amd64/promtool /usr/local/bin/
#ajouter les permissions necessaires
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
#copier les dossiers
sudo cp -r prometheus-2.24.1.linux-amd64/consoles /etc/prometheus
sudo cp -r prometheus-2.24.1.linux-amd64/console_libraries /etc/prometheus


#ajouter les permissions necessaires aux dossiers 

sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
#configuer prometheus
sudo cat <<EOF > /etc/prometheus/prometheus.yml
global:
  scrape_interval:     15s # By default, scrape targets every 15 seconds.
  # Attach these labels to any time series or alerts when communicating with
  # external systems (federation, remote storage, Alertmanager).
  external_labels:
    monitor: 'codelab-monitor'
# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']
  - job_name: node
    static_configs:
    - targets:
       - 192.168.60.20:9100
       - 192.168.60.30:9100

EOF


#configuer prometheus
sudo cat <<EOF > /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target
[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries


EOF

#Pour utiliser le service nouvellement créé, rechargez systemd.
sudo systemctl daemon-reload
#Vous pouvez maintenant démarrer Prometheus à l'aide de la commande suivante:
sudo systemctl start prometheus
#Pour vous assurer que Prometheus est en cours d'exécution, vérifiez l'état du service.
sudo systemctl status prometheus
sudo systemctl enable prometheus