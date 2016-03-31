from __future__ import print_function
from utils import print_import_error
try:
    import pysolr
    from pysolr import SolrError
except ImportError as e:
    print_import_error('pysolr', e)
    exit(1)
try:
    from nltk_contrib import timex
except ImportError as e:
    print_import_error('nltk_contrib.timex', e)
    exit(1)
import copy

def extract_temporal_from_doc(doc):
    enriched = copy.deepcopy(doc)
    extracted_date_list = []
    master_list = []

    if 'content' in doc.keys():
        master_list += doc['content']
    if 'title' in doc.keys():
        master_list += doc['title']

    for content in master_list:
        temporal_tags = timex.tag(content)
        for tag in temporal_tags:
            if tag not in extracted_date_list:
                extracted_date_list.append(tag)
                
    enriched['extracted_dates'] = extracted_date_list

    return enriched
