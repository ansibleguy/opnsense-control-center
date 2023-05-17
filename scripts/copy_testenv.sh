#!/bin/bash

set -eo pipefail

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]
then
  echo 'USAGE:'
  echo ' 1 > SSH Target (user@server)'
  echo ' 2 > SSH Port'
  echo ' 3 > SCP Target directory'
#  echo ' 4 > Domain'
  exit 1
fi

SSH_TGT="$1"
SSH_PORT="$2"
SCP_TGT="$3"
# DOM="$4"

set -u

cd "$(dirname "$0")"
scp -P "$SSH_PORT" -r "$(pwd)/../playbook/" "$SSH_TGT:$SCP_TGT"

# replace config
ssh -p "$SSH_PORT" "$SSH_TGT" "sed -i 's/        ssh: 22/        ssh: $SSH_PORT/g' $SCP_TGT/playbook/setup.yml"
# ssh -p "$SSH_PORT" "$SSH_TGT" "sed -i 's/      domain:/      domain: $DOM/g' $SCP_TGT/playbook/setup.yml"
