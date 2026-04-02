#!/bin/bash

# Create commands to execute at startup
# 1. Disable Turbo Boost (for Intel P-state driver)
# 2. apt update
# 3. Install packages

INSTALL_PACKAGES="build-essential htop cmake python3-pandas make automake libtool pkg-config libaio-dev git libmysqlclient-dev libssl-dev mysql-server zsh curl"
GIT_REPO_URL="https://github.com/hikaru2003/sysbench_binary_mysql.git"
ZSHRC_REPO_URL="https://github.com/hikaru2003/zshrc.git"
PCM_REPO=https://github.com/intel/pcm

# set -e
# Debug mode
set -x

# Redirect output to startup.log and stderr
exec > >(tee -a startup.log) 2>&1
echo "=== Startup script started ==="

# Disable Turbo Boost
echo "Disabling Turbo Boost..."
if [ -e /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
    echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
	echo "Turbo Boost disabled."
else
    echo "Intel pstate not found, skipping Turbo Boost disable."
fi

# Install Libraries
echo "Installing packages..."
DEBIAN_FRONTEND=noninteractive apt update
DEBIAN_FRONTEND=noninteractive apt install -y ${INSTALL_PACKAGES}
sudo chsh -s $(which zsh) $USER

# Clone experiment repository
echo "Cloning experiment repository..."
USER_HOME=/users/Morisaki
cd $USER_HOME
git clone ${GIT_REPO_URL}

# Clone zshrc repository
echo "Cloning zshrc repository..."
cd $USER_HOME
git clone ${ZSHRC_REPO_URL}
bash zshrc/install.sh
cp zshrc/zshrc ${USER_HOME}/.zshrc
chmod 644 ${USER_HOME}/.zshrc

# Clone PCM repository
echo "Cloning PCM repository..."
git clone --recursive ${PCM_REPO}
cd pcm/
git fetch --all --tags
git checkout
mkdir build
cd build
cmake ..
cmake --build .

# export LUA_PATH to include the sysbench_binary_mysql repository
echo "export LUA_PATH='/users/Morisaki/sysbench_binary_mysql/share/sysbench/?.lua;/users/Morisaki/sysbench_binary_mysql/share/sysbench/?/init.lua:\$LUA_PATH'" >> $USER_HOME/.zshrc

# Create MySQL user
sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS sbtest; CREATE USER 'sbuser'@'localhost' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON sbtest.* TO 'sbuser'@'localhost'; FLUSH PRIVILEGES;"
$USER_HOME/sysbench_binary_mysql/bin/sysbench --mysql-host=localhost --mysql-port=3306 --mysql-db=sbtest --mysql-user=sbuser --mysql-password=password --tables=1 --table_size=100 $USER_HOME/sysbench_binary_mysql/share/sysbench/oltp_common.lua prepare

# Change ownership of the repository to the user
USER_NAME=Morisaki
USER_GROUP=sslabko-fast-nw-
chown -R $USER_NAME:$USER_GROUP $(basename ${GIT_REPO_URL} .git)
chown -R $USER_NAME:$USER_GROUP $(basename ${ZSHRC_REPO_URL} .git)
chown -R $USER_NAME:$USER_GROUP $(basename ${PCM_REPO} .git)

echo "=== Startup script completed ==="
