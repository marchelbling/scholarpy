import json
from .utils import identity, compose, true


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
    >>> storage.dump([{'id': 1, 'x': 'a'}, {'id': 2, 'x': 'a'}], tablename,
    ...              fmt='json', unique=object_id)
    >>> storage.load(tablename, fmt='json')
    [{u'x': u'a', u'id': 1}, {u'x': u'a', u'id': 2}]
    >>> storage.load(tablename, fmt='json', func=object_id)
    [1, 2]

    >>> storage.dump([{'id': 1, 'x': 'b'}, {'id': 3, 'x': 'b'}], tablename,
    ...              fmt='json', unique=object_id)
    >>> storage.load(tablename, fmt='json', func=lambda x: (x['id'], x['x']))
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

    def load(self, table, fmt, func=None):
        deserializer = self._deserializer(fmt)
        functor = compose(deserializer, func or identity)

        try:
            with open(table, 'r') as storage:
                return map(functor, storage.readlines())
        except (IOError, ValueError):
            # if file is
            # * not existing
            # * empty/corrupted
            # return no data
            return []

    def _filter(self, table, fmt, unique):
        if unique:
            uniques = set(self.load(table, fmt, func=unique) if unique else [])
            return compose(compose(self._to_fmt(fmt), unique),
                           lambda x: x not in uniques)
        else:
            return true

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
