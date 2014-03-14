MSD_WCD_match
=============

Matching between metadata from the Million Song Dataset and metadata from large online audio collection.

Run "python mk_flaclist_index.py" to parse a compressed list flaclist.txt.gz, with each line describing 
a known track with tab-separated fields for artist, album, title, duration (sec), archivename, filepath 
for each track.  The parsed result is written to a "whoosh" index in ./WCDindexdir .

Run "python qry_flaclist_index.py" to query the index with information from each line of a list 
MSD-all-artist-release-title.txt, with tab-separated fields for artist, album, title, duration (sec), 
and MSD_ID.  Of the items in the index that (fuzzily) match the artist and title (and album if 
there are any), choose the one whose duration is closest to the one in the index (if any), then 
write out a tab-separated description to MSD-to-WCD.txt with
MSDid MSDduration WCDduration MSDartist MSDalbum MSDname WCDartist WCDalbum WCDtitle WCDarch WCDfile
for each MSD item.  Where no match is found, WCDduration = 0, WCDartst = "__NO_MATCH__", and the 
other WCD fields are empty.
