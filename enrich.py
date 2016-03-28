from __future__ import print_function
from utils import print_import_error
try:
    import pysolr
    from pysolr import SolrError
except ImportError as e:
    print_import_error('pysolr', e)
    exit(1)
try:
    from tika.tika import callServer
except ImportError as e:
    print_import_error('tika', e)
    exit(1)
import argparse
from geo_enrich import extract_geo_from_doc

__author__ = 'Lorraine Sposto'

# Using:
# Tika Server 1.12
# Command: lucene-geo-gazetteer -server
# Command: java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli

GEO_KEY = 'geo'
TEMPORAL_KEY = 'temp'

SOLR_SOURCE = 'http://polar.usc.edu/solr/polar'
SOLR_DEST = 'http://polar.usc.edu/solr/geo_enriched'
# SOLR_SOURCE = 'http://localhost:8983/solr/collection1'
# SOLR_DEST = 'http://localhost:8983/solr/geo'
TIKA_SERVER = 'http://localhost:9998/tika'

def process_solr_docs(name, start, rows, rounds, src, dest, tika):
    queries_made = 0
    num_total_successful = 0
    num_total_failure = 0

    print('Solr Source', src)
    print('Solr Dest', dest)
    print('Tika', tika)
    print('Start:', start)
    print('Rows:', rows)
    print('---------------\n')

    solr_src = pysolr.Solr(src, timeout=10)
    solr_dest = pysolr.Solr(dest, timeout=10)

    failed_at = []
    for i in range(rounds):
        print('Fetching', rows, 'rows from', start)
        r = solr_src.search('*', **{
            'start': start,
            'rows': rows
        })

        geo_docs = []
        for doc in r.docs:
            geo_enriched_doc = None
            if name == GEO_KEY:
                geo_enriched_doc = extract_geo_from_doc(doc, tika)
            elif name == TEMPORAL_KEY:
                pass

            if geo_enriched_doc is not None:
                geo_docs.append(geo_enriched_doc)
                num_total_successful += 1

        try:
            solr_dest.add(geo_docs)
            print('Indexed', num_total_successful, 'docs')
        except SolrError as e:
            failed_at.append(start)
            print('Failed at start', start, 'Query:', queries_made)
            print(e.message)
        queries_made += 1
        start += rows

    print('\n---------------')
    print('Hit Solr', queries_made, 'times')
    print('Successfully indexed', num_total_successful, 'docs')
    print('Failed at starts:', failed_at)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract geospatial data from one solr core and index into another.')

    subparser = parser.add_subparsers(help='The type of extraction to perform',  dest='name')
    geo_parser = subparser.add_parser(GEO_KEY)
    temp_parser = subparser.add_parser(TEMPORAL_KEY)

    geo_parser.add_argument('-s', '--src', dest='source', default=SOLR_SOURCE, help='url of source solr core')
    geo_parser.add_argument('-d', '--dest', dest='dest', default=SOLR_DEST, help='url of destination solr core')
    geo_parser.add_argument('-t', '--tika', dest='tika', default=TIKA_SERVER, help='url of running tika server')
    geo_parser.add_argument('--start', dest='start', type=int, default=0, help='start row to query solr, default 0')
    geo_parser.add_argument('--rows', dest='rows', type=int, default=1000, help='number of rows to query from solr, default 1000')
    geo_parser.add_argument('--rounds', dest='rounds', type=int, default=1, help='number of times to query from solr, default 1')

    temp_parser.add_argument('-s', '--src', dest='source', default=SOLR_SOURCE, help='url of source solr core')
    temp_parser.add_argument('-d', '--dest', dest='dest', default=SOLR_DEST, help='url of destination solr core')
    temp_parser.add_argument('-t', '--tika', dest='tika', default=TIKA_SERVER, help='url of running tika server')
    temp_parser.add_argument('--start', dest='start', type=int, default=0, help='start row to query solr, default 0')
    temp_parser.add_argument('--rows', dest='rows', type=int, default=1000, help='number of rows to query from solr, default 1000')
    temp_parser.add_argument('--rounds', dest='rounds', type=int, default=1, help='number of times to query from solr, default 1')

    args = parser.parse_args()
    print(args)

    name = args.name
    solr_src = args.source
    solr_dest = args.dest
    tika = args.tika
    start = args.start
    rows = args.rows
    rounds = args.rounds

    process_solr_docs(name, start, rows, rounds, solr_src, solr_dest, tika)


    print('Exiting...')
