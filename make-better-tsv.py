#!/usr/bin/python

import csv

# 5014120 9 42.25059  -83.84994 Washtenaw, Michigan, US 12588794  Washtenaw, Michigan, US 9 2347581 8

import sys

reader = csv.reader(open(sys.argv[1]), dialect='excel-tab')
writer = csv.writer(open('geonames-geoplanet-matches.csv', 'w'))
for row in reader:
  writer.writerow([row[5], row[0], row[6], row[2], row[3]])
