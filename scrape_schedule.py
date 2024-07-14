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
            
    SCHED={}
    all_index = 0
    for page in pages:
        dates = page.findAll('div', attrs = {'class':'Table__Title'})
        tables = page.findAll('tbody', attrs = {'class':'Table__TBODY'})
        index = 0
        for lines in tables:
            #pdb.set_trace()
            cdate = dates[index].text
            rows = lines.findAll('tr')
            ROWS={}
            r_idx = 0
            for row in rows:
                cols = row.findAll('td')
                COLS={}
                c_idx = 0
                for col in cols:
                    print (col.text)
                    COLS[c_idx] = col.text
                    c_idx+=1
                    #pdb.set_trace()
                ROWS[r_idx] = COLS
                r_idx+=1
                #pdb.set_trace()
            #pdb.set_trace()
            #ROWS={}
            #for r_idx in range(len(rows)):
                #ROWS[r_idx] = rows[r_idx]
                #ROWS[r_idx] = rows
            #COLS={}
            #for c_idx in range(len(cols)):
                #COLS[c_idx] = cols[c_idx]
                #COLS[c_idx] = cols
            SCHED[cdate] = ROWS
            all_index+=1
            index+=1
    pdb.set_trace()
    index=0
    for loop in range(len(SCHED)):
        #print ("date: " + SCHED[loop][0])
        #print ("rows: " + str(len(SCHED[loop])))
        #pdb.set_trace()
        for row in range(len(SCHED[loop])):
            #print (len(SCHED[loop][row]))
            #print (SCHED[loop][row])
            #pdb.set_trace()
            for col in range(len(SCHED[loop][row])):
                print (len(SCHED[loop][row][col]))
                #print (SCHED[loop][row][col])
                pdb.set_trace()

        pdb.set_trace()
    pdb.set_trace()
    for root, dirs, files in os.walk(settings.predict_root):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
