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
    the_max=-1
    best={}
    for item in m:
        print (m[str(item)])
        #pdb.set_trace()
        ratio = fuzz.ratio(t, m[str(item)])
        print (ratio)
        if the_max < ratio:
            the_max = ratio
            print ("item: " + str(item))
            print ("unpicked: " + u[str(item)])
            print ("ratio: " + str(ratio))
            print ("max: " + str(the_max))
            best = item, m[str(item)], u[str(item)], the_max
            print (best)
            #pdb.set_trace()
        #u[str(item)] = " "
        print ("team: " + t)
        print ("best: " + str(best))
        #pdb.set_trace()
    #pdb.set_trace()
    #print ("best: " + str(best))
    #print (str(best[2]))
    #print (str(best[3]))
    #print (str(item))
    #pdb.set_trace()
    return best

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

print("... retrieving teams spreadsheet")
teams_excel = "{0}teams.xlsx".format(settings.data_path)
excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
teams_json = json.loads(excel_df.to_json())

unpicked = teams_json["abbreviation"]
#matches = teams_json["shortDisplayName"] 88% (wrong)
matches = teams_json["displayName"] # 64% (correct)
#matches = teams_json["name"] 44% (wrong)
#matches = teams_json["nickname"] 88% (wrong)
#matches = teams_json["location"] 88% (wrong)

#print (unpicked)
abbrs=[]
ratios=[]
for team in A:
    #pdb.set_trace()
    the_best = GetFuzzyBest(team, matches, unpicked)
    unpicked[str(the_best[0])] = " "
    print (str(the_best))
    abbrs.append(str(the_best[2]))
    ratios.append(str(the_best[3]))
    #pdb.set_trace()
#pdb.set_trace()
#unpicked = []
#for element in teams_json:
    #print (teams_json[element]["abbreviation"])
    #print (picked["1"])
 #   pdb.set_trace()

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['PLpG3']=B
df['PTpP3']=C
df['OPLpG3']=D
df['OPTpP3']=E
df['abbreviation']=abbrs
df['confidence']=ratios
 
Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'teamrankings.json', 'w') as f:
    f.write(df.to_json(orient='index'))

writer = pd.ExcelWriter(settings.data_path + "teamrankings.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
