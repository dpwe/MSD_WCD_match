#
# get_MSD_audio.py
#
# Functions to retrieve the audio for a specified MSD item from the IA archive
#
# 2014-05-21 Dan Ellis dpwe@ee.columbia.edu

import os, subprocess

# Constants
lookupfile = "MSD-to-WCD-v3.txt"
lookuppickle = "msd_to_wcd_dict.pickle"
# Root of where files are downloaded (should be absolute) (must exist)
audio_dir = "../audio"

# global lookup dictionary
msd_dict = {};

# Initialize
def build_msd_dict(lookupfile, dt_thresh=2.0):
    """ Read a file written by qry_flaclist_index to build a dict mapping MSD TR IDs to the place to find them in the WCD archive.  dt_thresh rejects tracks whose durations differ by more than this amount """
    # Initialize empty dictionary
    new_msd_dict = {};
    with open(lookupfile, 'r') as f:
        for line in f:
            tokens = line.rstrip('\n').split('\t')
            # 0:TRxxx 1:MSD_dur 2:WCD_dur 3:MSD_artist 4:MSD_album 5:MSD_track 
            # 6:WCD_artist 7:WCD_album 8:WCD_track 9:WCD_archive 10:WCD_path
            TRid = tokens[0]
            MSD_dur = float(tokens[1])
            WCD_dur = float(tokens[2])
            if (WCD_dur > 0) and (abs(MSD_dur - WCD_dur) < dt_thresh):
                # Have a WCD match
                WCD_archive = tokens[9]
                WCD_path = tokens[10]
                # Save in dict
                new_msd_dict[TRid] = [WCD_archive, WCD_path, MSD_dur, WCD_dur]
    return new_msd_dict

# Retrieve a file given IA names
def IA_audio_file(WCD_archive, WCD_path=''):
    """Return path to audio file corresponding to WCD item.  Will download it from archive if file not found locally.

    :parameters:
      - WCD_archive : string
          name of the archive containing desired track

      - WCD_path : string
          path to the file within the archive.  If empty, recovered from 
          WCD_archive using os.path.split

    :returns:
      - fname : string
          full path to audio file, or None if no audio is available

    :note:
      Uses global ``audio_dir`` as root to download files into.
    """
    arc_parts = WCD_archive.split('/')
    if len(WCD_path) == 0:
        # assume we were passed IA as a single archive/path/to/file composite
        WCD_archive = arc_parts[0]
        WCD_path = '/'.join(arc_parts[1:])
    else:
        # Strip leading path off WCD_archive, we don't use it
        WCD_archive = arc_parts[-1]
    # Full target path
    fname = os.path.join(audio_dir, WCD_archive, WCD_path)
    # Does it exist?
    if not os.path.isfile(fname):
        # Maybe we have to update the WCD_archive name to updated value?
        a_id = archive_id(WCD_archive)
        if a_id in wcd_archive_map:
            WCD_archive = wcd_archive_map[archive_id(a_id)]
            fname = os.path.join(audio_dir, WCD_archive, WCD_path)
    # Now try again
    if not os.path.isfile(fname):
        # No, have to try and download
        # Build a list of values for "ia"
        #iacmd = ["ia", "download", WCD_archive, WCD_path]
        iacmd = ["/home/dpwe/MSD_WCD_match/ia_download", "download", WCD_archive, WCD_path]
        # Ignore any errors coming out of ia
        try:
            rcode = subprocess.check_call(iacmd, cwd=audio_dir)
        except:
            print "*** error running "+" ".join(iacmd)
    # Is it there now?
    if not os.path.isfile(fname):
        # WCD fnames contain weird non-ascii UTF-8 chars which print will reject (as does ia often)
        fname_uni = unicode(fname, encoding='utf-8')
        print trid+"->"+fname_uni+" not found"
        # Act like we never knew it
        fname = None

    return fname

def remove_audio(fname):
    """ Cleanup a file previously returned by IA_audio_file - remove the file and its directory """
    if fname[:len(audio_dir)] == audio_dir:
        if os.path.isfile(fname):
            ok = True
            try:
                print "removing",fname
                os.remove(fname)
            except OSError as ex:
                ok = False
                print "Error removing",fname
            head, tail = os.path.split(fname)
            while ok and len(head) > 0 and head != audio_dir and os.path.isdir(head):
                # and os.path.dirisempty(head):
                try:
                    print "rmdiring",head
                    os.rmdir(head)
                except OSError as ex:
                    ok = False
                    print "Error rmdiring", head
                    #if ex.errno == errno.ENOTEMPTY:
                    #    print "directory not empty"
                head, tail = os.path.split(head)
        else:
            print fname,"not found"
    else:
        print fname,"not a child of",audio_dir


# Retrieve a file given MSD tkid
def MSD_audio_file(trid):
    """Return path to audio file corresponding to MSD item.  Will download it from archive if file not found locally.

    :parameters:
      - trid : string
          MSD TK... ID specifying the track desired.

    :returns:
      - fname : string
          full path to audio file, or None if no audio is available

    :note:
      Uses global ``msd_dict`` to do lookup; must be initialized.
      Uses global ``audio_dir`` as root to download files into.
    """
    # Check if we know this track
    fname = None
    if trid in msd_dict:
        vals = msd_dict[trid]
        WCD_archive, WCD_path = vals[0:2]
        fname = IA_audio_file(WCD_archive, WCD_path)
    return fname

# Initialization
import cPickle as pickle
import gzip

# Do we have the index pre-pickled?
if os.path.isfile(lookuppickle):
    # Yes; read it in
    with open(lookuppickle, 'r') as f:
        msd_dict = pickle.load(f)
    print "Loaded from "+lookuppickle
else:
    # No; build from the ascii file
    msd_dict = build_msd_dict(lookupfile)
    # and write it out for next time
    with open(lookuppickle, 'w') as f:
        pickle.dump(msd_dict, f, pickle.HIGHEST_PROTOCOL)
    print "Constructed dict and saved to "+lookuppickle

# Also have to build a map of past to current WCD archive names
def archive_id(archive_name):
    """ Return the numbers at the end of the item """
    return archive_name[archive_name.rfind('_')+1:]

# Turns out archive names have been fixed since I built the map
# but the id numbers are the same, so I can translate
wcd_item_list = 'what_cd-itemlist-2014-04-29.txt'
wcd_archive_map = {}
with open(wcd_item_list, 'r') as f:
    for line in f:
        archive_name = line.rstrip('\n')
        id = archive_id(archive_name)
        wcd_archive_map[id] = archive_name

print len(wcd_archive_map.keys()), " items read from ", wcd_item_list
