#!/usr/bin/env python

##
## verify that my m4a and mp3 directories are in sync
##

import re
import os
import os.path
import shutil

## recursive function to build list of files
def walkncount (basedir, extension, dirlist, filelist, parent=None):
  ## simple function to count files 
  ## location of mp3s and m4as
  datahome = "/Users/cgough/Desktop/music"

  os.chdir(basedir)
  for file in os.listdir(basedir):
    filepath = "%s/%s" % (basedir, file)

    if re.search(("\." + re.escape(extension) + "$"), file):
      myfile = re.sub(("\." + re.escape(extension) + "$"), '', file)             
      mybasedir = re.sub(("^" + re.escape(datahome) + "/" + re.escape(extension) + "/"), '', basedir)             
      filelist.append("%s/%s" % (mybasedir, myfile))

    ## if file is a directory
    if os.path.isdir(filepath):
      mydir = re.sub(("^" + re.escape(datahome) + "/" + re.escape(extension) + "/"), '', filepath)             
      dirlist.append(mydir)
      walkncount(filepath, extension, dirlist, filelist, basedir)
  return dirlist, filelist


def diff_files(mp3s, m4as):
  print("\n%s" % 'FILES ONLY FOUND IN MP3 FOLDER')
  for file in mp3s:
    if not file in m4as:
      print("%s.mp3" % file)

  print("\n%s" % 'FILES ONLY FOUND IN M4A FOLDER')
  for file in m4as:
    if not file in mp3s:
      print("%s.m4a" % file)

def diff_dirs(mp3d, m4ad):
  print("\n%s" % "DIRS FOUND ONLY IN MP3 FOLDER")
  for dir in mp3d:
    if not dir in m4ad:
      print(dir)

  print("\n%s" % "DIRS FOUND ONLY IN M4A FOLDER")
  for dir in m4ad:
    if not dir in mp3d:
      print(dir)


def main():
  datahome = "/Users/cgough/Desktop/music"

  ## mp3s
  dirlist = []
  filelist = []

  mp3 = []
  mp3d = []
  mp3s, mp3d = walkncount((datahome + '/mp3'), 'mp3', dirlist, filelist)

  #mp3s = filelist
  #mp3d = dirlist
  print("TOTAL MP3 COUNT: %s" % len(mp3s))
  print( "TOTAL MP3 DIRS: %s" % len(mp3d))

  ## m4as
  dirlist = []
  filelist = []
  m4ads = datahome + '/m4a'
  #m4ads = '/Volumes/brukbento/music/m4a'
  walkncount(m4ads, 'm4a', dirlist, filelist)
  m4as = filelist
  m4ad = dirlist
  print( "TOTAL M4A COUNT: %s" % len(m4as))
  print( "TOTAL M4A DIRS: %s" % len(m4ad))

  diff_dirs(mp3d, m4ad)

####
main()

