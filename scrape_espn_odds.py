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

def FirstUpper(s1):
    #s1 = "asdfasdfasdfasdfasdfASDFASDFASDF"
    m = re.search("[A-Z]", s1)
    #if m:
        #print ("Upper Case at position {0}".format(m.start()))
    #else:
        #print ("No Upper Case in that string")
    return m.start()

def ParseOddsStringToList(s):
    fields=[]
    returns={}
    #
    # field 1 time: "12:00 PM"  (length 8)
    #
    index=0
    fields.append(s[:8])
    index+=8
    print ("***")
    print ("field 1: " + fields[0])
    #
    # field 2 "Open"  (length 4)
    #
    fields.append(s[index:index+4])
    index+=4
    print ("field 2: " + fields[1])
    #
    # field 3 "Spread"  (length 6)
    #
    fields.append(s[index:index+6])
    index+=6
    print ("field 3: " + fields[2])
    #
    # field 4 "Total"  (length 5)
    #
    fields.append(s[index:index+5])
    index+=5
    print ("field 4: " + fields[3])
    #
    # field 5 "ML"  (length 2)
    #
    fields.append(s[index:index+2])
    index+=2
    print ("field 5: " + fields[4])
    #
    # field 6 Team 1 name end of parse is a: "("
    #
    left_text = s[index:len(s)].partition("(")[0]
    fields.append(left_text)
    index+=len(left_text)
    print ("field 6: " + fields[5])
    #
    # field 7 (0-0) end of parse is a: ")"
    #
    left_text = s[index:len(s)].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 7: " + fields[6])
    #
    # field 8 Home/Away end of parse is a: ")"
    #
    left_text = s[index:len(s)].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 8: " + fields[7])
    #
    # field 9 odds end of parse is an uppercase letter
    #
    idx_f = FirstUpper(s[index:len(s)])
    #pdb.set_trace()
    fields.append(s[index:index+idx_f])
    index+=idx_f
    print ("field 9: " + fields[8])
    #
    # field 10 Team 2 name end of parse is a: "("
    #
    left_text = s[index:len(s)].partition("(")[0]
    fields.append(left_text)
    index+=len(left_text)
    print ("field 10: " + fields[9])
    #
    # field 11 (0-0) end of parse is a: ")"
    #
    left_text = s[index:len(s)].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 11: " + fields[10])
    #
    # field 12 Home/Away end of parse is a: ")"
    #
    left_text = s[index:len(s)].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 12: " + fields[11])
    #
    # field 13 odds end of parse is a: ":" and back off 2
    #
    left_text = s[index:len(s)].partition(":")[0]
    fields.append(left_text[:-2])
    index+=(len(left_text) - 2)
    print ("field 13: " + fields[12])
    print ("***")
    #pdb.set_trace()
    returns["list"]=fields
    returns["index"]=index
    returns["slice"]=len(fields)
    return returns

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
    #LINES={}
    for page in pages:
        dates = page.findAll('div', attrs = {'class':'rIczU uzVSX avctS McMna WtEci pdYhu seFhp'})
        teams = page.findAll('div', attrs = {'class':'VZTD UeCOM rpjsZ ANPUN'})
        for i in dates:
            DATES.append(i.text)
        for i in range(len(teams)):
            print ("Date: " + DATES[i])
            print ("Line: " + teams[i].text)
            returns={}
            returns = ParseOddsStringToList(teams[i].text)
            print (returns)
            pdb.set_trace()

            #LINES=teams[i].text.split()
            #LINES=teams[i].text
            #TEAMS[DATES[i]]=LINES

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
    cteam2=[]
    CHUNKS={}
    index=0
    for cdate in TEAMS:
        print ("date: " + cdate)
        print ("TEAMS[cdate]: " + str(TEAMS[cdate]))
        #returns={}
        #returns = ParseOddsStringToList(TEAMS[cdate])
        pdb.set_trace()
        CHUNKS = SplitListInChunks(0, len(TEAMS[cdate]), 16, TEAMS[cdate])
        pdb.set_trace()
        for item in CHUNKS:
            print (CHUNKS[item])
            pdb.set_trace()
            team1 = TEAMS[cdate][item+1] + " " + TEAMS[cdate][item+2] + " " + TEAMS[cdate][item+3]
            #team1 = team1.replace('PMOpenSpreadTotalML', '')
            the_best = pyBlitz.GetFuzzyBest(team1, matches, returned)
            print ("team 1: " + team1)
            print ("the_best: " + str(the_best))
            cteam1.append(the_best[1])
            #pdb.set_trace()
            team2 = TEAMS[cdate][item+6] + " " + TEAMS[cdate][item+7] + " " + TEAMS[cdate][item+8]
            #team2 = team2.replace('PMOpenSpreadTotalML', '')
            the_best = pyBlitz.GetFuzzyBest(team2, matches, returned)
            print ("team 2: " + team2)
            print ("the_best: " + str(the_best))
            pdb.set_trace()
            cteam2.append(the_best[1])
            cdates.append(cdate)
            index+=1
            IDX.append(index)
            #pdb.set_trace()
        #pdb.set_trace()
    #pdb.set_trace()
          
    print ("... creating Odds JSON file")
    the_file = "{0}odds.json".format(settings.data_path)
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)
    df=pd.DataFrame(IDX,columns=['Index'])
    df['Date'] = cdates
    df['Team 1'] = cteam1
    df['Team 2'] = cteam2
    
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
