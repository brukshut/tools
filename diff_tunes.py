#!/usr/bin/env python

##
## diff_tunes.py
## verify that my m4a and mp3 directories are in sync
## takes optional full path of directory containing mp3 and m4a directories as argument
##
import re
import os
import os.path
import shutil
import argparse

## functions
def argue():
  parser = argparse.ArgumentParser(description="Compare m4as and mp3s directories")
  parser.add_argument("-d", "--datahome", default='/Users/cgough/Desktop/music', help="datahome")
  args = parser.parse_args()
  return args

def list_files(basedir, extension, filelist, parent=None):
  ## simple function to walk directories and build lists of files and directories
  os.chdir(f'{basedir}')
  for file in sorted(os.listdir(f'{basedir}')):
    ## we need to preserve path
    filepath = f'{basedir}/{file}'

    if not os.path.isdir(filepath):
      if re.search((f'\.{extension}$'), file):
        ## strip extension from filename
        file = re.sub((f'\.{extension}$'), '', file)
        ## strip basedir from filename
        basedir = re.sub((f'^.*/{extension}/'), '', basedir)             
        filelist.append(f'{basedir}/{file}')

    elif os.path.isdir(filepath):
      filelist.append(re.sub((f'^.*/{extension}/'), '', filepath))
      #filelist.append(filepath)
      filelist = list_files(filepath, extension, filelist, basedir)

  return filelist

def diff_files(a, b):
  diff_list = []
  for file in a:
    if not file in b:
      diff_list.append(f'{file}')
  return diff_list      

def main():
  args = argue()
  ## we have a directory of m4a (apple lossless) files 
  ## we have a directory of mp3 files which we have encoded from m4a files
  ## the folders are named m4a and mp3 respectively
  ## these folders should be in sync with the same number of files and directories
  ## the filenames should be identical except for the extension (.m4a or .mp3)
  mp3s, m4as, diff = ([] for i in range(3))
  mp3s = list_files(f'{args.datahome}/mp3', 'mp3', mp3s)
  m4as = list_files(f'{args.datahome}/m4a', 'm4a', m4as)
  print(f'Total mp3 count: {len(mp3s)}')
  print(f'Total m4a count: {len(m4as)}')

  ## show differences between files and directories
  ## mp3s
  diff = diff_files(mp3s, m4as)
  if len(diff) > 0:
    print(f'Files present only in mp3 folder')
    for file in diff:
      print(f'present only in mp3 --> {file}')

  ## m4as
  diff = diff_files(m4as, mp3s)
  if len(diff) > 0:
    print(f'Files present only in m4a folder')
    for file in diff:
      print(f'present only in m4a --> {file}')

## end functions
main()

