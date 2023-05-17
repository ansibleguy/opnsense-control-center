#!/bin/bash

set -euo pipefail

# NOTE: run this script on the target server!

PLAY_DIR="$(dirname "$0")/playbook"
BRANCH='dev'

apt -y install python3-pip
python3 -m pip install ansible

if ! [ -d "$PLAY_DIR" ]
then
  apt install wget
  wget "https://github.com/ansibleguy/opnsense-control-center/archive/refs/heads/${BRANCH}.zip" -O /tmp/repo_opncc.zip
  unzip /tmp/repo_opncc.zip -d /tmp/repo_opncc/
  PLAY_DIR="/tmp/repo_opncc/opnsense-control-center-${BRANCH}/playbook"
fi

cd "$PLAY_DIR"

export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export ANSIBLE_INVENTORY_UNPARSED_WARNING=False
export ANSIBLE_LOCALHOST_WARNING=False

ansible-galaxy role install -r requirements.yml -p ./roles/
ansible-galaxy collection install -r requirements.yml -p ./collecions/

ansible-playbook setup.yml
