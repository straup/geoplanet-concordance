#!/usr/bin/python

import geocoder
import sys
from threaded_geocoder import *
from geocoder import *
import traceback

geocoder = Geocoder('localhost:20001')

# 378466  La Pastora, La Pastora, Caaguazu, PY    7       26810910,2346451        9,8

def trySearch(line, place, woetype):
  woeTypes = [woetype]

  # town, admin3, suburb
  townWoeTypes = ['7', '10', '22']
  if woetype in townWoeTypes:
    woeTypes = townWoeTypes

  try:
    g = geocoder.geocode(place, {
      'woeRestrict': ','.join(woeTypes),
      'allowedSources': 'geonameid'
    })
    if g and g.geonameid() and g.isFull():
      return GeocodeSuccess(u'\t'.join([unicode(g.geonameid()), unicode(g.woeType()), unicode(g.lat()), unicode(g.lng()), g.matchedName(), line.decode('utf-8')]))
    else:
      return GeocodeFailure(line.decode('utf-8'))
  except:
      print 'timeout'
      return GeocodeTimeout(line.decode('utf-8'))

def lineProcessor(line):
  line = line.strip()
  parts = line.split('\t')
  if len(parts) >= 3:
    woeid = parts[0]
    place = parts[1]
    woetype = parts[2]

    if woetype != '20':
      if len(place.replace('-', ' ').split(' ')) > 10 or (woetype == '16'):
        placeParts = place.split(',')
        if len(placeParts) > 3:
          newPlace = ','.join([placeParts[0]] + placeParts[-2:])
          # print 'made %s into %s' % (place, newPlace)
          place = newPlace
    
      ret = None
      retryCount = 0
      while ((ret == None or ret.status == 'timeout') and retryCount < 3):
        if retryCount > 0:
          print 'retry %d: %s' % (retryCount, line)
        ret = trySearch(line, place, woetype)
        retryCount += 1
      return ret
    else:
      return GeocodeSkip(line.decode('utf-8'))

ThreadedGeocoder().run(sys.argv[1], 'output-matches.txt', 'output-failures.txt', lineProcessor)
