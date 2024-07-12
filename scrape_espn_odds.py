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

def SplitListInChunks(e, s, l):
    begin = 0
    end = e
    step = s
    count=0
    c={}
    for y in range(begin, end, step): 
        x = y
        c[count]=l[x:x+step]
        count+=1
    return c

def flatten(xss):
    return [x for xs in xss for x in xs]

def FirstUpper(s1):
    m = re.search("[A-Z]", s1)
    return m.start()

def ParseOddsStringToList(c, i, s):
    fields=[]
    returns={}
    #
    # field 1 time: "12:00 PM" end of parse is an: "O"
    #
    index=0
    left_text = s[index:].partition("O")
    fields.append(left_text[0])
    index+=len(left_text[0])
    print ("***")
    print ("count: " + str(c))
    print ("index start: " + str(i))
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
    left_text = s[index:].replace("(OH)", "").replace("(PA)", "").partition("(")
    fields.append(left_text[0])
    index+=len(left_text[0])
    print ("field 6: " + fields[5])
    #
    # field 7 (0-0) end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 7: " + fields[6])
    #
    # field 8 Home/Away end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 8: " + fields[7])
    #
    # field 9 odds end of parse is first uppercase word
    #
    idx_f = FirstUpper(s[index:].replace("OFF", "off"))
    fields.append(s[index:index+idx_f])
    index+=(idx_f)
    print ("field 9: " + fields[8])
    #
    # field 10 Team 2 name end of parse is a: "("
    #
    left_text = s[index:].replace("(OH)", "").replace("(PA)", "").partition("(")
    fields.append(left_text[0])
    index+=len(left_text[0])
    print ("field 10: " + fields[9])
    #
    # field 11 (0-0) end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 11: " + fields[10])
    #
    # field 12 Home/Away end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields.append(left_text)
    index+=len(left_text)
    print ("field 12: " + fields[11])
    #
    # field 13 odds end of parse is a: ":" and back off 2
    #
    left_text = s[index:].replace("OFF", "off").replace("TBD", "??:?? AM").partition(":")
    if left_text[1]:
        t_number=left_text[0][-2]
        if t_number == "1" or (t_number == "?"):
            fields.append(left_text[0][:-2])
            index+=len(left_text[0][:-2])
        else:
            fields.append(left_text[0][:-1])
            index+=len(left_text[0][:-1])
    else:
        fields.append(s[index:])
        index+=len(s[index:]) 
    print ("field 13: " + fields[12])
    print (" index end: " + str(index))
    print ("***")
    returns["list"]=fields
    returns["index"]=index
    returns["chunks"]=len(fields)
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
    chunks=0
    count=0
    for page in pages:
        dates = page.findAll('div', attrs = {'class':'rIczU uzVSX avctS McMna WtEci pdYhu seFhp'})
        teams = page.findAll('div', attrs = {'class':'VZTD UeCOM rpjsZ ANPUN'})
        for i in dates:
            DATES.append(i.text)
        for i in range(len(teams)):
            idx = 0
            returns={}
            LINES=[]
            while idx < len(teams[i].text):
                returns = ParseOddsStringToList(count, idx, teams[i].text[idx:])
                count+=1
                idx+=returns["index"]
                chunks=returns["chunks"]
                LINES.append(returns["list"])
            
            flat=[]
            flat = flatten(LINES)
            TEAMS[DATES[i]]=flat

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
    codds1=[]
    cteam2=[]
    codds2=[]
    cwhere=[]
    ctime=[]
    index=0
    for cdate in TEAMS:
        CHUNKS={}
        CHUNKS = SplitListInChunks(len(TEAMS[cdate]), chunks, TEAMS[cdate])
        for item in CHUNKS:
            if "Away" in CHUNKS[item][7]:
                cwhere.append("away")
            else:
                if "Home" in CHUNKS[item][7]:
                    cwhere.append("home")
                else:
                    cwhere.append("neutral") 
                    
            team1 = CHUNKS[item][5]
            the_best = pyBlitz.GetFuzzyBest(team1, matches, returned)
            cteam1.append(the_best[1])
            
            team2 = CHUNKS[item][9]
            the_best = pyBlitz.GetFuzzyBest(team2, matches, returned)
            cteam2.append(the_best[1])
            
            ctime.append(CHUNKS[item][0])
            codds1.append(CHUNKS[item][8])
            codds2.append(CHUNKS[item][12])
            cdates.append(cdate)
            index+=1
            IDX.append(index)
    
    print ("... creating Odds JSON file")
    the_file = "{0}odds.json".format(settings.data_path)
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)
    df=pd.DataFrame(IDX,columns=['Index'])
    df['Date'] = cdates
    df['Time'] = ctime
    df['Where'] = cwhere
    df['Team 1'] = cteam1
    df['Odds 1'] = codds1
    df['Team 2'] = cteam2
    df['Odds 2'] = codds2

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
