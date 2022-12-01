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

sudo cp /prometheus/prometheus.yml /etc/prometheus/