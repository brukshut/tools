#!/usr/bin/env python

##
## diff_tunes.py
## file_walk with me
## verify that my m4a and mp3 directories are in sync
## takes paths to two directories of encoded files
## assumes directory names match file extension
## 
import re
import os
import os.path
import shutil
import argparse

## functions
def argue():
  basedir = '/Users/cgough/Desktop/music/mp3'
  compdir = '/Users/cgough/Desktop/music/m4a'
  parser = argparse.ArgumentParser(description="Compare directories of encoded files")
  parser.add_argument("-b", "--basedir", default=basedir, help=f'default: {basedir}')
  parser.add_argument("-c", "--compdir", default=compdir, help=f'default: {compdir}')
  args = parser.parse_args()
  return args

def list_files(basedir, extension, filelist, parent=None):
  ## walk directories and build lists of files
  ## only count files that match given file extension
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
        filelist.append(f'file:{basedir}/{file}')
    ## if we are a directory
    elif os.path.isdir(filepath):
      dirpath = re.sub((f'^.*/{extension}/'), '', filepath)
      filelist.append(f'directory:{dirpath}')
      ## recurse
      filelist = list_files(filepath, extension, filelist, basedir)
  return filelist

def file_walk(basedir, compdir):
  ## we have several directories of encoded music files
  ## we have mp3 directory containing mp3 files encoded from m4a files
  ## these directories are named by file extension, i.e. "mp3" or "m4a"
  ## these folders should be in sync with the exception of file extension
  list1, list2 = ([] for i in range(2))
  ext1 = basedir.split('/').pop()
  ext2 = compdir.split('/').pop()
  list1 = list_files(basedir, ext1, list1)
  list2 = list_files(compdir, ext2, list2)
  return list1, list2

def diff_files(list1, list2):
  diff = []
  for file in list1:
    if not file in list2:
      diff.append(f'{file}')
  return diff

def print_diff(ext, diff):
  if len(diff) > 0:
    print(f'Files present only in {ext}:')
    for file in diff:
      print(f"present only in {ext} --> {file.split(':')[1]}")

def main():
  args = argue()
  enc1, enc2, diff = ([] for i in range(3))
  ext1 = args.basedir.split('/').pop()
  ext2 = args.compdir.split('/').pop()
  enc1, enc2 = file_walk(args.basedir, args.compdir)
  ## show differences between directories
  print_diff(ext1, diff_files(enc1, enc2))
  print_diff(ext2, diff_files(enc2, enc1))

## end functions
main()
