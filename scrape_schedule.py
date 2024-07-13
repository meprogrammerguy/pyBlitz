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
import glob

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
current_working_directory = os.getcwd()

def main(argv):
    url = []
    test_files = "{0}/test/pages/schedule/{1}/w*.html".format(current_working_directory, year)
    url = glob.glob(test_files)

    starturl = "http://www.espn.com/college-football/schedule"
    path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

    print ("Scrape Schedule Tool")
    print ("**************************")
    if not url:
        test_mode=False
        print ("*** Live ***")
        print ("data is from {0}".format(starturl))
    else:
        test_mode=True
        print ("*** Test data ***")
        print ("    data is from {0}/test/pages/schedule/{1}/".format(current_working_directory, year))
        print ("*** delete test data and re-run to go live ***")
    print (" ")
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(path))
    print ("**************************")

    Path(path).mkdir(parents=True, exist_ok=True) 
    for p in Path(path).glob("sched*.*"):
        p.unlink()
        
    pages = []
    if not test_mode:
        url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))   
        if (year == int(now.year)):
            for week in range(1, 17):
                url.append("{0}/_/week/{1}/seasontype/2".format(starturl, week))
            url.append("{0}/_/week/1/seasontype/3".format(starturl))                
        else:
            for week in range(1, 17):
                url.append("{0}/_/week/{1}/year/{2}/seasontype/2".format(starturl, week, year))
            url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))   
            
        print("... fetching schedule pages")
        for item in url:
            req = Request(url=item, \
                headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
            try:
                page = urlopen(req)
            except HTTPError as e:
                page = pyBlitz.ErrorToJSON(e, url)
            pages.append(BeautifulSoup(page, "html5lib"))
    else:
        
        print("... fetching test schedule pages")
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
            
    pdb.set_trace()
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
                        try:
                            if (neutral[count]['data-is-neutral-site'] == 'true'):
                                C.append("Neutral")
                            else:
                                C.append("?")
                        except KeyError as e:
                            C.append("Neutral")
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
                    if (C[-1] == '?'):
                        C[-1] = D[-1] 
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
    for root, dirs, files in os.walk(settings.predict_root):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
