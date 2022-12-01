#!/usr/bin/env bash

#ajouter utilisateur necessaires

sudo useradd --no-create-home --shell /bin/false node_exporter

#telecharger le tar node_exporter

cd ~

curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.1.0/node_exporter-1.1.0.linux-amd64.tar.gz


# extraire le tar
tar xvf node_exporter-1.1.0.linux-amd64.tar.gz

# copier les fichiers binaires au repertoires necessaires

sudo cp node_exporter-1.1.0.linux-amd64/node_exporter /usr/local/bin 

#ajouter les permissions necessaires
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
#configuer prometheus

#configuer prometheus
sudo cat <<EOF > /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter 
Wants=network-online.target 
After=network-online.target
[Service] 
User=node_exporter 
Group=node_exporter 
Type=simple
ExecStart=/usr/local/bin/node_exporter
[Install]
WantedBy=multi-user.target

EOF

#Pour utiliser le service nouvellement créé, rechargez systemd.
sudo systemctl daemon-reload
#Vous pouvez maintenant démarrer Prometheus à l'aide de la commande suivante:
sudo systemctl start node_exporter
#Pour vous assurer que Prometheus est en cours d'exécution, vérifiez l'état du service.
sudo systemctl status node_exporter
sudo systemctl enable node_exporter