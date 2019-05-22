#!/bin/bash

##
## asg_instance.sh
##
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
export AWS_DEFAULT_REGION="us-west-1"

## FUNCTIONS
function die { echo "$*" 1>&2 && exit 1; }

function usage { printf "%s\n" "Usage: $0 [-c] [-n] [-t]" ; exit 1; }

function get_instance_id {
  local asg_name=$1
  local instance_id=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names=${asg_name} | jq -r .AutoScalingGroups[0].Instances[0].InstanceId)
  [[ $instance_id == 'null' ]] && die "instance_id is null" || echo $instance_id
}

function get_public_dns {
  local instance_id=$1
  local public_dns=$(aws ec2 describe-instances --instance-id=${instance_id} | jq -r .Reservations[].Instances[].PublicDnsName)
  [[ ! -z $public_dns ]] && echo $public_dns || die
}

function connect_ec2 {
  local asg_name=$1
  ssh -A $(get_public_dns $(get_instance_id $asg_name))
}

function terminate_ec2 {
  local instance_id=$1
  [[ $(aws ec2 terminate-instances --instance-ids ${instance_id}) ]] &&
     echo "terminated ${instance_id}" || die
}

## END FUNCTIONS
while getopts ":n:ct" opt; do
  case $opt in
    c) CONNECT=true
      ;;
    n) ASG_NAME=${OPTARG}
      ;;
    t) TERMINATE=true
      ;;
    *) usage
      ;;
  esac
done

## require asg name and single command
[[ ! -z $ASG_NAME ]] && 
  ( [[ $CONNECT ]] || [[ $TERMINATE ]] ) || usage

## don't handle both commands
( [[ $CONNECT ]] && [[ $TERMINATE ]] ) && usage

## connect or terminate
[[ $CONNECT ]] && connect_ec2 $ASG_NAME
[[ $TERMINATE ]] && terminate_ec2 $(get_instance_id $ASG_NAME)
