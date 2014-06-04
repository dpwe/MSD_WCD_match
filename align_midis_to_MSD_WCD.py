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

import joblib

def align_md5_to_MSDs(md5, msd_array):
    for msd_item in msd_array:
        track_id = msd_item[0]
        if track_id in msd_to_wcd:
            dur_diff = np.abs(msd_to_wcd[track_id][2] - msd_to_wcd[track_id][3])
            if dur_diff < .5:
                if md5 in md5_to_path:
                    midi_path = os.path.join(midi_dir, md5_to_path[md5])
                    audio_path = get_MSD_audio.MSD_audio_file(track_id)
                    if audio_path is not None:
                        audio_dir, audio_tail = os.path.split(audio_path)
                        audio_stem, audio_ext = os.path.splitext(audio_tail)
                        output_midi_filename = midi_path.replace(midi_dir, output_root).replace('.mid', '-'+audio_stem+'.mid')
                        output_dir = os.path.dirname(output_midi_filename)
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        if os.path.isfile(output_midi_filename):
                            print "Skipping -", output_midi_filename, "exists"
                        else:
                            print "Aligning", audio_path, "to", midi_path, "writing", output_midi_filename
                            midi_alignment.align_one_file(audio_path, midi_path, output_midi_filename, output_diagnostics=True)


joblib.Parallel(n_jobs=4)(joblib.delayed(align_md5_to_MSDs)(md5, msd_array)
                          for md5, msd_array in md5_to_msd.items())

