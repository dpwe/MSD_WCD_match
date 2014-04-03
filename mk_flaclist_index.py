# mk_flaclist_index.py
#
# Read the list of arist/album/title/dur/path entries from WCD 
# in flaclist.txt.tgz
# and use it to populate a whoosh index
# in WCDindexdir
#
# 2013-12-11 Dan Ellis dpwe@ee.columbia.edu

import whoosh, whoosh.fields, whoosh.index, whoosh.analysis
from whoosh.support.charset import accent_map
import os.path

# flaclist.txt contains artist	album	title	length	dir	name
flaclistgz = "flaclist.txt.gz"

# Setup whoosh index structure
A = (whoosh.analysis.StemmingAnalyzer() 
     | whoosh.analysis.CharsetFilter(accent_map) )
schema = whoosh.fields.Schema(
                artist=whoosh.fields.TEXT(stored=True, analyzer=A), 
                album=whoosh.fields.TEXT(stored=True, analyzer=A), 
                title=whoosh.fields.TEXT(stored=True, analyzer=A), 
                duration=whoosh.fields.NUMERIC(stored=True), 
                iadir=whoosh.fields.ID(stored=True),
                ianame=whoosh.fields.ID(stored=True))
indexdir = 'WCDindexdir'
if not os.path.exists(indexdir):
    os.mkdir(indexdir)
ix = whoosh.index.create_in(indexdir, schema)

writer = ix.writer()

# helper functions for finding durations
import re
myre = re.compile(r'(.*)\(([0-9:.]*)\)')

def hms_to_sec(hms):
    ''' convert hh:mm:ss.ccc into a real-valued second count '''
    parts = hms.split(':')
    secs = 0.0
    for part in parts:
        secs = 60*secs + float(part)
    return secs

def extract_dur(title):
    ''' If <title> is a string like 
        Tuyi (3:01)
        extract the duration part and return ('Tuyi', 181.0)
        Usese pre-compiled RE in global <myre>
    '''
    dur = 0.0;
    if title[-1] == ')':
        res = myre.match(title)
        if res:
            title = res.group(1)
            dur = hms_to_sec(res.group(2))
    return title, dur

def normz(string):
  # Normalize a string by mapping to lower case and mapping any non-alphanumerics to space
  return re.sub('[^-A-Za-z0-9]',' ',string.lower())

#title = 'Ponyo (3:05)'
#ti, du = extract_dur(title)
#print ti, du


# Now, read from the gunzip pipe and write into index
import subprocess

count = 0
#with subprocess.Popen(['/usr/bin/gunzip','-c',flaclistgz], stdout=subprocess.PIPE) as fp:
fp = subprocess.Popen(['/bin/gunzip','-c',flaclistgz], 
                      stdout=subprocess.PIPE)

if fp != None:
    for line in fp.stdout:
        # discard first line - it's the header
        # artist	album	title	length	dir	name
        if count > 0 and len(line) > 0:
            goon = True
            try:
                artist, album, title, dur, iadir, ianame = line.strip().split('\t',6)
            except:
                print "problem splitting line ", count
                print line.strip().split('\t')
                goon = False
            if goon:
                if dur == '<missing>':
                    title, dur = extract_dur(title)
                writer.add_document(artist=unicode(normz(artist), encoding='utf-8'), 
                                    album=unicode(normz(album), encoding='utf-8'), 
                                    title=unicode(normz(title), encoding='utf-8'), 
                                    duration=float(dur), 
                                    iadir=unicode(iadir, encoding='utf-8'), 
                                    ianame=unicode(ianame, encoding='utf-8'))
        count += 1
        if count % 10000 == 0:
            print count

fp.terminate()
writer.commit()

# 1h25 to run through all 7.1M entries on Porkpie

