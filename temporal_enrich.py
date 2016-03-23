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

__author__ = 'Lorraine Sposto'


if __name__ == "__main__":
    print('Exiting...')

