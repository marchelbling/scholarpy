import requests
import json
import os
from .crawler import Crawler
from .utils import wait, parse_xml


DATA_DIR = os.environ.get('DATA_PATH', '/data/')
ARXIV_DIR = os.path.join(DATA_DIR, 'arxiv')
ARXIV_XML_DIR = os.path.join(ARXIV_DIR, 'xml')
ARXIV_META = os.path.join(ARXIV_DIR, 'arxiv.json')
ARXIV_CC = os.path.join(ARXIV_DIR, 'cc.json')
ARXIV_REQUEST_DELAY = 21


class ArxivMetadataCrawler(Crawler):
    @staticmethod
    def get_last_cursor():
        _p = os.path
        xmls = filter(lambda x: _p.splitext(x)[-1] == '.xml',
                      filter(lambda x: _p.isfile(_p.join(ARXIV_XML_DIR, x)),
                             os.listdir(ARXIV_XML_DIR)))
        if not xmls:
            return None
        return _p.splitext(sorted(xmls)[-1])[0].split('_')[-1]

    @staticmethod
    def get_ids():
        ids = set()
        with open(ARXIV_META, 'r') as metadata:
            map(ids.add, json.loads(metadata).get('id'))
        return ids

    @staticmethod
    def base_url():
        return 'http://export.arxiv.org/oai2?verb=ListRecords'

    def __init__(self):
        self.cursor = ArxivMetadataCrawler.get_last_cursor() or '0001'
        self.token = None
        self.clock = None
        self.ids = ArxivMetadataCrawler.get_ids()

    def __nonzero__(self):
        return self.cursor is not None

    @property
    def url(self):
        if self.token is None:
            suffix = '&metadataPrefix=arXivRaw'
        else:
            suffix = '&resumptionToken=' + self.resumption_token

        return ArxivMetadataCrawler.base_url() + suffix

    @property
    def resumption_token(self):
        return '{}|{}'.format(self.token, self.cursor)

    @property
    def name(self):
        return 'arxiv_' + self.cursor

    @wait(ARXIV_REQUEST_DELAY)
    def fetch(self):
        print('Fetching {}'.format(self.url))
        return requests.get(self.url)

    def update(self, content):
        begin = content.find('<resumptionToken>')
        end = content.rfind('</resumptionToken>')
        try:
            self.token, cursor = content[begin:end].split('>')[1].split('|')
            self.cursor = max(int(self.cursor), int(cursor))
        except ValueError:
            self.cursor = None

    def transform(self, content):
        self.store(content, os.path.join(ARXIV_XML_DIR, self.name, '.xml'))

        data = parse_xml(content, 'record',
                         namespace='http://www.openarchives.org/OAI/2.0/',
                         keep_namespace=False)
        data = filter(lambda x: x['id'] not in self.ids, data)

        self.store('\n'.join(map(json.dumps, data)), ARXIV_META)
        self.ids.update(map(lambda x: x['id'], data))

        self.update(content)
