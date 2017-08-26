# coding=utf-8
import json
import urllib2

def download_coor(url, user_agent='wswp', num_retries=2):
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url,headers=headers)
    try:
        coor = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print "Download error:", e.reason
        html = None
        if num_retries>0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                return download_coor(url,user_agent,num_retries-1)
    js = json.loads(coor)
    print (js['result']['location']['lat'],js['result']['location']['lng'])

if __name__ == "__main__":
    download_coor('http://apis.map.qq.com/ws/geocoder/v1/?address=江苏省扬州市广陵区'+'粗茶淡饭'+'&key=FY5BZ-NCLWP-REDDA-LAH6F-IKYOV-EWFA4')