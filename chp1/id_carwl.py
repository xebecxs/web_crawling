import itertools
from webmap_crawl import download

# maximum number of consecutive download errors allowed
max_errors = 5
# current number of consecutive download errors
num_errors = 0
for page in itertools.count(1):
    url = 'http://example.webscraping.com/view/-%d' % page
    html = download(url)
    if html is None:
        #received an error trying to download this webpage
        num_errors += 1
        if num_errors == max_errors:
            break
    else:
        num_errors = 0