import csv
#import lxml.html
import re
import urlparse
import urllib2
import robotparser
from datetime import datetime
import time
import Queue
from bs4 import BeautifulSoup

class Throttle:
    """Add a delay between downloads to the same domain
    """
    def __init__(self,delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self,url):
        """
        calculate the time to sleep
        """
        domain = urlparse.urlparse(url).netloc

        # the time of latest downloading
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() -
                                       last_accessed).seconds
            if sleep_secs > 0:
                # domain has been accessed recently
                # so need to sleep
                time.sleep(sleep_secs)
        # updata the last accessed time
        self.domains[domain] = datetime.now()


def download(url, user_agent='wswp',proxy=None, num_retries=2):

    print 'Downloading:', url
    headers = {'User-agent': 'wswp'}
    request = urllib2.Request(url,headers=headers)

    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme:proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print "Download error:", e.reason
        html = None
        if num_retries>0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download(url, user_agent,proxy,num_retries-1)
    return html


def get_links(html):
    """Return a list of links from html
    """

    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',
                               re.IGNORECASE)

    # list of all links from the webpage
    return webpage_regex.findall(html)


def link_crawler(seed_url, link_regex, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None,
                 num_retries=1,scrape_callback=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = Queue.deque([seed_url])
    # the URL's that have been seen and at what depth
    seen = {seed_url:0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}

    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent,url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []

            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])

            depth = seen[url]
            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex,link))

                for link in links:
                    link = normalize(seed_url,link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within some domain
                        if same_domain(seed_url,link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:',url


def get_robots(url):
    """initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url,'/robots.txt'))
    rp.read()
    return rp


def normalize(seed_url,link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link)      # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url,link)


def same_domain(url1,url2):
    """return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code',
                       'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            soup = BeautifulSoup(html)
            row = []

            for field in self.fields:
                tr = soup.find(attrs={'id': 'places_'+field+"__row"})
                td = tr.find(attrs={'class': "w2p_fw"})
                aim = td.text
                row.append(aim)
            #for field in self.fields:
            #    row.append(tree.cssselect('table > tbody > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            #print row
            self.writer.writerow(row)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/places/default/view', scrape_callback=ScrapeCallback())