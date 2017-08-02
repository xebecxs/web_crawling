import re
import urlparse
import urllib2


def download(url, user_agent='abcd', num_retries=2):
    print 'Downloading:', url
    headers = {'User-agent': 'abcd'}
    request = urllib2.Request(url,headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print "Download error:", e.reason
        html = None
        if num_retries>0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                return download(url,user_agent,num_retries-1)
    return html


def get_links(html):
    """Return a list of links from html
    """

    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',
                               re.IGNORECASE)

    # list of all links from the webpage
    return webpage_regex.findall(html)


def link_crawler(seed_url, link_regex):
    """Crawl from the given seed URL following links matched by link_regex
    """
    crawl_queue = [seed_url]
    seen = set(crawl_queue)
    while crawl_queue:
        url = crawl_queue.pop()
        html = download(url)
        for link in get_links(html):
            if re.match(link_regex,link):
                link = urlparse.urljoin(seed_url, link)
                if link not in seen:
                    seen.add(link)
                    crawl_queue.append(link)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com','/(places/default/index|places/default/view)')