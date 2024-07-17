#!/usr/bin/env python3

import pdb
import requests
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
from collections import OrderedDict
import json
import csv
import re
from pathlib import Path
from xlsxwriter import Workbook
import os, sys, stat, time
import datetime
import glob

import settings
import pyBlitz

current_working_directory = os.getcwd()
year = 0
now = datetime.datetime.now()
year = int(now.year)

url = []
test_files = "{0}/test/pages/schedule/{1}/bornpowerindex*.html".format(current_working_directory, year)
url = glob.glob(test_files)

starturl = 'http://www.bornpowerindex.com/cgi-bin/DBRetrieve.pl'

print ("Scrape Born Power Index Tool")
print ("**************************")
if not url:
    test_mode=False
    print ("*** Live ***")
    print ("data is from http://www.bornpowerindex.com")
else:
    test_mode=True
    print ("*** Test data ***")
    print ("    data is from {0}/test/pages/schedule/{1}/".format(current_working_directory, year))
    print ("*** delete test data and re-run to go live ***")

print ("Directory Location: {0}".format(settings.data_path))
print ("**************************")

if not test_mode:
    data1 = {
        "getClassName": "on",
        "class": "1",
        "sort": "team"
    }

    data2 = {
        "getClassName": "on",
        "class": "2",
        "sort": "team"
    }

    data3 = {
        "getClassName": "on",
        "class": "3",
        "sort": "team"
    }
    
    data4 = {
        "getClassName": "on",
        "class": "4",
        "sort": "team"
    }

    data5 = {
        "getClassName": "on",
        "class": "5",
        "sort": "team"
    }

    data6 = {
        "getClassName": "on",
        "class": "6",
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
    r = requests.post(starturl, data=data1, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table1 = soup.findAll("table")

    r = requests.post(starturl, data=data2, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table2 = soup.findAll("table")

    r = requests.post(starturl, data=data3, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table3 = soup.findAll("table")

    r = requests.post(starturl, data=data4, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table4 = soup.findAll("table")

    r = requests.post(starturl, data=data5, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table5 = soup.findAll("table")

    r = requests.post(starturl, data=data6, headers=headers)
    soup = BeautifulSoup(r.content, "html5lib")
    table6 = soup.findAll("table")
else:
    print("... fetching test bornpowerindex pages")
    index = 0
    for item in url:
        with open(item, 'r', encoding="windows-1252") as file:
            page = file.read().rstrip()
        soup= BeautifulSoup(page, "html5lib")
        index+=1
        if index == 1:
            table1 = soup.findAll("table")
        if index == 2:
            table2 = soup.findAll("table")
        if index == 3:
            table3 = soup.findAll("table")
        if index == 4:
            table4 = soup.findAll("table")
        if index == 5:
            table5 = soup.findAll("table")
        if index == 6:
            table6 = soup.findAll("table")
Path(settings.data_path).mkdir(parents=True, exist_ok=True)

IDX=[]
A=[]
B=[]
C=[]
index=0
for row in table1[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table2[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table3[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table4[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table5[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table6[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
        
print("... retrieving teams spreadsheet, adding abbreviations")
teams_excel = "{0}teams.xlsx".format(settings.data_path)
excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
teams_json = json.loads(excel_df.to_json())

matches={}
matches["shortDisplayName"]=teams_json["shortDisplayName"]
matches["displayName"]=teams_json["displayName"]
matches["name"]=teams_json["name"]
matches["nickname"]=teams_json["nickname"]
matches["location"]=teams_json["location"]

picked=teams_json["abbreviation"]

abbrs=[]
ratios=[]
idx=0
for team in A:
    bclass = str(C[idx]).strip()
    if "DIVISION 1  FBS" in bclass:
        the_best = pyBlitz.GetFuzzyBest(team.lower()[:10], matches, picked)
        abbrs.append(the_best[1])
        ratios.append(the_best[2])
        picked[the_best[0]] = " "
    else:
        abbrs.append(" ")
        ratios.append(0)    
    idx+=1
    
#idx=0        
#for team in A:
    #bclass = str(C[idx]).strip()
    #if not "DIVISION 1  FBS" in bclass:
        #the_best = pyBlitz.GetFuzzyBest(team.lower()[:10], matches, picked)
        #abbrs.append(the_best[1])
        #ratios.append(the_best[2])
        #picked[the_best[0]] = " "
    #idx+=1

    #else:
        #the_best = pyBlitz.GetFuzzyBest(team.lower()[:10], matches, picked)
        #abbrs.append(" ")
        #ratios.append(0)
    #index+=1

#pdb.set_trace()

df=pd.DataFrame(IDX,columns=['Index'])
df['team']=A
df['abbr']=abbrs
df['class']=C
df['bpi']=B
df['confidence']=ratios

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'bornpowerindex.json', 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()

writer = pd.ExcelWriter(settings.data_path + "bornpowerindex.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
