#!/bin/bash

## 
## simple packer wrapper to automatically fetch aws vpc and subnet ids
## sets AWS_VPC_ID and AWS_SUBNET_ID, referenced inside packer json
## requires awscli and jq
##

## functions
function fetch_vpc {
  local vpc_id=$(aws ec2 describe-vpcs | jq -r .Vpcs[0].VpcId)
  printf "%s\n" $vpc_id
}

function fetch_subnet {
  local subnet_cidr=$1
  local subnet_count=$(aws ec2 describe-subnets | jq '.Subnets | length')
  ## loop through subnets 
  for (( c=0; c<=${subnet_count}; c++ )); do
    local cidr_block=$(aws ec2 describe-subnets | jq -r .Subnets[${c}].CidrBlock)
    [[ "${cidr_block}" == "${subnet_cidr}" ]] &&
      local aws_subnet_id=$(aws ec2 describe-subnets | jq -r .Subnets[${c}].SubnetId)
    ## if we find our subnet id, break out of loop
    [[ -z ${aws_subnet_id} ]] || printf "%s\n" $aws_subnet_id && break 
  done
}

function usage() {
  echo "Usage: $0 -f [file] -s [subnet_cidr] -v [vpc]" && exit 1
}
## end functions

## main
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

while getopts ":f:s:v:" opt; do
  case $opt in
    f) FILE=${OPTARG}
      ;;
    s) SUBNET=${OPTARG}
      ;;
    v) VPC=${OPTARG}
      ;;
    *) usage
      ;;
  esac
done

## require file (packer json)
[[ -z $FILE ]] && usage ||
  [[ -e $FILE ]] && 
    ( [[ $VPC ]] || AWS_VPC_ID=$(fetch_vpc)
      [[ $SUBNET ]] || SUBNET=10.0.0.0/24
      AWS_SUBNET_ID=$(fetch_subnet $SUBNET)
      export AWS_VPC_ID AWS_SUBNET_ID
      packer build $FILE ) || ( printf "%s not found\n" $FILE && exit 1 )

## end main

