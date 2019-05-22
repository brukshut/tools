#!/usr/bin/ruby

##
## deregister unused amis
##
class AwsChores
  require 'aws-sdk-ec2'
  require 'pp'

  ## constants
  OwnerId='780612422170'

  def initialize(region)
    @ec2 = begin
      Aws::EC2::Resource.new(region: region)
    rescue StandardError => e
      raise e
      exit
    end
  end

  ## return array of objects
  def find_amis(name) 
    amis = @ec2.images({
      owners: [OwnerId],
      filters: [{
        name: 'tag:Name',
        values: ["#{name}"],
      }]
    })
    sorted_amis = (amis.sort_by { |obj| obj.name }).reverse
  end
end

require 'optparse'

## options
options = Hash.new
opt_parser = OptionParser.new do |opts|
  opts.banner = "Usage: #{$0} [OPTIONS]"
  opts.on('-c N', '--count=N', Integer, 'number of images to retain') do |v|
    options[:count] = v
  end
  opts.on('-n NAME', '--name=NAME', String, 'filter images by name tag') do |v|
    options[:name] = v
  end
  opts.on('-h', '--help', 'help') do
    puts opts
    exit
  end
end
opt_parser.parse!

## require count
if options[:count].nil?
  puts opt_parser
  exit
end

## if we don't specify name, clean up all images
if options[:name].nil? 
  image_names = %w(gturn-debian-stretch gturn-bastion gturn-nat gturn-mail gturn-ubuntu-xenial)
else
  image_names = [options[:name]]
end

chores = AwsChores.new('us-west-1')
image_names.each do |name|
  amis = chores.find_amis(name)
  slice = amis.slice(options[:count], amis.count)
  unless slice.nil?
    slice.each do |i|
      print "deregistering #{i.name} (#{i.image_id})..."
      i.deregister
      print "done\n"
    end
  end
end

## print list of all remaining amis
amis = chores.find_amis("gturn-*")
puts "ALL AMIS:"
amis.each do |i|
  puts "#{i.name} #{i.image_id}"
end
