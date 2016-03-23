from __future__ import print_function
import sys


def print_import_error(module_name, e):
    print('Error importing module \'{module_name}\'.'.format(module_name=module_name), file=sys.stderr)
    print(e, file=sys.stderr)
