# coding=utf-8

from bs4 import BeautifulSoup
import urllib2
import re
import csv
import json


def input_domain(url):
    urls = []
    count = 0
    f = csv.writer(open('东关街2.csv', 'w'))
    for i in range(1,51):
        urls = crawl_catalog(url + str(i), urls)
        print str(i) + ' is ok.'
    for each in urls:
        print each + ' is crawling'
        select_info('http://www.dianping.com' + each,f,each)
        count += 1
        print str(count) + ' have done.'


def crawl_catalog(url, urls):
    # download the catalog html
    html = download(url)
    # extract the shop links
    soup = BeautifulSoup(html)
    urls_temp = soup.findAll('a',href=True)
    for url in urls_temp:
        if re.findall('/shop/\d+\Z',url['href']) and url['href'] not in urls:
            urls.append(url['href'])
    return urls


def download(url):
    req = urllib2.Request(url)
    try:
        html = urllib2.urlopen(req).read()
    except urllib2.HTTPError,e:
        print e.code
        print e.reason
        print e.geturl()
        print e.read()
    return html


def download_coor(url):

    coor = urllib2.urlopen(url)
    js = json.loads(coor.read())
    return [js['result']['location']['lat'],js['result']['location']['lng']]



def select_info(url,f,each):
    html = download(url)
    soup = BeautifulSoup(html)

    # The content that we need
    shop_number = each
    print '1'
    shop_id_html = soup.select('.breadcrumb > span')
    try:

        shop_id = ((shop_id_html[0]).string).encode("gb18030")

        shop_address = ((soup.find('span',{'itemprop':'street-address'}).string).strip()).encode('gb18030')

        address = urllib2.quote('扬州市广陵区'+ (soup.find('span',{'itemprop':'street-address'}).string).encode('utf-8'))
        shop_coor = download_coor('http://apis.map.qq.com/ws/geocoder/v1/?address=%s&key=FY5BZ-NCLWP-REDDA-LAH6F-IKYOV-EWFA4' % address)

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
        shop_address = 'temp'
        shop_coor = 'temp'
        shop_type = 'temp'
        shop_comment = 'temp'
        shop_price = 'temp'
        shop_comment_score = 'temp'

    write_to_excel(shop_number,shop_id, shop_address,shop_coor, shop_type, shop_comment, shop_price, shop_comment_score,f)


def write_to_excel(number,id,address,coor,type,comment,price,score,f):

    fields = (number,id,address,coor,type,comment,price,score)
    f.writerow(fields)
    print id + ' has done.'


if __name__ == '__main__':
    input_domain('http://www.dianping.com/search/keyword/12/0_%E4%B8%9C%E5%85%B3%E8%A1%97/p')