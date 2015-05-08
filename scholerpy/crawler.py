from .storage import Storage


class Crawler(object):
    def fetch(self):
        raise NotImplementedError

    def transform(self, content):
        raise NotImplementedError

    def crawl(self):
        while self:
            response = self.fetch()
            if response.status_code == 200:
                self.store(response.content, table=self.response_storage,
                           fmt=None, override=True)
                self.transform(response.content)
            else:
                print(response.content)
                return

    def store(self, *args, **kwargs):
        Storage().dump(*args, **kwargs)
