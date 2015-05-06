class Crawler(object):
    def fetch(self):
        raise NotImplementedError

    def transform(self, content):
        raise NotImplementedError

    def crawl(self):
        while self:
            response = self.fetch()
            if response.status_code == 200:
                self.transform(response.content)
            else:
                print(response.content)
                return

    def store(self, content, path):
        with open(path, 'a') as storage:
            storage.write(content)
