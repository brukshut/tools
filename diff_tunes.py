#!/usr/bin/env python

##
## diff_tunes.py
## file_walk with me
## verify that my m4a and mp3 directories are in sync
## I have several directories of encoded music files
## I have mp3 files that have been encoded from m4a files
## I keep multiple copies of these encoded files in different places
## As I add new music these folders fall out of sync
## This script will walk two directories and count files with a given extension
## It will then diff the lists of files, ignoring the file extension
## 
import re
import os
import os.path
import shutil
import argparse
import sys
from termcolor import colored, cprint

## functions
def argue():
  basedir = 'mp3:/Users/cgough/Desktop/music/mp3'
  compdir = 'm4a:/Users/cgough/Desktop/music/m4a'
  parser = argparse.ArgumentParser(description="Compare directories of encoded files")
  parser.add_argument("-b", "--basedir", default=basedir, help=f'default: {basedir}')
  parser.add_argument("-c", "--compdir", default=compdir, help=f'default: {compdir}')
  args = parser.parse_args()
  return args

def list_files(basedir, ext, filelist, parent=None):
  ## walk directories and build lists of files
  ## only count files that match given file extension
  if os.path.isdir(basedir):
    os.chdir(f'{basedir}')
  else:
    sys.exit(f'{basedir} does not exit')
  ## basedir exists
  for file in sorted(os.listdir(f'{basedir}')):
    ## we need to preserve path
    filepath = f'{basedir}/{file}'
    if not os.path.isdir(filepath):
      if re.search((f'\.{ext}$'), file):
        ## strip extension from filename
        file = re.sub((f'\.{ext}$'), '', file)
        ## strip basedir from filename
        basedir = re.sub((f'^.*/{ext}/'), '', basedir)
        filelist.append(f'file:{basedir}/{file}')
    ## if we are a directory
    elif os.path.isdir(filepath):
      dirpath = re.sub((f'^.*/{ext}/'), '', filepath)
      filelist.append(f'directory:{dirpath}')
      ## recurse
      filelist = list_files(filepath, ext, filelist, basedir)
  return filelist

def file_walk(basedir, compdir, ext1, ext2):
  ## file_walk with me
  list1, list2 = ([] for i in range(2))
  list1 = list_files(basedir, ext1, list1)
  list2 = list_files(compdir, ext2, list2)
  return list1, list2

def diff_files(list1, list2):
  diff = []
  for file in list1:
    if not file in list2:
      diff.append(f'{file}')
  return diff

def print_diff(dir, diff, ext):
  if len(diff) > 0:
    cprint(f'\nFiles present only in {dir}:', 'red', attrs=['bold'])
    #print(colored(f'\nFiles present only in {dir}:', 'red'))
    for file in diff:
      ftype, fname = file.split(':')
      if ftype == 'file':
        fname = colored(f"{fname}.{ext}", 'blue')
        message = f"{dir} --> {fname}"
        print(message)
      elif ftype == 'directory':
        fname = colored(f"{fname}", 'green')
        message = f"{dir} --> {fname}"
        print(message)

def main():
  args = argue()
  enc1, enc2, diff = ([] for i in range(3))
  ## arg format is ext:directory
  ext1, basedir = args.basedir.split(':')
  ext2, compdir = args.compdir.split(':')
  ## show differences between directories
  enc1, enc2 = file_walk(basedir, compdir, ext1, ext2)
  print_diff(basedir, diff_files(enc1, enc2), ext1)
  print_diff(compdir, diff_files(enc2, enc1), ext2)

## end functions
main()
