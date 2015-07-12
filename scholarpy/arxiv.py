import os
import requests
import datetime
from .crawler import Crawler
from .utils import wait, parse_xml

_p = os.path


class ArxivMetadataCrawler(Crawler):
    REQUEST_DELAY = 21

    @staticmethod
    def get_last_cursor(response_dir):
        xmls = filter(lambda x: _p.splitext(x)[-1] == '.xml',
                      filter(lambda x: _p.isfile(_p.join(response_dir, x)),
                             os.listdir(response_dir)))
        if not xmls:
            return None
        return str(max(int(xml.split('.', 1)[0].rsplit('_', 1)[1])
                       for xml in xmls))

    @staticmethod
    def base_url():
        return 'http://export.arxiv.org/oai2?verb=ListRecords'

    def __init__(self, data_dir=None, from_date=None, to_date=None):
        default_cursor = '0001'
        self.data_dir = _p.join(data_dir, 'arxiv')
        self.response_dir = _p.join(self.data_dir, 'xml')

        if from_date or to_date:
            if not from_date:
                folders = filter(lambda x: _p.isdir(_p.join(self.response_dir, x)),
                                 os.listdir(self.response_dir))
                from_date = max(folder.split('_', 1)[-1] for folder in folders) or '1991-01-01'
            if not to_date:
                to_date = datetime.datetime.now().strftime('%Y-%m-%d')
            # do not override some responses xml, use dedicated folder
            self.response_dir = os.path.join(self.response_dir, '{}_{}'.format(from_date, to_date))
            self.cursor = default_cursor
        else:
            # attempt to find the next cursor retrieved
            self.cursor = ArxivMetadataCrawler.get_last_cursor(self.response_dir) or default_cursor

        if not os.path.isdir(self.response_dir):
            os.makedirs(self.response_dir)

        self.from_date = from_date
        self.to_date = to_date
        self.token = None
        self.clock = None

    def __nonzero__(self):
        return self.cursor is not None

    @property
    def url(self):
        if self.token is None:
            suffix = '&metadataPrefix=arXivRaw'
            if self.from_date:
                suffix += '&from={}'.format(self.from_date)
            if self.to_date:
                suffix += '&until={}'.format(self.to_date)
        else:
            suffix = '&resumptionToken=' + self.resumption_token

        return ArxivMetadataCrawler.base_url() + suffix

    @property
    def resumption_token(self):
        return '{}|{}'.format(self.token, self.cursor)

    @property
    def response_name(self):
        return 'arxiv_' + self.cursor + '.xml'

    @property
    def response_storage(self):
        return os.path.join(self.response_dir, self.response_name)

    @property
    def transform_storage(self):
        return os.path.join(self.data_dir, 'arxiv.json')

    @wait(REQUEST_DELAY)
    def fetch(self):
        print('Fetching {}'.format(self.url))
        return requests.get(self.url)

    def update(self, content):
        begin = content.find('<resumptionToken')
        end = content.rfind('</resumptionToken')
        try:
            self.token, cursor = content[begin:end].split('>')[1].split('|')
            if int(cursor) > int(self.cursor):
                self.cursor = cursor
        except ValueError:
            self.cursor = None

    def transform(self, content):
        data = parse_xml(content, 'record',
                         namespace='http://www.openarchives.org/OAI/2.0/',
                         keep_namespace=False)
        self.store(data, table=self.transform_storage, fmt='json',
                   override=False,
                   unique=lambda x: x.get('id', x['identifier']))
        self.update(content)
