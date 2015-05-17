import json
from .utils import identity


class Storage(object):
    r"""
    >>> import tempfile
    >>> import operator
    >>> tablename = tempfile.NamedTemporaryFile(delete=False).name
    >>> storage = Storage()

    >>> data = {1: 'foo'}
    >>> storage._to_fmt(None)(data)
    {1: 'foo'}
    >>> storage._to_fmt('json')(data)
    {u'1': u'foo'}

    >>> storage._format('foo')
    'foo\n'
    >>> storage._format(['foo', 'bar'])
    'foo\nbar\n'

    >>> storage.dumps(data, fmt='json')
    '{"1": "foo"}\n'

    >>> object_id = lambda x: operator.__getitem__(x, 'id')
    >>> storage.dump([{'id': 1, 'x': 'a'}, {'id': 2, 'x':'a'}], tablename,
    ...              fmt='json', unique=object_id)
    >>> storage._uniques(tablename, fmt='json', unique=object_id)
    set([1, 2])

    >>> storage.dump([{'id': 1, 'x': 'b'}, {'id': 3, 'x': 'b'}], tablename,
    ...              fmt='json', unique=object_id)
    >>> map(lambda x: (x['id'], x['x']), storage.load(tablename, fmt='json'))
    [(1, u'a'), (2, u'a'), (3, u'b')]
    """
    def _serializer(self, fmt):
        return {
            None: identity,
            'json': json.dumps
        }.get(fmt, identity)

    def _deserializer(self, fmt):
        return {
            None: identity,
            'json': json.loads
        }.get(fmt, identity)

    def _to_fmt(self, fmt):
        serializer = self._serializer(fmt)
        deserializer = self._deserializer(fmt)
        return lambda x: deserializer(serializer(x))

    def load(self, table, fmt):
        try:
            with open(table, 'r') as storage:
                return map(self._deserializer(fmt), storage.readlines())
        except (IOError, ValueError):
            # if file is
            # * not existing
            # * empty/corrupted
            # return no data
            return []

    def _uniques(self, table, fmt, unique):
        data = self.load(table, fmt)
        return set(map(unique, data))

    def _filter(self, table, fmt, unique):
        if unique:
            uniques = self._uniques(table, fmt, unique) if unique else set()
            formatter = self._to_fmt(fmt)
            return lambda x: unique(formatter(x)) not in uniques
        else:
            return lambda x: True

    def _format(self, content):
        if not isinstance(content, basestring):
            content = '\n'.join(content)
        # always end table storage by a newline for least surprise principle
        if content and not content.endswith('\n'):
            content += '\n'
        return content

    def dumps(self, content, fmt, exclude=None):
        if not isinstance(content, (list, tuple)):
            content = [content]
        content = map(self._serializer(fmt),
                      filter(exclude, content))
        return self._format(content)

    def mode(self, override):
        return 'w' if override else 'a'

    def dump(self, content, table, fmt=None, unique=None, override=False):
        content = self.dumps(content, fmt,
                             exclude=self._filter(table, fmt, unique))
        with open(table, self.mode(override)) as table_storage:
            table_storage.write(content)
