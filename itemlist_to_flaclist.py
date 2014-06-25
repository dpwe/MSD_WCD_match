# itemlist_to_flaclist.py
#
# Takes a list of IA items
# Retrieves its metadata
# then writes a list of all the FLAC fils found
# with related metadata.
#
# Rebuild of the one originally run on IA in 2013-10
#
# 2014-06-22 Dan Ellis dpwe@ee.columbia.edu

import os
import sys

import subprocess
import json
import codecs

# list of all the archive items that exist
itemlist = 'what_cd-itemlist-2014-04-29.txt'

# output file
opfile = 'flaclist2.txt'

# but write it zipped
import gzip

itemcount = 0
flaccount = 0
# Read the metadata of each item to create a list of artist album title length dir name
with open(itemlist, 'r') as fp:
    # write directly to a gzip file, use codecs to translate to utf-8 on output
    with codecs.getwriter('utf-8')(gzip.open(opfile+'.gz', 'wb')) as opfp:
        # header
        opfp.write( ('\t'.join(['#artist','album','title','length','dir','name']))+'\n' )
        # body
        for item in fp:
            # Ignore any errors coming out of ia
            iacmd = ['ia','metadata',item]
            try:
                metadata = json.loads(subprocess.check_output(iacmd))
            except:
                print "*** error running/parsing "+" ".join(iacmd)
                metadata = dict()  # fake an empty result
            #print "Archive",item,"contains",metadata['files_count'],"files"
            if 'files' in metadata:
                for fileinfo in metadata['files']:
                    if 'format' in fileinfo.keys() and fileinfo['format'] == 'Flac':
                        if 'artist' in fileinfo and 'album' in fileinfo and 'title' in fileinfo and 'length' in fileinfo and 'name' in fileinfo:
                            artist = fileinfo['artist']
                            album = fileinfo['album']
                            title = fileinfo['title']
                            length = fileinfo['length']
                            iaitem = item.rstrip('\n')
                            name = fileinfo['name']
                            opfp.write( ('\t'.join([artist, album, title, length, iaitem, name]))+'\n' )
                            flaccount += 1
                        else:
                            print "**warn: missing fields in", fileinfo
                itemcount += 1
                if (itemcount % 100) == 0:
                    print "processed",itemcount,"items (",flaccount,"flacs)"
            else:
                print "**warn: no files metadata for", item
