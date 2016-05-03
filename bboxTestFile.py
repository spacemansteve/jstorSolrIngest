
import sys
import traceback
import json
import getBBox
import operator
import pysolr

# to ingest a file of jstor data in json format
# python bboxTestFile.py ../../data/ejcArticles/ejcSample1000.json geonamesUser
#



def printPlaces(metadata):
    entities = metadata['entities']
    if 'clavin' in entities:
        clavinPlaces = entities['clavin']
    if 'cliff' in entities:
        cliffPlaces = entities['cliff']
        cliffPlaces = [x for x in cliffPlaces if x['type'] == "location"]
    for place in cliffPlaces:
        print place
    return None

def getBestPlacenames(metadata):
    """return a list of array of placenames with the highest  clavin count """
    entities = metadata['entities']
    returnPlaces = []
    maxCount = 0
    if 'clavin' in entities:
        clavinPlaces = entities['clavin']
        clavinPlaces.sort(key=operator.itemgetter('count'), reverse=True)
        if len(clavinPlaces) > 0:
            maxCount = clavinPlaces[0]['count']
            clavinPlaces = [x for x in clavinPlaces if x['count'] == maxCount]
            for place in clavinPlaces:
                placename = place['suggested']
                if (placename.find(',') > -1):
                    # clean up placename string for easier geonames processing
                    cityState = placename.split(',')
                    cityState = [cityState[0].strip(), cityState[1].strip()]
                    returnPlaces.append(cityState)
    return (returnPlaces, maxCount)
    

def processFile(filename, geonames, solr):
    """create Solr records for json objects in file
    each line in the file contains a single json hashtable
    fields in json object are migrated to solr except for 'entities' which Solr didn't aways parse cleanly
    several spatial fields are added as well as fields holding the details from the clavin record
    if multiple placenames share the highest count, create one Solr record for each place name"""
    totalCount = 0
    with open(filename) as file:
        for line in file:
            try:
                current = json.loads(line)
                if 'article_type' in current:
                    cityStates,occurancesCount = getBestPlacenames(current)
                    if (len(cityStates) > 0):
                        for loopCount,cityState in enumerate(cityStates):
                            bbox = geonames.get_BBox(cityState[0], cityState[1])
                            if ('doi' in current):
                                current['id'] = 'doi:' + current['doi'] + ":" + str(loopCount)
                            else:
                                current['id'] = 'nodoi:' + str(totalCount)
                            if ('entities' in current):
                                current.pop('entities', None)
                                totalCount += 1
                            if bbox:
                                envelope = 'ENVELOPE({0},{1},{2},{3})'.format(bbox['west'], bbox['east'],bbox['north'],bbox['south'])
                                current['area_f'] = (bbox['north'] - bbox['south']) * (bbox['east'] - bbox['west'])

                            else:
                                envelope = 'ENVELOPE(0, 0, 0, 0)'
                                current['area_f'] = .00001
                            current['bbox_srpt'] = envelope                    
                            # https://github.com/geoblacklight/geoblacklight-schema/issues/10
                            current['bbox_bbox'] = envelope
                            current['geocodedLocation_s'] = cityState[0] + ', ' + cityState[1];
                            current['geocodedOccurancesCount_i'] = occurancesCount
                            solr.add([current])
                            if ((totalCount % 10) == 0):
                                print totalCount
                            if ((totalCount % 500) == 0): 
                                geonames.saveCache()

                    
            except BaseException as e:
                print e
                traceback.print_exc()
    geonames.saveCache()


if (len(sys.argv) < 3):
    print 'usage: python bboxTestFile.py jstorJsonDataFile geoNamesUserName'
    print '  the url of the Solr instance is hardcoded in this file'
else:
    filename = sys.argv[1]
    geonamesUser = sys.argv[2]
    geonames = getBBox.GeonamesUtil(geonamesUser)
    solrUrl = 'http://localhost:8983/solr/jstorTest/'
    solr = pysolr.Solr(solrUrl)
    processFile(filename, geonames, solr)

