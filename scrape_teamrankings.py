#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import pdb
from collections import OrderedDict
import json
import csv
import contextlib
import os
import re
from pathlib import Path
import datetime
import glob

import settings
import pyBlitz

current_working_directory = os.getcwd()
year = 0
now = datetime.datetime.now()
year = int(now.year)
url = []
test_files = "{0}/test/pages/schedule/{1}/teamrankings*.html".format(current_working_directory, year)
url = glob.glob(test_files)

print ("Scrape Team Rankings Tool")
print ("**************************")
ratings_table = []
if not url:
    urls = []
    urls.append("https://www.teamrankings.com/college-football/stat/plays-per-game")
    urls.append("https://www.teamrankings.com/college-football/stat/points-per-play")
    urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-game")
    urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-play")
    test_mode=False
    print ("*** Live ***")
    for starturl in urls:
        print ("data is from {0}".format(starturl))
        with contextlib.closing(urlopen(starturl)) as page:
            soup = BeautifulSoup(page, "html5lib")
        ratings_table.append(soup.find('table', {"class":"tr-table datatable scrollable"}))
else:
    test_mode=True
    print ("*** Test data ***")
    print ("    data is from {0}/test/pages/schedule/{1}/".format(current_working_directory, year))
    print ("*** delete test data and re-run to go live ***")
    print("... fetching test teamrankings pages")
    for item in url:
        with open(item, 'r', encoding="windows-1252") as file:
            page = file.read().rstrip()
        soup= BeautifulSoup(page, "html5lib")
        ratings_table.append(soup.find('table', {"class":"tr-table datatable scrollable"}))
print ("Directory Location: {0}".format(settings.data_path))
print ("**************************")
IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
index=0
for row in ratings_table[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[1].find(string=True)!="Team":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[1].find(string=True)))
        B.append(col[3].find(string=True))
for team in A:
    for row in ratings_table[1].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            C.append(col[3].find(string=True))
            break
for team in A:
    for row in ratings_table[2].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            D.append(col[3].find(string=True))
            break
for team in A:
    for row in ratings_table[3].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            E.append(col[3].find(string=True))
            break

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
over=[]
for team in A:
    the_best = pyBlitz.GetFuzzyBest(team, matches, picked)
    abbrs.append(the_best[1])
    ratios.append(the_best[2])
    picked[the_best[0]] = " "
    over.append(" ")

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['PLpG3']=B
df['PTpP3']=C
df['OPLpG3']=D
df['OPTpP3']=E
df['abbr']=abbrs
df['confidence']=ratios
df['abbr override']=over

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'teamrankings.json', 'w') as f:
    f.write(df.to_json(orient='index'))

writer = pd.ExcelWriter(settings.data_path + "teamrankings.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
