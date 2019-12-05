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
from termcolor import colored, cprint

## functions
def argue():
  basedir = '/Users/cgough/Desktop/music/mp3'
  compdir = '/Users/cgough/Desktop/music/m4a'
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

def print_diff(dir, diff):
  if len(diff) > 0:
    ## directory name is same as extension
    ext = dir.split('/').pop()
    cprint(f'\nFiles present only in {dir}:', 'red', attrs=['bold'])
    #print(colored(f'\nFiles present only in {dir}:', 'red'))
    for file in diff:
      ftype = file.split(':')[0]
      if ftype == 'file':
        fname = colored(f"{file.split(':')[1]}.{ext}", 'blue')
        message = f"{dir} --> {fname}"
        print(message)
      elif ftype == 'directory':
        fname = colored(f"{file.split(':')[1]}", 'green')
        message = f"{dir} --> {fname}"
        print(message)

def main():
  args = argue()
  enc1, enc2, diff = ([] for i in range(3))
  ext1 = args.basedir.split('/').pop()
  ext2 = args.compdir.split('/').pop()
  enc1, enc2 = file_walk(args.basedir, args.compdir)
  ## show differences between directories
  print_diff(args.basedir, diff_files(enc1, enc2))
  print_diff(args.compdir, diff_files(enc2, enc1))

## end functions
main()
