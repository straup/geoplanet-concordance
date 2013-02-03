#!/usr/bin/python

# 23682960  "US"  "40th Street Station" ENG POI 12589352

import sys
f = open(sys.argv[1])

ID_COL = 0
CC_COL = 1
NAME_COL = 2
WOE_COL = 4
PARENT_ID_COL = 5

missingWoeTypes = []

def fixWoeType(woeName):
  woeMap ={
      'State': 8,
      'County': 9,
      'LocalAdmin': 10,
      'Country': 12,
      'Town': 7,
      'Suburb': 22,
      'Zip': 11,
      'HistoricalTown': 35,
      'POI': 20,
      'LandFeature': 16,
      'Supername': 19,
      'Airport': 14,
      'Island': 13,
      'Colloquial': 24,
      'Drainage': 15,
      'Timezone': 31,
      'HistoricalState': 26,
      'Zone': 25,
      'HistoricalCounty': 27,
      'Sport': 23,
  }

  if woeName not in woeMap:
    if woeName not in missingWoeTypes:
      missingWoeTypes.append(woeName)
      print >> sys.stderr, "%s missing from woeMap" % woeName
    return 0
  else:
    return woeMap[woeName]


fmap = {}
for l in f:
  parts = l.strip().replace('"', '').split('\t')
  if 'PlaceType' not in l:
    woetype = fixWoeType(parts[WOE_COL])
    if parts[WOE_COL] != 'Zip':
      id = parts[ID_COL]
      fmap[id] = parts
print >> sys.stderr, "DONE parsing file into memory"

def derefParents(pid):
  parent = fmap.get(pid)
  if parent is None:
    print >> sys.stderr, "can't find %s in map" % pid
  else:
    name = parent[NAME_COL]
    #print >> sys.stderr, "FOUND: %s" % (', '.join(parent))
    parentParentId = parent[PARENT_ID_COL]
    woeType = str(fixWoeType(parent[WOE_COL]))
    #print >> sys.stderr, "looking up: %s" % parentParentId
    if parentParentId != '1':
      (ids, woeTypes, names) = derefParents(parentParentId)
      return ([pid] + ids, [woeType] + woeTypes, [name] + names)
  return ([], [], [])

i = 0
for id in fmap:
  i += 1
  if i % 100 == 0:
    print >> sys.stderr, "processed %d records so far" % i
  parts = fmap[id]
  name = parts[NAME_COL]
  lang = parts[3]
  woetype = fixWoeType(parts[WOE_COL])
  parentId = parts[PARENT_ID_COL]

  #print >> sys.stderr, 'going up: %s' % ' '.join(parts)
  (parentIds, parentTypes, names) = derefParents(parentId)
  names = [name] + names

  print "%s\t%s\t%s\t%s\t%s" % (
      id,
      ', '.join(names + [parts[CC_COL]]),
      woetype,
      ','.join(parentIds),
      ','.join(parentTypes)
  )

  del names
  del parentIds
