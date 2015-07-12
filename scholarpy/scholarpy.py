# -*- coding: utf-8 -*-

""" cli interface for scholarpy """
__version__ = "0.0.1"

import argparse
from .arxiv import ArxivMetadataCrawler


def parse_options():
    parser = argparse.ArgumentParser(description='Crawl open scholar material')
    parser.add_argument('--arxiv', action='store_true', default=True,
                        help='Crawl arxiv metadata')
    parser.add_argument('--from', default=None, dest='from_date', help='Start date')
    parser.add_argument('--until', default=None, dest='to_date', help='End date')
    parser.add_argument('--transform', help='Transform existing data')
    parser.add_argument('--data-dir', default='/data',
                        help='Path to folder used for storage')
    return parser.parse_args()


def main():
    options = parse_options()
    handler = ArxivMetadataCrawler(data_dir=options.data_dir,
                                   from_date=options.from_date,
                                   to_date=options.to_date)

    if options.transform:
        with open(options.transform, 'r') as data:
            handler.transform(data.read())
    else:
        handler.crawl()
