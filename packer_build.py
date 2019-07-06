#!/usr/bin/env python

##
## packer wrapper that fetches vpc and subnet information
## 
import argparse
import boto3
import pprint
import os
import unicodedata
from os import path
from subprocess import Popen, PIPE

## functions
def argue():
    parser = argparse.ArgumentParser(description="Build Packer File")
    parser.add_argument("-f", "--file", required=True, help="name of packer file")
    parser.add_argument("-r", "--region-name", default="us-east-1", help="region name")
    parser.add_argument("-s", "--subnet-name", default="public-us-east-1a", help="name (tag) of public subnet")
    parser.add_argument("-v", "--vpc-name", default="default-vpc", help="name (tag) of vpc")
    args = parser.parse_args()
    return args

def boto_client(region_name, service_name):
    session = boto3.session.Session()
    client = session.client(
        service_name=service_name,
        region_name=region_name
    )
    return client

def fetch_vpc_id(client, vpcname):
    response = client.describe_vpcs(
        Filters=[
            {
                "Name": "tag:Name",
                'Values': [
                   vpcname,
                ]
            },
        ]
    )
    vpc_id = response["Vpcs"][0]["VpcId"]
    return vpc_id

def fetch_subnet_id(client, subnet_name):
    response = client.describe_subnets(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": [
                   subnet_name
                ]
            }
        ]
    )
    subnet_id = (response["Subnets"][0]["SubnetId"])
    return subnet_id

def set_env(region_name, vpc_name, subnet_name):
    ec2 = boto_client(region_name, 'ec2')
    env = dict(os.environ)
    env['AWS_SUBNET_ID'] = fetch_subnet_id(ec2, subnet_name)
    env['AWS_VPC_ID'] =  fetch_vpc_id(ec2, vpc_name)
    env['AWS_DEFAULT_REGION'] = region_name
    return env

def main():
    args = argue()
    ## check for packer file, otherwise exit
    print(args.file + " found") if path.exists(args.file) else exit(args.file + " not found")
    ## set env variables for packer build
    env = set_env(args.region_name, args.vpc_name, args.subnet_name)
    ## build with packer, pass env variables
    Popen(["/usr/local/bin/packer", "build", "centos.json"], env=env)

## end functions

## main

main()

## end main
