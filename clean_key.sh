#!/bin/bash

##
## peacefully update offending key from .ssh/known_hosts
## if ip address has changed, re-add new key quietly
##
PATH=/bin:/sbin:/usr/bin:/usr/sbin

function remove_key {
  KNOWN_HOSTS=${HOME}/.ssh/known_hosts
  local HOST=$1
  if [[ $(ssh-keygen -F $HOST) ]]; then
    printf "Removing %s\n" $HOST
    ssh-keygen -q -f $KNOWN_HOSTS -R $HOST &>/dev/null
  fi  
}
 
function scrub_known_hosts {
  local HOST=${1%%.*} && local DOMAIN=${1##${HOST}.}
  if [ -e $KNOWN_HOSTS ]; then 
    if [ -z $DOMAIN ]; then
      remove_key $HOST 
    else
      remove_key $1
      IP=$(host $1 | awk {'print $4'})
      [ -z $IP ] && remove_key $IP
    fi
  fi
}  

function add_key {
  ## re-add changed key
  ssh -q -oStrictHostKeyChecking=no $1 "exit"
}

## usage
USAGE="Usage: $0 [hostname]"
[ $# == 1 ] || { echo $USAGE; exit 1; }

## scrub hostname from known_hosts
scrub_known_hosts $1
add_key $1
