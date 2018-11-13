#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import pdb
import json
import csv
from collections import OrderedDict
import contextlib
import sys
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

def num_there(s):
    return any(i.isdigit() for i in s)

year = 0
now = datetime.datetime.now()
year = int(now.year)
if (len(sys.argv)>=2):
    year = GetNumber(sys.argv[1])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)

def main(argv):
    starturl = "http://www.espn.com/college-football/schedule"
    path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

    print ("Scrape Schedule Tool")
    print ("**************************")
    print ("data is from {0}".format(starturl))
    print
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(path))
    print ("**************************")

    Path(path).mkdir(parents=True, exist_ok=True) 
    for p in Path(path).glob("sched*.*"):
        p.unlink()

    url = []
    if (year == int(now.year)):
        #url.append(starturl)
        for week in range(1, 16):
            url.append("{0}/_/week/{1}".format(starturl, week))
        url.append("{0}/_/seasontype/3".format(starturl))
    else:
        url.append("{0}/_/year/{1}".format(starturl, year))
        for week in range(1, 16):
            url.append("{0}/_/week/{1}/year/{2}".format(starturl, week, year))        
        url.append("{0}/_/year/{1}/seasontype/3".format(starturl, year))        
    pages = []
    for item in url:
       with contextlib.closing(urlopen(item)) as page:
           pages.append(BeautifulSoup(page, "html5lib"))

    loop = 0
    for page in pages:
        loop+=1
        dates = page.findAll("h2", {"class": "table-caption"})
        tables = page.findAll('table', {"class": "schedule"})
        dateidx = 0
        index = 0
        IDX=[]
        Y=[]
        A=[]
        B=[]
        C=[]
        D=[]
        F=[]
        G=[]
        for table in tables:
            teams=table.findAll('abbr')
            home=table.findAll('td', {"class": "home"})
            scores=table.findAll('td')
            E=[]
            for score in scores:
                data = score.find(text=True)
                if (data is not None and ("Canceled" in data or "Postponed" in data)):
                    E.append(data)
                elif data is not None and ',' in data and num_there(data):
                    E.append(data)
                else:
                    E.append("?")
            if loop == len(pages):
                for item in range(2, len(E), 7):
                    F.append(E[item])
            else:
                for item in range(2, len(E), 6):
                    F.append(E[item])
            neutral=table.findAll('tr', {'class':['odd', 'even']})
            line = 0
            count = 0
            for team in teams:
                if (line % 2 == 0):
                    if dateidx < len(dates):
                        theDate = dates[dateidx].find(text=True)
                    else:
                        theDate = "?"
                    A.append(theDate)
                    if "January" not in theDate: 
                        Y.append(year)
                    else:
                        Y.append(year + 1)
                    B.append(pyBlitz.CleanString(team['title']))
                    if loop != len(pages):
                        if (neutral[count]['data-is-neutral-site'] == 'true'):
                            C.append("Neutral")
                        else:
                            C.append(pyBlitz.CleanString(team['title']))
                    else:
                        C.append("Neutral")
                    if (index < len(F)):
                        G.append(F[index])
                    else:
                        G.append("?")
                    count+=1
                    index+=1
                    IDX.append(index)
                else:
                    D.append(pyBlitz.CleanString(team['title']))
                line+=1
            dateidx+=1

        df=pd.DataFrame(IDX, columns=['Index'])
        df['Year']=Y
        df['Date']=A
        df['TeamA']=B
        df['Home']=C
        df['TeamB']=D
        df['Score']=G
        if (not df.empty):    
            filename = "{0}sched{1}.json".format(path, loop)
            with open(filename, 'w') as f:
                f.write(df.to_json(orient='index'))

            with open(filename) as sched_json:
                dict_sched = json.load(sched_json, object_pairs_hook=OrderedDict)

            filename = "{0}sched{1}.csv".format(path, loop)
            sched_sheet = open(filename, 'w', newline='')
            csvwriter = csv.writer(sched_sheet)
            count = 0
            for row in dict_sched.values():
                if (count == 0):
                    header = row.keys()
                    csvwriter.writerow(header)
                    count += 1
                csvwriter.writerow(row.values())
            sched_sheet.close()
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
