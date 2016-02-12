#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of ExtractCoverThumbs, licensed under
# GNU Affero GPLv3 or later.
# Copyright © Robert Błaut. See NOTICE for more information.
#
# This script extracts missing Cover Thumbnails from eBooks downloaded
# from Amazon Personal Documents Service and side loads them
# to your Kindle Paperwhite.
#

from __future__ import print_function

__license__ = 'GNU Affero GPL v3'
__copyright__ = '2014, Robert Błaut listy@blaut.biz'
__appname__ = u'ExtractCoverThumbs'
numeric_version = (0, 9)
__version__ = u'.'.join(map(unicode, numeric_version))
__author__ = u'Robert Błaut <listy@blaut.biz>'

import argparse
import os
import sys
import csv
from lib.pages import get_pages
from lib.extract_cover_thumbs import extract_cover_thumbs
from distutils.util import strtobool

parser = argparse.ArgumentParser()
parser.add_argument('-V', '--version', action='version',
                    version="%(prog)s (version " + __version__ + ")")
parser.add_argument("kindle_directory", help="directory where is a Kindle"
                    " Paperwhite mounted")
parser.add_argument("-s", "--silent", help="print less informations",
                    action="store_true")
parser.add_argument("--overwrite-pdoc-thumbs",
                    help="overwrite personal documents (PDOC) cover "
                         "thumbnails",
                    action="store_true")
parser.add_argument("--overwrite-amzn-thumbs",
                    help="overwrite amzn ebook (EBOK) and book sample (EBSP)"
                         " cover thumbnails",
                    action="store_true")
parser.add_argument("--overwrite-apnx", help="overwrite APNX files",
                    action="store_true")
parser.add_argument("--skip-apnx", help="skip generating APNX files",
                    action="store_true")
parser.add_argument("-f", "--fix-thumb",
                    help="fix thumbnails for PERSONAL badge",
                    action="store_true")
parser.add_argument("-z", "--azw", help="also extract covers from AZW files",
                    action="store_true")
parser.add_argument('-d', '--days', nargs='?', metavar='DAYS', const='7',
                    help='only "younger" ebooks than specified DAYS will '
                    'be processed (default: 7 days).')
parser.add_argument("--dump-pages",
                    help="dump list of new books with a rough number of "
                    "pages from last dump to a file 'book-pages.csv'",
                    action="store_true")
if sys.platform == 'darwin':
    parser.add_argument("-e", "--eject",
                        help="eject Kindle after completing process",
                        action="store_true")

args = parser.parse_args()

kindlepth = args.kindle_directory
docs = os.path.join(kindlepth, 'documents')


def user_yes_no_query(question):
    sys.stdout.write('%s [y/n]\n' % question)
    while True:
        try:
            return strtobool(raw_input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')

if __name__ == '__main__':
    asinlist = []
    mf = os.path.join('book-pages.csv')
    if args.dump_pages:
        print('* Dumping MOBI book pages to a CSV file...')
        if os.path.isfile(mf):
            with open(mf) as f:
                csvread = csv.reader(f, delimiter=';', quotechar='"',
                                     quoting=csv.QUOTE_ALL)
                asinlist = [row[0] for row in csvread]
        else:
            with open(mf, 'wb') as o:
                csvwrite = csv.writer(o, delimiter=';', quotechar='"',
                                      quoting=csv.QUOTE_ALL)
                csvwrite.writerow(
                    ['asin', 'isbn', 'author', 'title', 'pages', 'is_real']
                )
        for dirpath, dirs, files in os.walk(docs):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension not in ['.mobi', '.azw', '.azw3']:
                    continue
                print('* Processing: ' + file.decode(
                    sys.getfilesystemencoding()
                ) + '...')
                row = get_pages(dirpath, file)
                if row is None:
                    continue
                if row[0] in asinlist:
                    print('  * Existing the book entry in the CSV file. '
                          'Skipping... ')
                    continue
                with open(mf, 'ab') as o:
                    print('  ! Updating the CSV file...')
                    csvwrite = csv.writer(o, delimiter=';', quotechar='"',
                                          quoting=csv.QUOTE_ALL)
                    csvwrite.writerow(row)
        print('* Dumping completed...')
    else:
        extract_cover_thumbs(args.silent, args.overwrite_pdoc_thumbs,
                             args.overwrite_amzn_thumbs,
                             args.overwrite_apnx, args.skip_apnx,
                             kindlepth, docs, args.azw, args.days,
                             args.fix_thumb)
    if args.eject and sys.platform == 'darwin':
            os.system('diskutil eject ' + kindlepth)
