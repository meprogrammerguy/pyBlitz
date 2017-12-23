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

year = 0
now = datetime.datetime.now()
if (len(sys.argv)==1):
    year = int(now.year)
elif (len(sys.argv)==2):
    year = int(sys.argv[1])
    if (year < 100):
        year += 2000
else:
    print ("???")
    print ("error, usage: no arg is current year, 1 arg is year to scrape (like this)")
    print ("./scrape_schedule.py")
    print ("./scrape_schedule.py 2016")
    print ("???")
    sys.exit("error: incorrect number of arguments")

starturl = "http://www.espn.com/college-football/schedule"

print ("Scrape Schedule Tool")
print ("**************************")
print ("data is from {0}".format(starturl))
print
print ("Year is: {0}".format(year))
print ("**************************")

url = []
if (year == int(now.year)):
    url.append("{0}/_/seasontype/2".format(starturl))
    for week in range(2, 16):
        url.append("{0}/_/week/{1}/seasontype/2".format(starturl, week))
    url.append(starturl)       
else:
    url.append("{0}/_/year/{1}/seasontype/2".format(starturl, year))
    for week in range(2, 16):
        url.append("{0}/_/week/{1}/year/{2}/seasontype/2".format(starturl, week, year))        
    url.append("{0}/_/year/{1}".format(starturl, year))        

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
    A=[]
    B=[]
    C=[]
    D=[]
    for table in tables:
        #print (dates[dateidx].find(text=True))
        teams=table.findAll('abbr')
        home=table.findAll('td', {"class": "home"})
        scores=table.findAll('td')
        neutral=table.findAll('tr', {'class':['odd', 'even']})
        line = 0
        count = 0
        for team in teams:
            if (line % 2 == 0):
                if dateidx < len(dates):
                    A.append(dates[dateidx].find(text=True))
                else:
                    A.append("?")
                #print (team['title'])
                B.append(team['title'])
                if loop == len(pages) and dateidx == 5:
                    pdb.set_trace()
                #pdb.set_trace()
                if loop != len(pages):
                    if (neutral[count]['data-is-neutral-site'] == 'true'):
                        C.append("Neutral")
                    else:
                        C.append(team['title'])
                #print (home[count].div['data-home-text'])
                #print (neutral[count]['data-is-neutral-site'])
                count+=1
                index+=1
                IDX.append(index)
            else:
                #print (team['title'])
                D.append(team['title'])
            line+=1
        dateidx+=1
    if loop == len(pages):
        pdb.set_trace()
    df=pd.DataFrame(IDX, columns=['Index'])
    df['Date']=A
    df['TeamA']=B
    if C:
        df['Home']=C
    df['TeamB']=D
    
    filename = "week{0}.json".format(loop)
    with open(filename, 'w') as f:
        f.write(df.to_json(orient='index'))

    with open(filename) as sched_json:
        dict_sched = json.load(sched_json, object_pairs_hook=OrderedDict)

    filename = "week{0}.csv".format(loop)
    sched_sheet = open(filename, 'w', newline='')
    csvwriter = csv.writer(sched_sheet)
    count = 0
    for row in dict_sched.values():
        if (count == 0):
            header = row.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(row.values())
    #pdb.set_trace()
    sched_sheet.close()
print ("done.")


