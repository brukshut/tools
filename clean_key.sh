#!/bin/bash

##
## clean_key.sh [hostname]
## safely update stale ssh keys in your known_hosts
##
PATH=/bin:/sbin:/usr/bin:/usr/sbin

## functions
function die { echo "$*" 1>&2 && exit 1; }

function remove_key {
  local host=$1
  local known_hosts=$2
  [[ $(ssh-keygen -F $host) ]] &&
    ( printf "Removing %s\n" $host
      ssh-keygen -q -f $known_hosts -R $host &>/dev/null )
}
 
function scrub_known_hosts {
  local host=${1%%.*}
  local domain=${1##${host}.}
  local known_hosts=$2
  ## remove hostname or fqdn, but not both
  [[ -z $domain ]] && remove_key $1 $known_hosts ||
    remove_key $1 $known_hosts
  ## remove PTR if found
  local ipaddr=$(host $1 | awk {'print $4'})
  [[ -z $ipaddr ]] && remove_key $ipaddr
}  

function add_key {
  ## re-add changed key
  local host=$1
  ssh -q -oStrictHostKeyChecking=no $host "exit"
}

## end functions

## main

## require hostname
usage="usage: $0 [hostname]"
[[ $# == 1 ]] || { echo $usage; exit 1; }

## scrub hostname from known_hosts
known_hosts=${HOME}/.ssh/known_hosts

[[ ! -e $known_hosts ]] && die "known_hosts not found" ||
  ( scrub_known_hosts $1 $known_hosts
    add_key $1 )

## end main
