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

def normz(string):
  # Normalize a string by mapping to lower case and mapping many non-alphanumerics to space
  # We don't map apostrophe ' or period . because they are often used in names.
  # but we do map dash - to space since it's possibly inconsistent.
  # braces [] become \[\] and backslash \ becomes \\\\ (four backslashes)
  return re.sub('[-()\[\]!@#$%^&*_+={}:;"<>,/?|\\\\]',' ',string.lower())
  # We used to map any non-alphanumeric-dash ( [^-A-Za-z0-9] ), but that ended up stripping all the accented characters - not good.

def del_parend(string):
  # Remove any sequences in string that are enclosed in parens/braces/brackets
  return re.sub('[\(\[{][^)\]}]*[\)\]}]','_',string)

def findinWCD(artist, album, title, dur):
  # All query terms are reduced to alphanumerics and lower case
  # (avoid problems with underscores preventing fuzzy matches, and NOT being a reserved keyword)
  arp = arparser.parse(normz(artist))
  alp = alparser.parse(normz(album))
  tip = tiparser.parse(normz(title))
  # Strategy: 
  #  (1) Try match of all artist, album, title words
  #  (2) If no hits, try just artist and title
  #  (3) If no hits, try artist alone: do we get any hits?
  #        If not, try deleting parenthesized terms from artist
  #        then try deleting trailing words from artist name until there's only one left
  #  (4) If no hits, try deleting any parenthesized terms from title
  #  (5) In no hits, try deleting up to half the trailing words from title, one by one
  # case (1)
  qry = whoosh.query.And([arp, alp, tip])
  results = search.search(qry)
  if len(results) == 0:
    # case (2)
    qry = whoosh.query.And([arp, tip])
    results = search.search(qry)
  if len(results) == 0:
    # case (3)
    qry = whoosh.query.And([arp])
    results = search.search(qry)
    if len(results) == 0:
      # no matches at all for this artist name - start eroding it
      # first, delete parenthesized terms
      ndpartist = normz(del_parend(artist))
      arp = arparser.parse(ndpartist)
      qry = whoosh.query.And([arp])
      results = search.search(qry)
      if len(results) == 0:
        # then delete words from end
        narwords = filter(len, ndpartist.split(' '))
        for i in range(len(narwords)-1):  # up to nwords - 1 (so just one left)
          # drop i+1 words from end of artist
          arp = arparser.parse(' '.join(narwords[:-(i+1)]))
          qry = whoosh.query.And([arp])
          results = search.search(qry)
          # Stop as soon as we get any matches
          if len(results) > 0:
            break
    # Now we have an artist name that matches something, try with title again
    qry = whoosh.query.And([arp, tip])
    results = search.search(qry)
  if len(results) == 0:
    # case (4)
    ndptitle = normz(del_parend(title))
    tip = tiparser.parse(ndptitle)
    qry = whoosh.query.And([arp, tip])
    results = search.search(qry)
  if len(results) == 0:
    # case (5)
    # filter keeps only the nonempty results of the split
    ntiwords = filter(len, ndptitle.split(' '))
    # for i in range(len(ntiwords)/2):  # integer divide takes floor (rounds down)
    for i in range(len(ntiwords)-1):  # up to nwords - 1 (so just one left)
      # drop i+1 words from end of title
      tip = tiparser.parse(' '.join(ntiwords[:-(i+1)]))
      qry = whoosh.query.And([arp, tip])
      results = search.search(qry)
      # Stop as soon as we get any matches
      if len(results) > 0:
        break
  # OK, we've done our best trying to find results
  bestr = None
  bestddiff = 999999.0
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
