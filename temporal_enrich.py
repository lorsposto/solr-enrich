from __future__ import print_function
from utils import print_import_error
try:
    import pysolr
    from pysolr import SolrError
except ImportError as e:
    print_import_error('pysolr', e)
    exit(1)
try:
    from nltk_contrib.timex import *
except ImportError as e:
    print_import_error('nltk_contrib.timex', e)
    exit(1)
import copy
import re
import string
from datetime import datetime
from publish_date_ext import get_base_date

# TODO: move this somewhere better
months_abbrv = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12}

def extract_temporal_from_doc(doc):
    """
    Uses the NLTK timex.py module to extract temporal tags from the document and
    returns an enriched/updated copy of the document.

    List of extracted/formatted datestrings is added to 'extracted-dates' field
    in enriched document.

    :param doc: A document from solr, as a dict

    :return: Updated document, as a dict, or None if error
    """

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
        temporal_tags = tag(content)
        for tagged_text in temporal_tags:
            if tagged_text not in extracted_date_list:

                if isinstance(tagged_text, dict):
                    date_str = get_datestring_from_tagged_dict(tagged_text)

                    if date_str is not None:
                        if date_str not in extracted_date_list:
                            extracted_date_list.append(date_str)

                # just a year
                elif tagged_text.isdigit() and len(tagged_text) == 4:
                    # date_list = get year month day as list
                    datestring_tag = get_datestring_from_ymd(year=int(tagged_text))
                    if datestring_tag is not None:
                        if datestring_tag not in extracted_date_list:
                            extracted_date_list.append(datestring_tag)

                # If we're here the tag returned is a relative date expression (e.g.
                # 'this year', 'today', etc.)
                else:
                    text = re.sub(tagged_text + '(?!</TIMEX2>)', '<TIMEX2>' + tagged_text + '</TIMEX2>', tagged_text)
                    try:
                        # Retrieve base date
                        if 'url' in doc.keys():
                            base_date = get_base_date(doc['url'], "")
                            base_date.replace("T", " ")
                            base_date.replace("Z", ".00")

                            grounded_text = ground(text, base_date)
                            gr_dates = re.findall(r'"([^"]*)"', grounded_text)

                            for date in gr_dates:
                                ymd_list = date.split('-')

                                year = 0
                                month = 0
                                day = 0

                                if len(ymd_list) > 0:
                                    year = int(ymd_list[0])
                                if len(ymd_list) > 1:
                                    month = int(ymd_list[1])
                                if len(ymd_list) > 2:
                                    day = int(ymd_list[2])

                                datestring_tag = get_datestring_from_ymd(year=year, month=month, day=day)
                                if datestring_tag is not None:
                                    if datestring_tag not in extracted_date_list:
                                        extracted_date_list.append(datestring_tag)

                    except Exception as e:
                        print(e.message)

    print('Extracted dates', extracted_date_list)
    if (len(extracted_date_list)):
        enriched['extracted_dates'] = extracted_date_list

    return enriched

def get_datestring_from_tagged_dict(tagged_text):
    temp_day = None
    temp_month = None
    temp_year = None
    if 'day' in tagged_text:
        temp_day = tagged_text['day']
    else:
        temp_day = 1

    if 'month' in tagged_text:
        temp_month = tagged_text['month']

        if isinstance(temp_month, str):
            if temp_month.lower() in months_abbrv.keys():
                temp_month = months_abbrv[temp_month.lower()]
    else:
        temp_month = 1

    if 'year' in tagged_text:
        temp_year = tagged_text['year']

    return get_datestring_from_ymd(year=temp_year, month=temp_month, day=temp_day)

def get_datestring_from_ymd(year=None, month=None, day=None):
    """
    Format of datestring added to enriched document is: 'YYYY-MM-DDTHH-mm-ssZ'.
    Note that this is the format that Solr requires.

    :param year: (Optional) Year extracted from document, as an integer.
    :param month: (Optional) Month of year extracted from document, as an integer.
    :param day: (Optional) Day of month extracted from document, as an integer.

    :return: Default year = 200, month = 1, day = 1; otherwise datestring of parameters
    formatted to Solr specifications.
    """

    if year is None or int(year) <= 1900 or int(year) >= 2200:
        year = 2000
        return None
    if month is None or month == 0:
        month = 1
    if day is None or int(day) <= 0 or int(day) > 31:
        day = 1

    try:
        year = int(year)
        day = int(day)
    except ValueError as e:
        print ("Year and day must be integers.")
        print(e.message)
        return None

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
            return None

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
