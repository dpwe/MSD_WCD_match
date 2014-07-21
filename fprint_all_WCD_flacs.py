# fprint_all_WCD_flacs.py
#
# Run the audfprint fingerprinter on all the FLACs in the WCD collection.
# Just save to individual binary files under fprints/ for now.
#
# 2014-06-22 Dan Ellis dpwe@ee.columbia.edu

import os
import sys
import pickle
import get_MSD_audio
import numpy as np

sys.path.append('../python/audfprint')
# fingerprint fns
import audfprint

fp_dir = '../fprints'

import subprocess
import json
import codecs
import gzip

import joblib

# list of all the archive items that exist
flaclist = 'flaclist2.txt'

def read_all_flacs(flaclist):
    """ Read in the list of all flac items """
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
                    names.append(os.path.join(iaitem, name))
                except:
                    #print "%d: problem splitting %s" % (len(names), item)
                    nfails += 1

    print "%d items read, %d skipped" % (len(names), nfails)
    return names

def ensure_dir(fname):
    """ ensure that the directory for the named path exists """
    head, tail = os.path.split(fname)
    if len(head):
        if not os.path.exists(head):
            os.makedirs(head)

def make_fprint(WCD_name):
    """ calculate and store the fprint for one item """
    audio_file = get_MSD_audio.IA_audio_file(WCD_name)
    hashes = audfprint.wavfile2hashes(audio_file)
    WCD_root, WCD_ext = os.path.splitext(WCD_name)
    opfname = os.path.join(fp_dir, WCD_root+'.afp')
    ensure_dir(opfname)
    audfprint.hashes_save(opfname, hashes)
    print "wrote",opfname
    # Delete the files downloaded?
    get_MSD_audio.remove_audio(audio_file)


# Run the whole thing
flacs = read_all_flacs(flaclist)

joblib.Parallel(n_jobs=4)(joblib.delayed(make_fprint)(WCD_name)
                          for WCD_name in flacs)
