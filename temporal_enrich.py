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
from datetime import datetime


def extract_temporal_from_doc(doc):
    enriched = copy.deepcopy(doc)
    extracted_date_list = []
    master_list = []

    if '_version_' in enriched.keys():
        del enriched['_version_']
    if 'boost' in enriched.keys():
        del enriched['boost']

    if 'content' in doc.keys():
        master_list += doc['content']
    if 'title' in doc.keys():
        master_list += doc['title']

    for content in master_list:
        temporal_tags = timex.tag(content)
        for tag in temporal_tags:
            if tag not in extracted_date_list:

                # just a year
                if isinstance(tag, str) and len(tag) == 4:
                    # date_list = get year month day as list
                    datestring_tag = get_date_string_from_ymd(year=int(tag))
                    # print(datestring_tag)
                    extracted_date_list.append(datestring_tag)
                elif isinstance(tag, dict):
                    day = None
                    month = None
                    year = None
                    if 'day' in tag:
                        day = tag['day']
                    else:
                        day = 1
                    if 'month' in tag:
                        month = tag['month']
                    else:
                        month = 1
                    if 'year' in tag:
                        year = tag['year']
                    print(">> Parsing day {0}, month {1}, year {2}".format(day, month, year))
                    date_str = get_date_string_from_ymd(year=year, month=month, day=day)
                    extracted_date_list.append(date_str)

                # TODO: don't do anything for now because Solr doesn't accept non formatted
                # date strings (so make function to get a date format for the string tag)
                # else:
                    # extracted_date_list.append(tag)

    print('Extracted dates', extracted_date_list)
    if (len(extracted_date_list)):
        enriched['extracted_dates'] = extracted_date_list

    return enriched


def get_date_string_from_ymd(year=None, month=None, day=None):
    if day is None:
        day = 1
    if month is None:
        month = 1

    try:
        year = int(year)
        day = int(day)
    except ValueError as e:
        print ("Year and day must be integers.")
        print(e.message)
        return None

    if year is None or year <= 1900:
        year = 2000

    if isinstance(month, (str, unicode)):
        if len(month) == 3:
            month = datetime.strptime(month, "%b").month
        else:
            month = datetime.strptime(month, "%B").month

    try:
        # print("Parsing day {0}, month {1}, year {2}".format(day, month, year))
        dt = datetime(day=day, month=month, year=year)
    except ValueError as e:
        # try swapping month and day
        try:
            # print("Parsing day {0}, month {1}, year {2}".format(month, day, year))
            dt = datetime(day=month, month=day, year=year)
        except Exception as e:
            print(e.message)
            # print()
            return None

    ret = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print("Parsed", ret)
    # print()
    return ret
