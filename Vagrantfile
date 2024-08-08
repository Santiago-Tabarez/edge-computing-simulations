# Vagrantfile

Vagrant.configure("2") do |config|
  # Select the Vagrant box, Ubuntu 22.04 LTS (Jammy Jellyfish)
  config.vm.box = "ubuntu/jammy64"

  # Network configuration
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # VM basic config
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end

  # Sync the project directory
  config.vm.synced_folder ".", "/home/vagrant/project", type: "virtualbox"

  # Provision to install Python, MySQL, and dependencies
  config.vm.provision "shell", inline: <<-SHELL
    set -e  # Exit if any command fails

    # Update the system
    sudo apt-get update

    # Install the necessary dependencies in one call
    sudo apt-get install -y \
      software-properties-common \
      build-essential \
      zlib1g-dev \
      libssl-dev \
      libffi-dev \
      curl \
      libbz2-dev \
      libsqlite3-dev \
      liblzma-dev \
      mysql-server \
      libmysqlclient-dev \
      pkg-config

    # Download and install Python 3.12.1 from source if not installed
    if ! command -v python3.12; then
      curl -O https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
      tar -xf Python-3.12.1.tgz
      cd Python-3.12.1
      ./configure --enable-optimizations
      make -j $(nproc)
      sudo make altinstall
      cd ..
      rm -rf Python-3.12.1
      rm Python-3.12.1.tgz
    fi

    # Install pip for Python 3.12 if not installed
    if ! command -v pip3.12; then
      curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
    fi

    # Start and enable the MySQL service
    sudo systemctl start mysql
    sudo systemctl enable mysql

    # Create MySQL database and user
    sudo mysql -e "CREATE DATABASE edge_computing;"
    sudo mysql -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'admin';"
    sudo mysql -e "GRANT ALL PRIVILEGES ON edge_computing.* TO 'admin'@'%';"
    sudo mysql -e "FLUSH PRIVILEGES;"

    # Create a virtual environment for the project using Python 3.12.1 if it does not exist
    if [ ! -d /home/vagrant/env ]; then
      python3.12 -m venv /home/vagrant/env
    fi

    # Activate the virtual environment and install dependencies
    source /home/vagrant/env/bin/activate
    pip install --upgrade pip
    pip install -r /home/vagrant/edge-computing-simulation/requirements.txt

    # Deactivate the virtual environment
    deactivate
    echo "export PYTHONPATH=/home/vagrant/edge-computing-simulation" >> /home/vagrant/.bashrc
  SHELL

  # Enable cache if the plugin is installed
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end
end
