# fprint_all_WCD_flacs.py
#
# Run the audfprint fingerprinter on all the FLACs in the WCD collection.
# Just save to individual binary files under fprints/ for now.
#
# 2014-06-22 Dan Ellis dpwe@ee.columbia.edu

import os
import sys
import pickle
#import get_MSD_audio
import numpy as np

sys.path.append('../python/audfprint')
# fingerprint fns
import audfprint

fp_dir = '../fprints'

import subprocess
import json
import codecs
import gzip

# list of all the archive items that exist
flaclist = 'flaclist2.txt'

# Read in the list of all flac items
names = []
nfails = 0
with codecs.getreader('utf-8')(gzip.open(flaclist+'.gz', 'rb')) as fp:
    for item in fp:
        item = item.rstrip('\n')
        if item[:7] == "#artist":
            # header
            pass
        else:
            try:
                artist, album, title, length, iaitem, name = item.split('\t')
                names.append(name)
            except:
                #print "%d: problem splitting %s" % (len(names), item)
                nfails += 1

print "%d items read, %d skipped" % (len(names), nfails)

def make_fprint(WCD_archive, WCD_path):
    """ calculate and store the fprint for one item """
    fname = get_MSD_audio.IA_audio_file(WCD_archive, WCD_path)
    hashes = audfprint.wavfile2hashes(fname)
    opfname = os.path.join(fp_dir, fp_path)
    audfprint.hashes_save(opfname, hasehs)
    print "wrote",opfname
    # Delete the files downloaded?
