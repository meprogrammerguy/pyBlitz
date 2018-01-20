#!/usr/bin/env python3

import pdb
import requests

url = 'http://www.bornpowerindex.com/cgi-bin/DBRetrieve.pl'

data = {
    "getClassName": "on",
    "class": "1",
    "sort": "team"
}

headers = {
    "Host": "www.bornpowerindex.com",
    "Connection": "keep-alive",
    "Content-Length": "33",
    "Cache-Control": "max-age=0",
    "Origin": "http://www.bornpowerindex.com",
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "DNT": "1",
    "Referer": "http://www.bornpowerindex.com/M_COL_FB_CLASS.shtml",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9"
}

r = requests.post(url, data=data, headers=headers)
print(r.content)
