
#verifier l'os installé sur ta machine
cat /etc/*release*
#  ajouter les utilisateurs prometheus et node_exporter

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


#copier la configuration suivante dans le fichier config /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s

# A scrape configuration containing exactly one endpoint to scrape.
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']



sudo nano /etc/prometheus/prometheus.yml

##Étape 4 - Exécution de Prometheus
##Démarrez Prometheus en tant qu'utilisateur prometheus , en fournissant le chemin d'accès au fichier de configuration et au répertoire de données.

sudo -u prometheus /usr/local/bin/prometheus \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries



#creer un Fichier de service Prometheus 
sudo nano  /etc/systemd/system/prometheus.service
#copier 
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



#Enfin, enregistrez le fichier et fermez votre éditeur de texte.
#Pour utiliser le service nouvellement créé, rechargez systemd.
sudo systemctl daemon-reload
#Vous pouvez maintenant démarrer Prometheus à l'aide de la commande suivante:
sudo systemctl start prometheus
#Pour vous assurer que Prometheus est en cours d'exécution, vérifiez l'état du service.
sudo systemctl status prometheus