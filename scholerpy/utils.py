import re
import time
import xml.etree.ElementTree as et


def wait(delay):
    def decorator(method):
        def clocked(self, *args, **kwargs):
            if self.clock:
                elapsed = time.time() - self.clock
                if elapsed < delay:
                    time.sleep(delay - elapsed)
            result = method(self, *args, **kwargs)
            self.clock = time.time()
            return result
        return clocked
    return decorator


def parse_xml(content, tag, namespace=None, keep_namespace=False):
    """
    >>> xml = '<oai xmlns="http://foo" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://foo bar.xsd">' \
              '<record>' \
                '<header>' \
                  '<date>2009-11-23</date>' \
                '</header>' \
                '<metadata>' \
                  '<id>007.0001</id>' \
                  '<submitter>toto</submitter>' \
                '</metadata>' \
              '</record>' \
            '</oai>'
    >>> parse_xml(xml, '{http://foo}record', keep_namespace=False)
    [{'date': '2009-11-23', 'submitter': 'toto', 'id': '007.0001'}]
    >>> parse_xml(xml, '{http://foo}record', keep_namespace=True)
    [{'{http://foo}date': '2009-11-23', '{http://foo}submitter': 'toto', '{http://foo}id': '007.0001'}]
    """
    ns = re.compile('^{.*?}')
    clean = lambda string: string if keep_namespace else ns.sub('', string)
    node_to_dict = lambda node: {intern(clean(c.tag)): c.text.replace('\n', ' ')
                                 for c in node.iter() if c.text and c.text.strip()}

    tag = tag if not namespace else '{' + namespace + '}' + tag
    nodes = et.fromstring(content).iter(tag)
    return map(node_to_dict, nodes)
