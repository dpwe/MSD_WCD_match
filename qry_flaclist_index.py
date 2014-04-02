# qry_flaclist_index.py
#
# Query the index built by mk_flaclist_index.py
# 2014-03-14 Dan Ellis dpwe@ee.columbia.edu

# Querying
import whoosh, whoosh.index, whoosh.qparser
indexdir = 'WCDindexdir'
index = whoosh.index.open_dir(indexdir)
search = index.searcher()

arparser = whoosh.qparser.QueryParser('artist', index.schema)
alparser = whoosh.qparser.QueryParser('album', index.schema)
tiparser = whoosh.qparser.QueryParser('title', index.schema)

# One example query
#artist = u'Darrell Scott'
#album = u'Transatlantic Sessions - Series 3: Volume One'
#title = u'Shattered Cross'
#
#qry = whoosh.query.And([arparser.parse(artist), alparser.parse(album), tiparser.parse(title)])
#results = search.search(qry)
#
#if len(results) == 0:
#    # drop the album
#    qry = whoosh.query.And([arparser.parse(artist), tiparser.parse(title)])
#    results = search.search(qry)
#
#import pprint
#for r in results:
#    pprint.pprint(r)
import re

def findinWCD(artist, album, title, dur):
  # All query terms are reduced to alphanumerics and lower case
  # (avoid problems with underscores preventing fuzzy matches, and NOT being a reserved keyword)
  arp = arparser.parse(re.sub('[^A-Za-z0-9]',' ',artist.lower()))
  alp = alparser.parse(re.sub('[^A-Za-z0-9]',' ',album.lower()))
  tip = tiparser.parse(re.sub('[^A-Za-z0-9]',' ',title.lower()))
  qry = whoosh.query.And([arp, alp, tip])
  results = search.search(qry)
  if len(results) == 0:
    qry = whoosh.query.And([arp, tip])
    results = search.search(qry)
  bestr = None
  bestddiff = 9999
  for i, r in enumerate(results):
    thisdiff = abs(r['duration'] - dur)
    if thisdiff < bestddiff:
      bestr = i
      bestdiff = thisdiff
  if bestr == None:
    return '__NO_MATCH__','','',0,'',''
  else:
    res = results[bestr]
    return res['artist'], res['album'], res['title'], res['duration'], res['iadir'], res['ianame']

# Read in all of MSD records
msditems = []

with open('MSD-all-artist-release-title.txt') as f:
  for l in f:
     # ar, al, ti, du, id
     msditems.append(l.rstrip().split('\t'))

#allres = [];
#for ar, al, ti, du, id in msditems[:10]:
#  allres.append(findinWCD(ar.decode('utf-8'), al.decode('utf-8'), ti.decode('utf-8'), float(du)))

import datetime

import codecs


################# command line args (from postproc_video.py)
import sys
# Default parameters
skiptracks = 0
outfile = 'MSD-to-WCD.txt'
reportstep = 1000

arg = 1
while arg < len(sys.argv):
    argkey = sys.argv[arg];
    if argkey == '-skiptracks':
        arg += 1
        skiptracks = int(sys.argv[arg])
    elif argkey == '-outfile':
        arg += 1
        outfile = sys.argv[arg]
    elif argkey == '-reportstep':
        arg += 1
        reportstep = int(sys.argv[arg])
    else:
        print "Usage: ", sys.argv[0], " -skiptracks <num> -outfile <path> -reportstep <step>"
        raise ValueError('Argument '+argkey+' unrecognized')
    arg += 1


t = '\t'
tracknum = 0
with codecs.open(outfile, 'w', "utf-8") as f:
  for ar, al, ti, du, id in msditems:
    dar = ar.decode('utf-8')
    dal = al.decode('utf-8')
    dti = ti.decode('utf-8')
    if tracknum >= skiptracks:
      iar, ial, iti, idu, iid, iin = findinWCD(dar, dal, dti, float(du))
      f.write(id + t + du + t + '%.2f'%idu + t + dar + t + dal + t + dti + t + iar + t + ial + t + iti + t + iid + t + iin + '\n')
    tracknum += 1
    if tracknum > skiptracks and tracknum % reportstep == 0:
      print datetime.datetime.now(), ": Wrote track # ", tracknum
