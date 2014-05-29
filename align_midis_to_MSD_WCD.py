# align_midis_to_MSD_WCD.py
#
# Grand alignment of Colin's MIDI collection, as resolved against MSD
# and WCD audio, as resolved against MSD
# to generate ? candidate aligned audio.
#
# 2014-05-22 Dan Ellis dpwe@ee.columbia.edu after code from Colin Raffel

import os
import pickle
import get_MSD_audio
import numpy as np

# Colin's helper function
import midi_alignment

midi_dir = '/home/dpwe/midi'
output_root = '/home/dpwe/midi_aligned'

with open('msd_to_wcd_dict.pickle') as f:
    msd_to_wcd = pickle.load(f)
with open(os.path.join(midi_dir, 'Clean MIDIs-md5_to_path.pickle')) as f:
    md5_to_path = pickle.load(f)
with open(os.path.join(midi_dir, 'Clean MIDIs-md5_to_msd.pickle')) as f:
    md5_to_msd = pickle.load(f)

found = 0
count = 0
for md5, msd_array in md5_to_msd.items():
    for msd_item in msd_array:
        track_id = msd_item[0]
        if track_id in msd_to_wcd:
            dur_diff = np.abs(msd_to_wcd[track_id][2] - msd_to_wcd[track_id][3])
            if dur_diff < .5:
                if md5 in md5_to_path:
                    midi_path = os.path.join(midi_dir, md5_to_path[md5])
                    audio_path = get_MSD_audio.MSD_audio_file(track_id)
                    if audio_path is not None:
                        found += 1
                        #align(midi_path, audio_path)
                        output_midi_filename = midi_path.replace(midi_dir, output_root)
                        output_dir = os.path.dirname(output_midi_filename)
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        print "Aligning", audio_path, "to", midi_path, "writing", output_midi_filename
                        midi_alignment.align_one_file(audio_path, midi_path, output_midi_filename, output_diagnostics=True)
                    count += 1
                    #if count >= 10:
                    #    raise ValueError

print "Found ", found, " of ", count
