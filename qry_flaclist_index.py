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

def findinWCD(artist, album, title, dur):
  qry = whoosh.query.And([arparser.parse(artist), alparser.parse(album), tiparser.parse(title)])
  results = search.search(qry)
  if len(results) == 0:
    qry = whoosh.query.And([arparser.parse(artist), tiparser.parse(title)])
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
outfile = 'MSD-to-WCD.txt'
t = '\t'
nwrit = 0
with codecs.open(outfile, 'w', "utf-8") as f:
  for ar, al, ti, du, id in msditems:
    dar = ar.decode('utf-8')
    dal = al.decode('utf-8')
    dti = ti.decode('utf-8')
    iar, ial, iti, idu, iid, iin = findinWCD(dar, dal, dti, float(du))
    f.write(id + t + du + t + '%.2f'%idu + t + dar + t + dal + t + dti + t + iar + t + ial + t + iti + t + iid + t + iin + '\n')
    nwrit += 1
    if nwrit % 1000 == 0:
      current_time = datetime.datetime.now().time()
      print current_time.isoformat(), ": Written ", nwrit






