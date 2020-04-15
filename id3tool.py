#!/usr/bin/env python

##
## Normalize tags of mp3 and m4a files
## Rename mp3 and m4a files
##
## rename directories (split filename and find dirs and rename?)

## Update Genre Of files
## Update Artist Of files
## Update Album Title Of files
##

import sys
import re
import os
import os.path
import argparse
import mutagen.mp4
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC
from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, cast

## functions
def list_files(basedir, ext, filelist, parent=None):
    ## walk directories and build lists of files
    ## only count files that match given file extension
    if os.path.isdir(basedir):
        os.chdir(basedir)
    else:
        sys.exit(f"{basedir} does not exit")
    ## basedir exists
    for file in sorted(os.listdir(basedir)):
        ## we need to preserve path
        filepath = f'{basedir}/{file}'
        if not os.path.isdir(filepath):
            if re.search((f'\.{ext}$'), file):
                filelist.append(filepath)
        ## if we are a directory, recurse
        elif os.path.isdir(filepath):
            filelist = list_files(filepath, ext, filelist, basedir)

    return filelist


class LossLess:
    def __init__(self, filename: str, genre: str = None):
        self.filename = filename
        try:
            self.lossless = mutagen.mp4.MP4(self.filename)
        except mutagen.mp4.MP4StreamInfoError as e:
            print(f"{self.filename} is not an m4a")


    def rename(self):
        """ return updated filename """
        new_name: str = str()
        tags = self.lossless.tags
        artist: str = tags['\xa9ART'][0]
        track_name: str = tags['\xa9nam'][0]
        track_num: str = str(tags['trkn'][0][0]).zfill(2)
        new_name: str = f"{track_num} {artist} - {track_name}.m4a"
        return new_name


    def update_tag(self, tag: str, tag_value: str) -> None:
        """ update lossless tag """
        print(tag)
        print(tag_value)


class MpThree:
    def __init__(self, filename, genre=None):
        self.filename = filename
        try:
            self.tags = ID3(filename)
        except ID3NoHeaderError as e:
            print(e.response['Error']['Code'])
            print(f"{file} is not an mp3")


    def rename(self):
        """ generate updated filename """
        #TIT2 --> Just Head
        #TPE1 --> Nervous Eaters
        #TRCK --> 2/2
        #TALB --> Just Head
        #TPOS --> 1/1
        #TDRC --> 1979
        #TCON --> Punk
        #TPE2 --> Nervous Eaters
        #TSSE --> Sound Studio 3
        track = str(self.tags['TRCK']).split('/')[0].zfill(2)
        new_name: str = f"{track} {self.tags['TPE2']} - {self.tags['TIT2']}.mp3"
        return new_name


    def update_tag(self, tag: str, tag_value: str) -> None:
        """ update mp3 tag """
        print(tag)
        print(tag_value)
        #tpe1 = str(tags['TPE1']).title()
        #tpe2 = str(tags['TPE2']).title()
        #talb = str(tags['TALB']).title()
        #tit2 = str(tags['TIT2']).title()
        #tags['TALB'] = TALB(encoding=3, text=u'The nervous EATERs')
        #tags['TIT2'] = TIT2(encoding=3, text=tit2)
        #tags['TPE1'] = TPE1(encoding=3, text=tpe1)
        #tags['TPE2'] = TPE2(encoding=3, text=tpe1)
        #tags.save(mp3)


def argue():
    parser = argparse.ArgumentParser(description="Directory of encoded files")
    parser.add_argument("-b", "--basedir", required=True, help=f'basedir of files')
    parser.add_argument("-t", "--type", required=True, help=f'type of file')
    args = parser.parse_args()
    return args

def main():
    args = argue()
    files = []
    files = list_files(args.basedir, args.type, files)
    if args.type == "m4a":
        for file in files: 
            my_m4a = LossLess(file)
            print(my_m4a.rename())

    if args.type == "mp3":
        for file in files: 
            my_mp3 = MpThree(file)
            print(my_mp3.rename())

## main

main()

## main

