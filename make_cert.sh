#!/bin/bash

##
## make_cert.sh
## simple shell script to generate self signed SSL certificate
##

## functions
## create secuire and 
function generate_key {
  local cn=$1
  openssl genrsa -out ${cn}.secure.key 4096
  ## decrypt secure key to create public key
  openssl rsa -in ${cn}.secure.key -out ${cn}.key
}

## generate csr
function generate_csr {
  local cn=$1
  openssl req -new -key ${cn}.secure.key -out ${cn}.csr
}

## generate crt
function generate_crt {
  local cn=$1
  openssl x509 -req -days 365 -in ${cn}.csr -signkey ${cn}.key -out ${cn}.crt
}

function usage() {
  echo "Usage: $0 -c [commonname]" && exit 1
}
## end functions

## main
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

while getopts ":c:" opt; do
  case $opt in
    c) COMMONNAME=${OPTARG}
      ;;
    *) usage
      ;;
  esac
done

## require common name
[[ -z $COMMONNAME ]] && usage ||
  ( [[ -d $COMMONNAME ]] || mkdir ${COMMONNAME}
    cd $COMMONNAME
    generate_key $COMMONNAME
    generate_csr $COMMONNAME
		generate_crt $COMMONNAME )

## end main
