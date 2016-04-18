from __future__ import print_function
from utils import print_import_error
try:
    import pysolr
    from pysolr import SolrError
except ImportError as e:
    print_import_error('pysolr', e)
    exit(1)
import json
import urllib2
import re
import copy
import argparse

__author__ = 'Lorraine Sposto'

# Using:
# Tika Server 1.12
# Command: lucene-geo-gazetteer -server
# Command: java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli

# SOLR_SOURCE = 'http://polar.usc.edu/solr/polar'
# SOLR_DEST = 'http://polar.usc.edu/solr/geo_enriched'
# SOLR_SOURCE = 'http://localhost:8983/solr/collection1'
# SOLR_DEST = 'http://localhost:8983/solr/geo'
GAZETTEER_SERVER = 'http://localhost:8765/api/search?'


def extract_codes(doc):
    """
    Uses Tika to extract geo data and returns an updated copy of the document.

    This script utilizes GeoTopicParser: https://wiki.apache.org/tika/GeoTopicParser
    Make sure to follow the set up steps at the link above to set up location-ner-model and geotopic-mime.

    This script queries documents from the Solr source core and extracts geo data from the document's 'content' field.
    GeoTopicParser returns a set of location names and coordinates. This information is added to each document in the
    fields 'location_names' and 'location_coordinates' respectively, and the new document is indexed to the destination
    core.

    Make sure you have:
      - a lucene-geo-gazetteer server running.
      - a Tika server running with location-ner-model and geotopic-mime in the classpath. Set the Tika server url below.
      - a Solr server running. Set the source core url (the core of documents you want to process)
          and the destination core url (where the enriched documents will go).

    This script assumes Tika is set up with GeoTopicParser. If any of the above is not satisfied, documents will still be
    indexed into the destination core, but will not have any new data. If you do not configure your own Tika server,
    tika-python will attempt to start its own server, which will not have the necessary items in the classpath.
    Additionally, the gazetteer must be running for the Geo extractions to be performed.

    :param doc: A document from solr, as a dict
    :return: Updated document, as a dict, or None if error
    """
    try:
        names = []
        coords = []
        if 'location_name' in doc:
            print(doc['location_name'])
            q = '&s='.join(['+'.join(x.split()) for x in doc['location_name']])
            if len(q) > 0:
                q = 's=' + q
            print(q)

        url = GAZETTEER_SERVER + q
        res = urllib2.urlopen(url).read()
        print(res)
        enriched = copy.deepcopy(doc)
        enriched['country_code'] = []
        enriched['admincode1'] = []
        enriched['admincode2'] = []
        if res:
            res = json.loads(res)
            for loc in res.keys():
                if res[loc][0]:
                    arr = res[loc][0]
                    if 'countryCode' in arr.keys():
                        print(arr['countryCode'])
                        enriched['country_code'].append(arr['countryCode'])
                    if 'admin1Code' in arr.keys():
                        # state
                        print(arr['admin1Code'])
                        enriched['admincode1'].append(arr['admin1Code'])
                    if 'admin2Code' in arr.keys():
                        print(arr['admin2Code'])
                        enriched['admincode2'].append(arr['admin2Code'])
        # if res[0] == 200:
        #     parsed = res[1]
        #     parsed_json = json.loads(parsed)
        #     for item in parsed_json:
        #         # Group long/lat/name by index
        #         geo_groups = {}
        #         for key in item.keys():
        #             reg = re.findall(r'Optional_([a-zA-Z]+)(\d+)', key)
        #             if reg:
        #                 attr = str(reg[0][0]).lower()
        #                 n = str(reg[0][1])
        #                 if n not in geo_groups.keys():
        #                     geo_groups[n] = {}
        #                 geo_groups[n][attr] = item[key]
        #
        #         for key, value in geo_groups.iteritems():
        #             geokeys = value.keys()
        #             if 'name' in geokeys:
        #                 names.append(value['name'])
        #             lat = ""
        #             longd = ""
        #             if 'latitude' in geokeys:
        #                 lat = str(value['latitude'])
        #             if 'longitude' in geokeys:
        #                 longd = str(value['longitude'])
        #             coords.append(lat + ',' + longd)

        # now we have all names grouped, all coordinates grouped

        return enriched
    except Exception as e:
        print('Error', e.message)
        return None

if __name__ == "__main__":

    print('Exiting...')
