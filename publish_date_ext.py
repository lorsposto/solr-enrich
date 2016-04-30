import requests
import json
from temporal_enrich import get_datestring_from_tagged_dict
from datetime import datetime
try:
    from nltk_contrib.timex import *
except ImportError as e:
    print_import_error('nltk_contrib.timex', e)
    exit(1)

DEFAULT_MAX_DATE = "9999-01-01T00:00:00Z"

def get_base_date(url, content):
    '''
    Attempts to retrieve the publish date of document that corresponds to the
    provided url. There aren't any absolutely accurate methods of accessing this
    data so this method finds the earliest date from 3 methods:
    - retrieving the date from the last modified header of the HTTP response
    - look for a 'last modified|updated' field in the article
    - find the first archive date of the web page using the archive.org APIs

    Note: It may be a good idea to only use one or two of the three since executing
    all 3 will take a long time on large data sets.

    :param url: Url data of the document retrieved from Solr
    :param content: Content of the document retrieved from Solr

    :return: a HTTP datestring if any reasonable date was found, None otherwise
    '''

    last_modified_header = DEFAULT_MAX_DATE
    last_modified_content = DEFAULT_MAX_DATE
    archive_date = DEFAULT_MAX_DATE

    last_modified_header = get_last_modified_header(url)
    last_modified_content = get_last_modified_content(content)
    archive_date = get_archive_date(url)

    earliest_record = min(archive_date, min(last_modified_header, last_modified_content))

    if earliest_record == DEFAULT_MAX_DATE:
        return None
    else:
        return earliest_record

def get_last_modified_header(url):
    datestring = DEFAULT_MAX_DATE

    try:
        r = requests.get(url)
        response = r.headers
    except requests.exceptions.ConnectionError as ce:
        print('Connection error encountered', ce.message)

    if 'last-modified' in response.keys():
        last_mod = response['last-modified']
        tag_dict = tag(last_mod)

        max_len = 0
        largest_dict = None
        for t in tag_dict:
            if len(t) > max_len and len(t) <= 3:
                max_len = len(t)
                largest_dict = t

        if largest_dict is not None:
            datestring = get_datestring_from_tagged_dict(largest_dict);

    return datestring

def get_last_modified_content(content):
    # TODO check the footer of html body? or just content from doc?

    return DEFAULT_MAX_DATE

def get_archive_date(url):
    datestring = DEFAULT_MAX_DATE

    try:
        r = requests.get("http://timetravel.mementoweb.org/api/json/20130115102033/" + url, timeout=10)
        response = json.loads(r.text)
        datestring = response['mementos']['first']['datetime']
    except requests.exceptions.Timeout as te:
        print('Request timed out', te.message)
    except requests.exceptions.ConnectionError as ce:
        print('Connection error encountered', ce.message)
    except ValueError as ve:
        print('Response could not be converted to JSON - data does not have required field', ve.message)
    except KeyError as ke:
        print('Key error encountered - data does not have required field', ke.message)
    except Exception as e:
        print(e.message)

    return datestring

def demo():
    url = "http://www.library.ucla.edu/news/library-research-guides-updated"

    print(get_base_date(url, ""))

if __name__ == "__main__":
    # TODO take url arguments from cmd line
    demo()
