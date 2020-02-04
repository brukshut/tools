#!/usr/bin/env python

##
## simple python script to generate random passwords
##
import argparse
import random
import string
import re

## main
def randomString(length):
  """Generate a random string of fixed length """
  letters = f'{string.digits}{string.ascii_uppercase}{string.ascii_lowercase}{string.punctuation}'
  letters = re.sub('[\\\/\[\]\{\}\(\)]', '', letters)
  return ''.join(random.choice(letters) for i in range(int(length)))

def argue():
  parser = argparse.ArgumentParser(description="Generate Secure Password")
  parser.add_argument("-l", "--length", required=True, help="length of password")
  args = parser.parse_args()
  return args

def main():
  args = argue()
  print(randomString(args.length))

## end functions

## main
main()
## end main
