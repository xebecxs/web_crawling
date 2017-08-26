# coding=utf-8

import urllib2
from bs4 import BeautifulSoup
import csv
import re


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


def write_to_excel(id,type,comment,price,score):
    f = csv.writer(open('东关街.csv', 'w'))
    fields = (id,type,comment,price,score)
    f.writerow(fields)
    print id[0] + ' has done.'

if __name__ == "__main__":
    html = download('http://www.dianping.com/shop/3461623')
    soup = BeautifulSoup(html)

    # The content that we need

    shop_id_html = soup.select('.breadcrumb > span')
    shop_id = ((shop_id_html[0]).string).encode("gb18030")

    shop_type_html = soup.select('.breadcrumb a')
    shop_type = ''
    print shop_type_html
    for each in shop_type_html:
        temp = each.get_text()
        con = re.findall("\S*", temp)
        shop_type += (con[13]+' ').encode("gb18030")

    shop_comment = soup.find('span',id="reviewCount").string.encode("gb18030")

    shop_price = soup.find("span",id="avgPriceTitle").string.encode("gb18030")

    shop_comment_score_temp = soup.select('#comment_score > .item')
    shop_comment_score = ''
    for each in shop_comment_score_temp:
        shop_comment_score += each.string.encode("gb18030")

    write_to_excel(shop_id,shop_type,shop_comment,shop_price,shop_comment_score)