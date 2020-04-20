#!/usr/bin/env python

##
## Normalize tags of mp3 and m4a files
##
import argparse
import sys
import re
import os
from os import path
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


class M4a:
    def __init__(self, filename: str):
        self.filename = filename
        try:
            self.m4a = mutagen.mp4.MP4(self.filename)
        except mutagen.mp4.MP4StreamInfoError as e:
            print(f"{self.filename} is not an m4a")


    def rename(self):
        """ return updated filename """
        new_name: str = str()
        tags = self.m4a.tags
        artist: str = tags['\xa9ART'][0]
        track_name: str = tags['\xa9nam'][0]
        track_num: str = str(tags['trkn'][0][0]).zfill(2)
        new_name: str = f"{track_num} {artist} - {track_name}.m4a"
        try:
            new_name = f"{os.path.dirname(self.filename)}/{new_name}"
            #os.rename(self.filename, new_name)
        except:
            print(sys.exc_info()[0])            
        return new_name


    def update_tag(self, tag: str, tag_value: str) -> None:
        """ update lossless tag """
        print(tag)
        print(tag_value)


class Mp3:
    def __init__(self, filename, genre=None):
        self.filename = filename
        self.genre = genre
        try:
            self.tags = ID3(filename)
        except ID3NoHeaderError as e:
            print(e.response['Error']['Code'])
            print(f"{file} is not an mp3")


    @staticmethod
    def mutate(tag):
        """ transform characters in tag """
        tag = tag.translate(tag.maketrans('[]', '()'))
        tag = tag.replace('?', '')
        tag = tag.replace(' - ', ' -- ')
        tag = tag.replace('/', ' -- ')
        tag = tag.replace("'", 'xxx').title().replace('xxx', "'")
        return tag


    def _upgrade(self):
        self.tags.update_to_v24()
        self.tags.save()
        #for key, value in self.tags.items():
        #    if key != 'APIC:':
        #        print(f"{key} --> {value}")


    def normalize(self):
        """ normalize tags """
        ## TIT2 --> Just Head
        ## TPE1 --> Nervous Eaters
        ## TRCK --> 2/2
        ## TALB --> Just Head
        ## TPOS --> 1/1
        ## TDRC --> 1979
        ## TCON --> Punk (not always)
        ## TPE2 --> Nervous Eaters
        ## TSSE --> Sound Studio 3

        ## upgrade to 2.4
        self._upgrade()

        titles = list(self.tags['TIT2'])
        if len(titles) is not 0:
            genre = self.mutate(str(titles[0]))
            track_name = self.mutate(str(titles[1]))
        if len(titles) is 0:
            track_name: str = self.mutate(str(self.tags['TIT2']))
            track_name = self.mutate(str(titles[0]))
            try:
                genre: str = self.mutate(str(self.tags['TCON']))
            except KeyError:
                genre = 'Rock'

        artist: str = self.mutate(str(self.tags['TPE1']))
        album_artist: str = self.mutate(str(self.tags['TPE2']))
        album: str = self.mutate(str(self.tags['TALB']))
        try:
            print(f"{album} {artist} {track_name}")
            self.tags['TPE1'] = TPE1(encoding=3, text=artist)
            self.tags['TPE2'] = TPE2(encoding=3, text=artist)
            self.tags['TALB'] = TALB(encoding=3, text=album)
            self.tags['TIT2'] = TIT2(encoding=3, text=track_name)
            self.tags['TCON'] = TIT2(encoding=3, text=genre)
            #self.tags.save()
        except:
            print(sys.exc_info()[0])


    def rename(self):
        """ generate updated filename """
        track = str(self.tags['TRCK']).split('/')[0].zfill(2)
        new_name: str = f"{track} {self.tags['TPE2']} - {self.tags['TIT2']}.mp3"
        return new_name


    def update_tag(self, tag: str, tag_value: str) -> None:
        """ update mp3 tag """
        print(tag)
        print(tag_value)


def argue():
    parser = argparse.ArgumentParser(description="Directory of encoded files")
    parser.add_argument("-b", "--basedir", required=True, help=f'basedir of files')
    parser.add_argument("-t", "--type", required=True, help=f'type of file')
    parser.add_argument("-g", "--genre", help=f'genre')
    args = parser.parse_args()
    return args


def main():
    args = argue()
    files = []
    files = list_files(args.basedir, args.type, files)
    if args.type == "m4a":
        for file in files: 
            m4a = M4a(file)
            m4a.rename()

    if args.type == "mp3":
        for file in files: 
            mp3 = Mp3(file)
            mp3.normalize()
            mp3.rename()


## main

main()

## main

