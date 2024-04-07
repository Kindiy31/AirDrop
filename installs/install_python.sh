#!/bin/bash

sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
tar -xf Python-3.12.1.tgz
cd Python-3.12.1
./configure --enable-optimizations
make
sudo make altinstall
cd /home
python3.12 -m pip install --upgrade pip
pip install virtualenv