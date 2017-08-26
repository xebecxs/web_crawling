#coding:utf-8
from bs4 import BeautifulSoup


html = '<root><foo id="foo-id" class="foo zoo">Foo</foo><bar>中文</bar><baz/></root>'
soup = BeautifulSoup(html)
print soup.prettify()
print
print soup.foo.string
