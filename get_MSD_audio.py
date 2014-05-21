#
# get_MSD_audio.py
#
# Functions to retrieve the audio for a specified MSD item from the IA archive
#
# 2014-05-21 Dan Ellis dpwe@ee.columbia.edu

# Constants
lookupfile = "MSD-to-WCD-v3.txt"
audiodir = "audio"

# global lookup dictionary
msd_dict = {};

# Initialize
def build_msd_dict(lookupfile):
    """ Read a file written by qry_flaclist_index to build a dict mapping MSD TR IDs to the place to find them in the WCD archive """
    # Initialize empty dictionary
    msd_dict = {};
    with open(lookupfile, 'r') as f:
        for line in f:
            
