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
import contextlib
import os, sys, stat, time
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

def SplitListInChunks(b, e, s, l):
    begin = b
    end = e
    step = s
    count=0
    c={}
    for y in range(begin, end, step): 
        x = y
        c[count]=l[x:x+step]
        count+=1
    return c
    
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
    test_files = "{0}/test/pages/schedule/{1}/odds.html".format(current_working_directory, year)
    url = glob.glob(test_files)

    starturl = "https://www.espn.com/college-football/odds"

    print ("Scrape Odds Tool")
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
    print ("Directory location: {0}".format(settings.data_path))
    print ("**************************")
    
    Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
    
    if not test_mode:
        url.append(starturl)   
        print("... fetching odds page")
        for item in url:
            req = Request(url=item, \
            headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
            try:
                page = urlopen(req)
            except HTTPError as e:
                page = pyBlitz.ErrorToJSON(e, url)
            pages.append(BeautifulSoup(page, "html5lib"))
    else:
        pages = []
        print("... fetching test schedule pages")
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)

    DATES=[]
    TEAMS={}
    LINES={}
    for page in pages:
        dates = page.findAll('div', attrs = {'class':'rIczU uzVSX avctS McMna WtEci pdYhu seFhp'})
        teams = page.findAll('div', attrs = {'class':'VZTD UeCOM rpjsZ ANPUN'})
        for i in dates:
            DATES.append(i.text)
        for i in range(len(teams)):
            LINES=teams[i].text.split()
            TEAMS[DATES[i]]=LINES

    print("... retrieving teams spreadsheet")
    teams_excel = "{0}teams.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
    teams_json = json.loads(excel_df.to_json())
        
    matches={}
    matches["displayName"]=teams_json["displayName"]
    returned=teams_json["displayName"]

    IDX=[]
    cdates=[]
    cteam1=[]
    cabbr1=[]
    cabbr2=[]
    the_line=[]
    CHUNKS={}
    index=0
    for cdate in TEAMS:
        print ("date: " + cdate)
        CHUNKS = SplitListInChunks(0, len(TEAMS[cdate]), 16, TEAMS[cdate])
        for item in CHUNKS:
            print (CHUNKS[item])
            pdb.set_trace()
           
    print ("... creating Odds JSON file")
    the_file = "{0}odds.json".format(settings.data_path)
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)
    df=pd.DataFrame(IDX,columns=['Index'])
    df['Date'] = cdates
    df['Team 1'] = cteam1
    
    with open(the_file, 'w') as f:
        f.write(df.to_json(orient='index'))
    f.close()
    
    print ("... creating odds spreadsheet")
    excel_file = "{0}odds.xlsx".format(settings.data_path)
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.close()

    for root, dirs, files in os.walk(settings.data_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
