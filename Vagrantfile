#  -*-  mode:  ruby -*-
# vi: set ft=ruby  :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION)  do  |config|
  # General Vagrant VM   configuration.
  config.vm.box  =  "centos/7"
  config.ssh.insert_key  =  false
  config.vm.synced_folder  ".",  "/vagrant"
  config.vm.provider  :virtualbox  do  |v|
    v.memory  =  1024
    v.linked_clone  =  true
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false  
  end
  end

  #  Swarm Control Master
  config.vm.define  "master"  do  |app|
    app.vm.hostname  =  "master"
    app.vm.network  :public_network,  ip:  "192.168.60.10",  auto_config: false
	app.vm.provision "shell", path: "boostrap_prometheus.sh"
	app.vm.network "forwarded_port", guest: 9090, host: 9090 
  end

  #  Swarm node 1.
  config.vm.define  "node1"  do  |app|
    app.vm.hostname  =  "node1"
	app.vm.provision "shell", path: "boostrap_node_exporter.sh"
    app.vm.network  :private_network,  ip:  "192.168.60.20"
	app.vm.network "forwarded_port", guest: 9100, host: 9100 
  end

  #  Swarm node 2.
  config.vm.define  "node2"  do  |app|
    app.vm.hostname  =  "node2"
	app.vm.provision "shell", path: "boostrap_node_exporter.sh"
    app.vm.network  :private_network,  ip:  "192.168.60.30"
	app.vm.network "forwarded_port", guest: 9100, host: 9100 
  end

end
