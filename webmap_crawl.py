# coding=utf-8

from bs4 import BeautifulSoup
import urllib2
import re
import csv


def download(url, user_agent='wswp', num_retries=2):
    headers = {'User-agent': user_agent}
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


def crawl_catalog(url,urls):
    # download the catalog html
    html = download(url)
    # extract the shop links
    soup = BeautifulSoup(html)
    urls_temp = soup.findAll('a',href=True)
    for url in urls_temp:
        if re.findall('/shop/\d+\Z',url['href']) and url['href'] not in urls:
            urls.append(url['href'])
    return urls


def input_domain(url):
    urls = []
    count = 0
    f = csv.writer(open('东关街.csv', 'w'))
    for i in range(1,51):
        urls = crawl_catalog(url + str(i), urls)
        print str(i) + ' is ok.'
    for each in urls:
        print each + ' is crawling'
        select_info('http://www.dianping.com' + each,f,each)
        count += 1
        print str(count) + ' have done.'


def select_info(url,f,each):
    html = download(url)
    soup = BeautifulSoup(html)

    # The content that we need
    shop_number = each

    shop_id_html = soup.select('.breadcrumb > span')
    try:
        shop_id = ((shop_id_html[0]).string).encode("gb18030")
        shop_type_html = soup.select('.breadcrumb a')
        shop_type = ''
        for each in shop_type_html:
            temp = each.get_text()
            con = re.findall("\S*", temp)
            shop_type += (con[13] + ' ').encode("gb18030")

        shop_comment = soup.find('span', id="reviewCount").string.encode("gb18030")

        shop_price = soup.find("span", id="avgPriceTitle").string.encode("gb18030")

        shop_comment_score_temp = soup.select('#comment_score > .item')
        shop_comment_score = ''
        for each in shop_comment_score_temp:
            shop_comment_score += each.string.encode("gb18030")
    except BaseException, e:
        shop_id = 'temp'
        shop_type = 'temp'
        shop_comment = 'temp'
        shop_price = 'temp'
        shop_comment_score = 'temp'

    write_to_excel(shop_number,shop_id, shop_type, shop_comment, shop_price, shop_comment_score,f)


def write_to_excel(number,id,type,comment,price,score,f):

    fields = (number,id,type,comment,price,score)
    f.writerow(fields)
    print id + ' has done.'


if __name__ == '__main__':
    input_domain('http://www.dianping.com/search/keyword/12/0_%E4%B8%9C%E5%85%B3%E8%A1%97/p')