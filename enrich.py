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
import re
from geo_enrich import extract_geo_from_doc
from temporal_enrich import extract_temporal_from_doc

__author__ = 'Lorraine Sposto'

# Using:
# Tika Server 1.12
# Command: lucene-geo-gazetteer -server
# Command: java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli

GEO_KEY = 'geo'
TEMPORAL_KEY = 'temp'
NOTHING_KEY = 'nothing'

SOLR_SOURCE = 'http://polar.usc.edu/solr/geo'
SOLR_DEST_GEO = 'http://polar.usc.edu/solr/geo'
SOLR_DEST_TEMP = 'http://polar.usc.edu/solr/temporal'
TIKA_SERVER = 'http://localhost:9998/tika'

def do_nothing(doc):
    return doc


def process_solr_docs(name, start, rows, rounds, src, dest, tika, dry):
    queries_made = 0
    num_total_docs = 0
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

        enriched_docs = []
        for doc in r.docs:
            num_total_docs += 1
            enriched = None
            if name == GEO_KEY:
                enriched = extract_geo_from_doc(doc, tika)
            elif name == TEMPORAL_KEY:
                enriched = extract_temporal_from_doc(doc)
            elif name == NOTHING_KEY:
                enriched = do_nothing(doc)

            if enriched is not None:
                if '_version_' in enriched.keys():
                    del enriched['_version_']
                if 'boost' in enriched.keys():
                    del enriched['boost']
                if 'tstamp' in enriched.keys():
                    tstamp = enriched['tstamp']
                    reg = re.findall('ERROR:SCHEMA-INDEX-MISMATCH,stringValue=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z)', tstamp)
                    if reg is not None and len(reg) > 0:
                        tstamp = str(reg[0])
                        enriched['tstamp'] = tstamp

                enriched_docs.append(enriched)
                num_total_successful += 1
            else:
                print('Document', i, 'failed from start', start)
        try:
            if not dry:
                solr_dest.add(enriched_docs)
                print('Indexed', num_total_successful, 'docs')
            else:
                print('Dry run, not indexing to solr')
        except SolrError as e:
            failed_at.append(start)
            print('Failed at start', start, 'Query:', queries_made)
            print(e.message)
        queries_made += 1
        start += rows

    print('\n---------------')
    print('Hit Solr', queries_made, 'times')
    print('Total documents found: ', num_total_docs)
    print('Successfully indexed', num_total_successful, 'docs')
    print('Failed at starts:', failed_at)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract geospatial data from one solr core and index into another.')

    subparser = parser.add_subparsers(help='The type of extraction to perform',  dest='name')
    geo_parser = subparser.add_parser(GEO_KEY)
    temp_parser = subparser.add_parser(TEMPORAL_KEY)
    nothing_parser = subparser.add_parser(NOTHING_KEY)

    geo_parser.add_argument('-s', '--src', dest='source', default=SOLR_SOURCE, help='url of source solr core')
    geo_parser.add_argument('-d', '--dest', dest='dest', default=SOLR_DEST_GEO, help='url of destination solr core')
    geo_parser.add_argument('-t', '--tika', dest='tika', default=TIKA_SERVER, help='url of running tika server')
    geo_parser.add_argument('--start', dest='start', type=int, default=0, help='start row to query solr, default 0')
    geo_parser.add_argument('--rows', dest='rows', type=int, default=1000, help='number of rows to query from solr, default 1000')
    geo_parser.add_argument('--rounds', dest='rounds', type=int, default=1, help='number of times to query from solr, default 1')
    geo_parser.add_argument('--dry-run', dest='dry', action='store_true', help='if True, print output, dont commit to solr')

    temp_parser.add_argument('-s', '--src', dest='source', default=SOLR_SOURCE, help='url of source solr core')
    temp_parser.add_argument('-d', '--dest', dest='dest', default=SOLR_DEST_TEMP, help='url of destination solr core')
    temp_parser.add_argument('-t', '--tika', dest='tika', default=TIKA_SERVER, help='url of running tika server')
    temp_parser.add_argument('--start', dest='start', type=int, default=0, help='start row to query solr, default 0')
    temp_parser.add_argument('--rows', dest='rows', type=int, default=1000, help='number of rows to query from solr, default 1000')
    temp_parser.add_argument('--rounds', dest='rounds', type=int, default=1, help='number of times to query from solr, default 1')
    temp_parser.add_argument('--dry-run', dest='dry', action='store_true', help='if True, print output, dont commit to solr')

    nothing_parser.add_argument('-s', '--src', dest='source', default=SOLR_SOURCE, help='url of source solr core')
    nothing_parser.add_argument('-d', '--dest', dest='dest', default=SOLR_DEST_TEMP, help='url of destination solr core')
    nothing_parser.add_argument('-t', '--tika', dest='tika', default=TIKA_SERVER, help='url of running tika server')
    nothing_parser.add_argument('--start', dest='start', type=int, default=0, help='start row to query solr, default 0')
    nothing_parser.add_argument('--rows', dest='rows', type=int, default=1000, help='number of rows to query from solr, default 1000')
    nothing_parser.add_argument('--rounds', dest='rounds', type=int, default=1, help='number of times to query from solr, default 1')
    nothing_parser.add_argument('--dry-run', dest='dry', action='store_true', help='if True, print output, dont commit to solr')

    args = parser.parse_args()
    print(args)

    name = args.name
    solr_src = args.source
    solr_dest = args.dest
    tika = args.tika
    start = args.start
    rows = args.rows
    rounds = args.rounds
    dry = bool(args.dry)

    process_solr_docs(name, start, rows, rounds, solr_src, solr_dest, tika, dry)

    print('Exiting...')
