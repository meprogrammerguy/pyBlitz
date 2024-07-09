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
from thefuzz import fuzz
from thefuzz import process

import settings
import pyBlitz

def GetFuzzyBest(t, m, u):
    item=[]
    best_lists={}
    for item in m:
        best=""
        the_max=-1
        matches=m[item]
        for i in matches:
            match = matches[i]
            abbr = u[i]
            ratio = fuzz.ratio(t, match)
            if abbr == "zzzz":
                ratio = 0
            if the_max < ratio:
                the_max = ratio
                best = i, t, match, abbr, the_max
            best_lists[item] = best
    the_best={}
    for item in best_lists:
        best=""
        the_max=-1
        ratio = best_lists[item][4]
        abbr = best_lists[item][3]
        index = best_lists[item][0]
        if abbr == "zzzz":
            ratio = 0
        if the_max < ratio:
            the_max = ratio
            best = index, item, abbr, the_max
        the_best[t]=best
    u[the_best[t][0]] = "zzzz"
    return the_best[t][0], the_best[t][2], the_best[t][3]

urls = []
urls.append("https://www.teamrankings.com/college-football/stat/plays-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/points-per-play")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-play")

print ("Scrape Team Rankings Tool")
print ("**************************")
ratings_table = []
for url in urls:
    print ("data is from {0}".format(url))
    with contextlib.closing(urlopen(url)) as page:
        soup = BeautifulSoup(page, "html5lib")
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

abbrs=[]
ratios=[]
over=[]
for team in A:
    the_best = GetFuzzyBest(team, matches, teams_json["abbreviation"])
    abbrs.append(the_best[1])
    ratios.append(the_best[2])
    over.append(" ")

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['PLpG3']=B
df['PTpP3']=C
df['OPLpG3']=D
df['OPTpP3']=E
df['abbr guess']=abbrs
df['confidence']=ratios
df['abbr override']=over

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'teamrankings.json', 'w') as f:
    f.write(df.to_json(orient='index'))

writer = pd.ExcelWriter(settings.data_path + "teamrankings.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
