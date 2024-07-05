#!/usr/bin/env python3

from urllib.request import urlopen
from urllib.request import HTTPError
from urllib.request import Request

from bs4 import BeautifulSoup
import re
import pandas as pd
import html5lib
import pdb
import json
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
    url = glob.glob("/home/jsmith/git/pyBlitz/test/pages/schedule/{0}/*.txt".format(year))
    if not url:
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
            req = Request(url=item, \
                          headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
            try:
                page = urlopen(req)
            except HTTPError as e:
                page = e.read()
            pages.append(BeautifulSoup(page, "html5lib"))
    else:
        pages = []
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)

    index = 0
    A=[]
    B=[]
    C=[]
    D=[]
    E=[]
    F=[]
    G=[]
    H=[]
    I=[]
    J=[]
    K=[]
    for page in pages:
        body = page.findAll('body')
        names = page.findAll('span', attrs = {'class':'Table__Team'})
        names2 = page.findAll('div', attrs = {'class':'Table__Team'})
        tdates = page.findAll('div', attrs = {'class':'Table__Title'})
        titles = page.findAll('th', attrs = {'class':'Table__TH'})
        tbodys = page.findAll('tbody', attrs = {'class':'Table__TBODY'})
        #the_links = page.findAll('div', text="Link")
        for name in names:
            A.append(pyBlitz.CleanString(name.text).split())
            J.append(name) # get IDs from here too
        for title in titles:
            B.append(title.text)
        for tbody in tbodys:
            C.append(tbody)
            # (C[0].td.a) gives me team id
            a_texts = tbody.findAll('a')
            for a_text in a_texts:
                G.append(a_text)
            D.append(tbody.text)
        for ids in C:
            H.append(ids.td.a)
        #pdb.set_trace()
        for tdate in tdates:
            E.append(tdate)
            F.append(tdate.text)
    new_items = []
    for items in A:
        new_items.append([item for item in items if not item.isdigit()])
    A = []
    for item in new_items:
        the_string = ""
        for piece in item:
            the_string = the_string + piece + " "
        A.append(the_string[:-1])
    A = list(set(A))
    H = list(set(H))
    J = list(set(J))
    #       (Pdb) print (G[4].text)
    #               OHIO 41, GASO 21
    #       the step is 8: 4, 12, 20 ...
    #
    #       [start:stop:step]
    # mylist = [1,2,3,4,5,6,7,8,9,10]
    # for i in mylist[::2]:
    #   print i,
    # prints 1 3 5 7 9

for i in mylist[1::2]:
    print i,
# prints 2 4 6 8 10
    pdb.set_trace()
    # use the Team vs team and pull up the json for each Then properly fill out the spreadsheet
    the_api = []
    for item in A:
        the_api.append("https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/" + item)
    # J has the https page 
    # for H pull out id from pattern _/id/2050/
    pdb.set_trace()
    # https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/alabama
    # https://www.espn.com/college-football/team/_/id/103 Boston College get the ID into the spreadsheet
    # https://www.espn.com/college-football/team/_/id/333
    # go to team page, J has it, then click on schedule (to get the ID) <==
    dct = {#'ID': {0: 23, 1: 43, 2: 12,  
              #3: 13, 4: 67, 5: 89,  
              #6: 90, 7: 56, 8: 34}, 
      'Team': {0: A[0], 1: A[1]},  
      'espn API': {0: the_api[0], 1: the_api[1]}
    }  
    # forming dataframe 
    #   data = pd.DataFrame(dct)  
  
    # storing into the excel file 
    #   data.to_excel("output.xlsx")
    
    #df = pd.DataFrame([A[0], the_api[0]], columns=["Team", "espn API"])  
    df = pd.DataFrame(dct) 
    excel_file = settings.data_path + "abbreviation.xlsx"  
    df.to_excel(excel_file, index=False) 
 
    for root, dirs, files in os.walk(settings.data_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
