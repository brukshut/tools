#!/usr/bin/ruby

##
## describe_vpcs.rb
## outputs terraform map variables
##
## variable "images" {
##   type = "map"
##
##   default = {
##     us-east-1 = "image-1234"
##     us-west-2 = "image-4567"
##   }
## }
##
require 'optparse'
require 'aws-sdk-ec2'
require 'pp'

## methods
## initialize aws ec2 resource
def ec2_resource(region)
  begin
    ec2 = Aws::EC2::Resource.new(region: region)
  rescue => e
    puts e
    exit
  end
end

## initialize aws ec2 client
def ec2_client(region)
  begin
    client = Aws::EC2::Client.new(region: region)
  rescue => e
    puts e
    exit
  end
end

## return list of all vpcs
def get_all_vpcs(ec2)
  all_vpcs = {}
  ec2.vpcs.each do |vpc|
    vpc_name=""
    vpc.tags.each do |tag| 
      vpc_name = tag.value if tag.key == "Name" 
    end
    ## hash of hashes
    all_vpcs[vpc_name] = {
      'cidr_block' => vpc.data['cidr_block'], 
      'vpc_id'     => vpc.data['vpc_id'], 
    }
  end
  all_vpcs
end

## get list of subnets for a vpc
def get_vpc_subnets(client, vpc_id)
  resp = client.describe_subnets({
    filters: [{
      name: "vpc-id", 
      values: [vpc_id]
    }], 
  })
end

## sort and return public or private subnets
def get_subnets(client, vpc_id, vpc_name, subnet_type, subnet_hash)
  resp = get_vpc_subnets(client, vpc_id)
  resp.subnets.each do |subnet|
    if subnet_type == 'public'
      push_subnet(subnet, subnet_hash, vpc_name) if subnet['map_public_ip_on_launch'] 
    elsif subnet_type == 'private'
      push_subnet(subnet, subnet_hash, vpc_name) unless subnet['map_public_ip_on_launch']
    end
  end
  subnet_hash
end

def push_subnet(subnet, subnet_hash, vpc_name)
  subnet_name = ""
  subnet.tags.each do |tag| 
    subnet_name = tag.value if tag.key == "Name" 
  end
  subnet_hash[subnet_name] = { 
    'subnet_name' => subnet_name, 
    'subnet_id'   => subnet['subnet_id'], 
    'subnet_cidr' => subnet['cidr_block'], 
    'vpc_name'    => vpc_name,
    'az'          => subnet['availability_zone']
  }
end

def print_header(name)
  printf "%s \"%s\" {\n", 'variable', name
  printf "  %s\n\n", "type = \"map\""
  printf "  %s\n", "default = {"
end

def print_footer
  printf "  %s\n", "}"
  printf "%s\n\n", "}"
end

def print_subnets(name, subnet_hash)
  unless subnet_hash.length == 0
    print_header(name)
    subnet_hash.sort.each do |k, v|
      printf "    %s = \"%s\" // %s %s (%s)\n", v['subnet_name'], v['subnet_id'], v['vpc_name'], v['az'], v['subnet_cidr']
    end
    print_footer
  end
end

def print_vpcs(all_vpcs)
  print_header('vpcs')
  all_vpcs.each do |vpc_name, vpc_data|
    printf "    %s = \"%s\" // (%s)\n", vpc_name, vpc_data['vpc_id'], vpc_data['cidr_block']
  end
  print_footer
end

def print_vpc_subnets(vpc_list, all_vpcs, client)
  public_subnets = {}
  private_subnets = {}
  ## map vpc(s)
  print_header('vpcs')
  vpc_names = []
  vpc_names = vpc_list.split(",")
  vpc_names.each do |vpc_name|
    vpc_id = all_vpcs[vpc_name]['vpc_id']
    public_subnets  = get_subnets(client, vpc_id, vpc_name, "public", public_subnets)
    private_subnets = get_subnets(client, vpc_id, vpc_name, "private", private_subnets)
    printf "    %s = \"%s\" // (%s)\n", vpc_name, all_vpcs[vpc_name]['vpc_id'], all_vpcs[vpc_name]['cidr_block']
  end
  print_footer
  ## map subnets
  print_subnets('public_subnets', public_subnets)
  print_subnets('private_subnets', private_subnets)
end
## end methods

## main
## options
options = Hash.new
opt_parser = OptionParser.new do |opts|
  opts.banner = "Usage: #{$0} [OPTIONS]"
  opts.on('-r REGION', '--region=REGION', String, 'filter by region') do |v|
    options[:region] = v
  end
  opts.on('-n NAME', '--name=NAME', String, 'filter by name') do |v|
    options[:name] = v
  end
  opts.on('-h', '--help', 'help') do
    puts opts
    exit
  end
end
opt_parser.parse!

## require region
if options[:region].nil?
  puts opt_parser
  exit
end

## connect
ec2 = ec2_resource(options[:region])
client = ec2_client(options[:region])

## get all vpcs
all_vpcs = {}
all_vpcs = get_all_vpcs(ec2)

## map all vpcs without subnets
print_vpcs(all_vpcs) if options[:name].nil?

## map (csv list of) vpc(s) and their public and private subnets
print_vpc_subnets(options[:name], all_vpcs, client) if options[:name]

## end main



