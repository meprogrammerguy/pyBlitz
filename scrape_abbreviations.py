#!/usr/bin/env python3

from urllib.request import urlopen
from urllib.request import HTTPError
from urllib.request import Request

from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import pdb
import json
import csv
from collections import OrderedDict
import contextlib
import os, sys, stat
import datetime
from pathlib import Path
import re

import settings
import pyBlitz

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

year = 0
now = datetime.datetime.now()
year = int(now.year)
if (len(sys.argv)>=2):
    year = GetNumber(sys.argv[1])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)
year -= 1

def main(argv):
    starturl = "http://www.espn.com/college-football/schedule"

    print ("Scrape abbreviations Tool")
    print ("**************************")
    print ("data is from {0}".format(starturl))
    print
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(settings.data_path))
    print ("**************************")
    Path(settings.data_path).mkdir(parents=True, exist_ok=True) 

    url = []
    url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))   
    if (year == int(now.year)):
        for week in range(1, 17):
            url.append("{0}/_/week/{1}/seasontype/2".format(starturl, week))
        url.append("{0}/_/week/1/seasontype/3".format(starturl))                
    else:
        for week in range(1, 17):
            url.append("{0}/_/week/{1}/year/{2}/seasontype/2".format(starturl, week, year))
        url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))   
    pages = []
    for item in url:
        req = Request(url=item,headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        try:
            page = urlopen(req)
        except HTTPError as e:
            page = e.read()
        pages.append(BeautifulSoup(page, "html5lib"))

    Path(settings.data_path).mkdir(parents=True, exist_ok=True)
    stats_sheet = open(settings.data_path + 'abbreviation.csv', 'w', newline='')
    csvwriter = csv.writer(stats_sheet)

    index = 0
    A=[]
    B=[]
    C=[]
    D=[]
    for page in pages:
        tables = page.findAll('table', {"class": "schedule"})
        for table in tables:
            teams=table.findAll('abbr')
            for team in teams:
                A.append(pyBlitz.CleanString(team['title']))
                B.append(team.text)
                index+=1
    C=list(OrderedDict.fromkeys(A))
    D=list(OrderedDict.fromkeys(B))
    index = len(C)
    IDX=[]
    for loop in range(1, index + 1):
        IDX.append(loop)
    df=pd.DataFrame(IDX, columns=['Index'])
    df['Team']=C
    df['Abbreviation']=D
    if (not df.empty):
        with open(settings.data_path + 'abbreviation.json', 'w') as f:
            f.write(df.to_json(orient='index'))

        with open(settings.data_path + "abbreviation.json") as stats_json:
            dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)

        count = 0
        for row in dict_stats.values():
            if (count == 0):
                header = row.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(row.values())
    stats_sheet.close()
    for root, dirs, files in os.walk(settings.data_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
