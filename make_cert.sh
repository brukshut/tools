#!/bin/bash

##
## make_cert.sh
## simple shell script to generate self signed SSL certificate
##
USAGE="Usage: $0 [server.common.name]"

if [ $# == 0 ]; then
  echo ${USAGE}
  exit 1
fi

COMMONNAME=$1
PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
export PATH

#openssl genrsa -des3 -passout pass:x -out ${COMMONNAME}.secure.key 2048
#openssl rsa -passin pass:x -in server.pass.key -out server.key

## create secure key
openssl genrsa -des3 -out ${COMMONNAME}.secure.key 2048
## decrypt secure key to create public key
openssl rsa -in ${COMMONNAME}.secure.key -out ${COMMONNAME}.key  

## generate csr
openssl req -new -key ${COMMONNAME}.secure.key -out ${COMMONNAME}.csr

## generate crt
openssl x509 -req -days 365 -in ${COMMONNAME}.csr -signkey ${COMMONNAME}.key -out ${COMMONNAME}.crt
