geoplanet-concordance
=====================

Tools to make a mapping from [geonames](http://www.geonames.org) to [geoplanet](http://developer.yahoo.com/geo/geoplanet/data/).

It occurs to me that you could add latlngs to geoplanet by using the centroids of the [flickr alpha shapes](http://code.flickr.net/2012/10/24/2273/). Todo next.

of ~2 million non-zip, non-POI features in geoplanet, we match ~440k to geonames. I don't know if this is in the right ballpark, though hand inspecting a handful of failed matches has shown they are missing entirely from geonames

reprocess.py
-----------
This script takes the geoplanet_places tsv, which has the format
> 23682960  "US"  "40th Street Station" ENG POI 12589352
and dereferences the parents all the way up to the country level, and translates the string representation of the woe type (POI here) to the integer woe type.

The output looks like
> 29074691        Kottur, Kancheepuram, Tamil Nadu, IN    7       12586683,2345758        9,8
which is
woeid | fully qualified name, includng parents | woetype | parent woeids | parent woetypes

geonames_matcher.py
-------------------
This script requires a local [twofishes](https://github.com/foursquare/twofishes) server running. It trims each place down to only 3 place components if there are more than 10 tokens in the fully qualified place name (due to twofishes' recursive descent, the number of tokens it can parse is limited, though this is getting fixed). It then geocodes the string, requiring that the woetype matches the twofishes translation of the geonames feature ontology into woetypes. So if we are looking for a state named "new york", we won't accept the city of "new york". Unless the feature is a town, admin3 or suburb (neighborhood), in which case we will accept a match of any of those types, because the definitions are somewhat fluid.

The output from this is very very verbose.
> 4498408 7       35.50208        -79.71475       Westmore, Moore, North Carolina, US     2518362 Westmore, Moore, North Carolina, US     7       12589436,2347592        9,8
geonameid, geonameWoeType, geonameLat, geonameLng, geonameMatchedName, geoplanetWoeId, geoplanetWoeName, geoplanetWoeType, geoplanetParentIds, geoplanetParentWoeTypes

make-better-tsv.py
------------------
reformats the output of geonames_matcher into

> 28645250,8348696,"Murrin Bridge, Cobar, New South Wales, AU",-33.20677,146.37107

woeId,geonameId, fullyQualifiedWoeName, geonameLat, geonameLng
