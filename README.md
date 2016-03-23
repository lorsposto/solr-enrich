# solr-enrich
Enrich indexed Solr documents to a new Solr core using these scripts.

## geo_enrich.py
Extract geospatial info and index an enriched copy of the document to a new core.

This script utilizes GeoTopicParser: https://wiki.apache.org/tika/GeoTopicParser

Make sure to follow the set up steps at the link above to set up `location-ner-model` and `geotopic-mime`.

This script queries documents from the Solr source core and extracts geo data from the document's 'content' field.
GeoTopicParser returns a set of location names and coordinates. This information is added to each document in the
fields 'location_names' and 'location_coordinates' respectively, and the new document is indexed to the destination
core.

Make sure you have:
  - a lucene-geo-gazetteer server running.
  - a Tika server running with location-ner-model and geotopic-mime in the classpath.
  - a Solr server running. Set the source core url (the core of documents you want to process)
      and the destination core url (where the enriched documents will go).
  - multivalue fields called `location_names` and `location_coordinates` in your destination schema
  
This script assumes Tika is set up with GeoTopicParser. If any of the above is not satisfied, documents will still be
indexed into the destination core, but will not have any new data. If you do not configure your own Tika server,
tika-python will attempt to start its own server, which will not have the necessary items in the classpath.
Additionally, the gazetteer must be running for the Geo extractions to be performed.

#### Usage

The script takes the command-line arguments:
- `--src`, `-s` : URL of the source Solr core.
- `--dest-`, `-d` : URL of the destination Solr core.
- `--tika`, `-t` : URL of the Tika server.
- `--start` : the start row from which to the source Solr core.
- `--rows` : the number of rows to query from the source Solr core, starting at `start`.
- `--rounds` : the number of iterations to query from the source Solr core. Each iteration, `start` is advanced by `rows`.

`python geo_enrich.py --src [src_solr_core_url] --dest [dest_solr_core_url --tika [tika_server_url] --start [start] --rows [rows] --rounds [rounds]`

`python geo_enrich.py --src http://localhost:8983/solr/core1 --dest http://localhost:8983/solr/core2 --tika http://localhost:9980/tika --start 0 --rows 1000 --rounds 100`
