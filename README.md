# tools
Provides some useful scripts for common chores.

## describe_vpcs.rb

This ruby script will scrape your AWS account for vpc and, optionally, subnet information and outputs `terraform` variable maps. These are useful if you are working with an existing AWS infrastructure that is not managed by `terraform` and do not wish to import your existing vpcs or subnets. It requires a region as an argument passed to the `-r` flag. Without any additional arguments, it will map all existing vpcs that it finds:

```
[brukbook.local:~] brukshut% ./describe_vpcs.rb -r us-west-1

variable "vpcs" {
  type = "map"

  default = {
    bruknet = "vpc-023asdfcbc70c9e" // (10.0.0.0/22)
  }
}
```
If you pass the name of the vpc, or a csv separated list of vpcs, it will generate map variables for public and private subnets for those vpcs:
```
[brukbook.local:~] brukshut% describe_vpcs.rb -r us-west-1 -n bruknet
variable "vpcs" {
  type = "map"

  default = {
    bruknet = "vpc-023asdfcbc70c9e" // (10.0.0.0/22)
  }
}

variable "public_subnets" {
  type = "map"

  default = {
    bruknet-public-1 = "subnet-0222348b9d00bdd56" // bruknet us-west-1a (10.0.0.0/24)
    bruknet-public-2 = "subnet-033234cb1fba656ab" // bruknet us-west-1a (10.0.1.0/24)
  }
}

variable "private_subnets" {
  type = "map"

  default = {
    bruknet-private-1 = "subnet-0asdff7a753bac2c" // bruknet us-west-1a (10.0.2.0/24)
    bruknet-private-2 = "subnet-0asdf2248de5ae93" // bruknet us-west-1a (10.0.3.0/24)
  }
}
```

## make_cert.sh

Generates a 4096 bit rsa key, a certificate signing request and a self signed certificate. Requires a common name.

```
[brukbook.local:~] brukshut% ./make_cert.sh
Usage: ./make_cert.sh -c [commonname]
```