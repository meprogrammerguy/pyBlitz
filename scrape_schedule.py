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
from datetime import datetime

import settings
import pyBlitz

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def GetScores(s):
    print (s)
    return 88, 89

year = 0
now = datetime.now()
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
    for page in pages:
        dates = page.findAll('div', attrs = {'class':'Table__Title'})
        tables = page.findAll('tbody', attrs = {'class':'Table__TBODY'})
        index = 0
        for lines in tables:
            rows = lines.findAll('tr')
            ROWS={}
            r_idx = 0
            for row in rows:
                cols = row.findAll('td')
                COLS={}
                c_idx = 0
                for col in cols:
                    COLS[c_idx] = col.text
                    c_idx+=1
                ROWS[r_idx] = COLS
                r_idx+=1
            SCHED[dates[index].text] = ROWS
            index+=1
            
    print("... retrieving teams JSON file")
    teams_excel = "{0}teams.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
    teams_json = json.loads(excel_df.to_json())
        
    matches={}
    matches["location"]=teams_json["location"]
    returned=teams_json["location"]

    index = 0
    IDX=[]
    cdate=[]
    teama=[]
    abbrev1=[]
    score1=[]
    where=[]
    teamb=[]
    abbrev2=[]
    score2=[]
    for dates in SCHED:
        for rows in SCHED[dates]:
            print(SCHED[dates][rows])
            #print(SCHED[dates][rows][0])
            the_best = pyBlitz.GetFuzzyBest(pyBlitz.CleanString(SCHED[dates][rows][0])[:10], matches, returned)
            #print ("team1: " + the_best[1])
            teama.append(the_best[1])
            #pdb.set_trace()
            abbrev1.append(teams_json["abbreviation"][the_best[0]])
            #pdb.set_trace()
            the_best = pyBlitz.GetFuzzyBest(pyBlitz.CleanString(SCHED[dates][rows][1])[2:12], matches, returned)
            #print ("team2: " + the_best[1])
            teamb.append(the_best[1])
            abbrev2.append(teams_json["abbreviation"][the_best[0]])
            cwhere = SCHED[dates][rows][1].partition("@")
            if cwhere[1]:
                where.append("Away")
            else:
                where.append("Neutral")
            t_score1, t_score2 = GetScores(SCHED[dates][rows][2])
            score1.append(t_score1)
            score2.append(t_score2)
            #pdb.set_trace()
            yyyy_date = pd.to_datetime(dates, errors='coerce')
            cdate.append(str(yyyy_date)[:10])
            index+=1
            IDX.append(index)
            #pdb.set_trace()
    #pdb.set_trace()
    
    print ("... creating sched JSON file")
    filename = "{0}sched.json".format(path)
    Path(path).mkdir(parents=True, exist_ok=True)
    df=pd.DataFrame(IDX, columns=['Index'])
    df['Date']=cdate
    df['Team 1']=teama
    df['Abbrev 1']=abbrev1
    df['Score 1']=score1
    df['Where']=where
    df['Team 2']=teamb
    df['Abbrev 2']=abbrev2
    df['Score 2']=score2

    with open(filename, 'w') as f:
        f.write(df.to_json(orient='index'))
    f.close()
    
    print ("... creating teams spreadsheet")
    excel_file = "{0}sched.xlsx".format(path)
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.close()

    for root, dirs, files in os.walk(settings.predict_root):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
