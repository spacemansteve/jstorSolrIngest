# jstorSolrIngest
utility code that geocodes plancenames to a bounding box and sends records to Solr

This utility code accepts JSON formatted JSTOR documents which have
been processed to identify placenames.  For each document, the place
names(s) with the highest occurance are geocoded to a bounding box
using the GeoNames API.  Then, for each highly occuring place name, a
Solr document is created.  Several spatial fields are populated (using
the field types RPT and BBox).  

Often, place names are geocoded to a point.  However, this is
insufficient for search systems or displays using heatmaps.  In
these cases, and no doubt others, it is important to obtan the
bounding box for each place name.

Code in getBBox.py uses the GeoNames API to obtain bounding boxes for
placenames.  For performance reasons, this code maintains a cache of
previously geocoded place names.  The cache is saved on disk in the
file geonamesCache.pkl.

Code in bboxTestFile.py is intended to be called from the command
line.  It interates over lines in a file, each line holds metadata on
a JSTOR resource.  The metadata includes place names obtained from
Cliff, Clavin, or a similar geoparser.  If the place name is
successfully geocoded, the resource is added to Solr.

This code uses the GeoNames API.  To use it, you will need a GeoNames
API key/username.  You can obtain this for free from GeoNames.  With the free
key, you are limited to an average of about 2 requests per second.
So, the code in getBBox.py limits API requests to that rate.  If a
location has been previously geocoded then it's bounding box is
retreived from the cache and no request to GeoNames made.  

To run this code from the command line use:
   python bboxTestFile.py path/to/jstorDataFile geoNamesApiKey

When running, it will occasionally print out the number of records
that have been processed.  Rarely, I've seen the program hang.  If
that happens, hit control-C to abort the hung request process the next
jstor document.  




