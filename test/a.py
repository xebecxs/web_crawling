#coding:utf-8
from lxml import etree

xml_string = '<root><foo id="foo-id" class="foo zoo">Foo</foo><bar>a</bar><baz></baz></root>'
root = etree.fromstring(xml_string.encode('utf-8'))
etree.tostring(root)
print etree.tostring(root,pretty_print=True).encode('utf-8')