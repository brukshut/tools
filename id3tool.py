#!/usr/bin/env python

##
## Normalize tags of mp3 and m4a files
## Rename mp3 and m4a files
##
## Update Genre Of files
## Update Artist Of files
## Update Album Title Of files
##

import re
import os
import os.path
import argparse
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC

## functions
def list_files(basedir, ext, filelist, parent=None):
  ## walk directories and build lists of files
  ## only count files that match given file extension
  if os.path.isdir(basedir):
    os.chdir(basedir)
  else:
    sys.exit(f'{basedir} does not exit')
  ## basedir exists
  for file in sorted(os.listdir(basedir)):
    ## we need to preserve path
    filepath = f'{basedir}/{file}'
    if not os.path.isdir(filepath):
      if re.search((f'\.{ext}$'), file):
        filelist.append(filepath)
    ## if we are a directory
    elif os.path.isdir(filepath):
      ## recurse
      filelist = list_files(filepath, ext, filelist, basedir)
  return filelist

## functions
def show_id3_tags(file):
  #TIT2 --> Just Head
  #TPE1 --> Nervous Eaters
  #TRCK --> 2/2
  #TALB --> Just Head
  #TPOS --> 1/1
  #TDRC --> 1979
  #TCON --> Punk
  #TPE2 --> Nervous Eaters
  #TSSE --> Sound Studio 3
  tags = ID3(file)
  for k, v in tags.items():
    if k == 'APIC:' or re.search(('^COMM.*'), k):
      next
    else:
      print(f'{k} --> {v}')

def rename(file):
  new_file = file.title()
  print(new_file)

def argue():
  parser = argparse.ArgumentParser(description="Directory of encoded files")
  parser.add_argument("-b", "--basedir", required=True, help=f'basedir of files')
  parser.add_argument("-t", "--type", required=True, help=f'type of file')
  args = parser.parse_args()
  return args

def main():
  args = argue()
  list = []
  list = list_files(args.basedir, args.type, list)
  for file in list: 
    rename(file)

## main

main()

## main

#tpe1 = str(tags['TPE1']).title()
#tpe2 = str(tags['TPE2']).title()
#talb = str(tags['TALB']).title()
#tit2 = str(tags['TIT2']).title()

#tags['TALB'] = TALB(encoding=3, text=u'The nervous EATERs')

#print(tpe1)
#print(tpe2)

#tags['TIT2'] = TIT2(encoding=3, text=tit2)
#tags['TPE1'] = TPE1(encoding=3, text=tpe1)
#tags['TPE2'] = TPE2(encoding=3, text=tpe1)
#tags.save(mp3)

## show tags
#show_tags()
