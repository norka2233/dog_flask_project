Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network :forwarded_port, guest: 8000, host: 5000
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end
end