
# from getBBox import geonamesUtil
# sample url
# http://api.geonames.org/searchJSON?name=Logan%20Airport&maxRows=2&username=myUsername&style=FULL

import sys
import urllib
import urllib2
import json
import operator
import pickle
import os.path
import datetime
import time

class GeonamesUtil:
    """code to obtain data from geonames"""

    
    cacheFilename = 'geonamesCache.pkl'

    def __init__(self, username):
        """pass in username to provide to geonames as person making api call"""
        self.username = username
        # we remember old answers in a cache for reuse
        self.cache = {}
        self.lastApiCallDatetime = datetime.datetime.now()
        if os.path.isfile(GeonamesUtil.cacheFilename):
            with open(GeonamesUtil.cacheFilename, 'rb') as file:
                self.cache = pickle.load(file)


    def saveCache(self):
        print 'saving cache'
        with open(GeonamesUtil.cacheFilename, 'wb') as file:
            pickle.dump(self.cache, file);

    # send request to geonames and return bbox from response
    # api usage is rate limited to 2000/hour so we make requests at most every 2 seconds
    def get_BBox_Aux(self, placename, state):
        currentDatetime = datetime.datetime.now()
        deltaSeconds = (currentDatetime - self.lastApiCallDatetime).total_seconds()
        if (deltaSeconds < 2):
            time.sleep(2 - deltaSeconds)
        self.lastApiCallDatetime = currentDatetime

        baseUrl = "http://api.geonames.org/searchJSON?name=%s&adminCode1=%s&maxRows=20&username=%s&style=FULL"
        placename = urllib.quote(placename)
        url = baseUrl % (placename, state, self.username)
        response = urllib2.urlopen(url)
        textResponse = response.read();
        jsonResponse = json.loads(textResponse)
        if (jsonResponse['totalResultsCount'] > 0):
            results = jsonResponse['geonames']
            for current in results:
                if 'fcl' in current: 
                    if current['fcl'] == 'A':
                        if 'bbox' in current:
                            return current['bbox']

    # maintain cache of returned results
    # currently only works when both place and state (admin 1 code) are provided.  
    def get_BBox(self, placename, state):
        key = "%s:%s" % (placename, state)
        if key in self.cache:
            return self.cache[key]
        else:
            bbox = self.get_BBox_Aux(placename, state)
            if bbox == None:
                print "warning: no bbox for", placename, state
            self.cache[key] = bbox
            return bbox


    @staticmethod


    @staticmethod
    def test(genamesUser):
        util = GeonamesUtil(geonamesUser)
        bbox1 = util.get_BBox("Boston", "MA")
        bbox2 = util.get_BBox("Baltimore", "MD")
        bbox1a = util.get_BBox("Boston", "MA")
        bbox2a = util.get_BBox("Baltimore", "MD")
        if bbox1 != bbox1a:
            print 'error 1'
        if bbox2 != bbox2a:
            print "error 2"
        print 'end test'
        
    



