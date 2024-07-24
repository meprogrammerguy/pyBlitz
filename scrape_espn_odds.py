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

def FirstUpper(s1):
    m = re.search("[A-Z]", s1)
    return m.start()

def SplitOdds(l):
    p_l = l.replace("o", " o")
    p_l = p_l.replace("u", " u")
    p_l = p_l.replace("-", " -")
    p_l = p_l.replace("+", " +")
    p_l = p_l.replace("OFF", " OFF")
    p_l = p_l.replace("EVEN", " EVEN")
    o_list=p_l.split()
    return len(o_list), o_list

def ParseOddsStringToList(i, s):
    fields={}
    returns={}
    #
    # field 1 time: "12:00 PM" end of parse is an: "O"
    #
    index=0
    left_text = s[index:].partition("O")
    fields["time"] = s[index:index+len(left_text[0])]
    index+=len(left_text[0])
    #print ("***")
    #print ("index start: " + str(i))
    #print ("field 1: " + fields["time"])
    #
    # field 2 "Open"  (length 4)
    #
    fields["open"] = s[index:index+4]
    index+=4
    #print ("field 2: " + fields["open"])
    #
    # field 3 "Spread"  (length 6)
    #
    fields["spread"] = s[index:index+6]
    index+=6
    #print ("field 3: " + fields["spread"])
    #
    # field 4 "Total"  (length 5)
    #
    fields["total"] = s[index:index+5]
    index+=5
    #print ("field 4: " + fields["total"])
    #
    # field 5 "ML"  (length 2)
    #
    fields["ml"] = s[index:index+2]
    index+=2
    #print ("field 5: " + fields["ml"])
    #
    # field 6 Team 1 name end of parse is a: "("
    #
    left_text = s[index:].replace("(OH)", "").replace("(PA)", "").partition("(")
    fields["team1"] = left_text[0]
    index+=len(left_text[0])
    #print ("field 6: " + fields["team1"])
    #
    # field 7 (0-0) end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields["scores1"] = s[index:index+len(left_text)]
    index+=len(left_text)
    #print ("field 7: " + fields["scores1"])
    #
    # field 8 Home/Away end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields["where1"] = s[index:index+len(left_text)]
    index+=len(left_text)
    #print ("field 8: " + fields["where1"])
    #
    # field 9 odds end of parse is first uppercase word
    #
    idx_f = FirstUpper(s[index:].replace("OFF", "off"))
    fields["odds1"] = s[index:index+idx_f]
    index+=(idx_f)
    odds_count, odds_list = SplitOdds(fields["odds1"])
    fields["odds1"] = odds_list
    #print ("field 9: " + str(fields["odds1"]))
    #
    # field 10 Team 2 name end of parse is a: "("
    #
    left_text = s[index:].replace("(OH)", "").replace("(PA)", "").partition("(")
    fields["team2"] = left_text[0]
    index+=len(left_text[0])
    #print ("field 10: " + fields["team2"])
    #
    # field 11 (0-0) end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields["scores2"] = s[index:index+len(left_text)]
    index+=len(left_text)
    #print ("field 11: " + fields["scores2"])
    #
    # field 12 Home/Away end of parse is a: ")"
    #
    left_text = s[index:].partition(")")[0]
    left_text = left_text + ")"
    fields["where2"] = s[index:index+len(left_text)]
    index+=len(left_text)
    #print ("field 12: " + fields["where2"])
    #
    # field 13 odds end of parse is a: ":" and back off 2
    #
    left_text = s[index:].replace("OFF", "off").replace("TBD", "??:?? AM").partition(":")
    if left_text[1]:
        t_number=left_text[0][-2]
        if t_number == "1" or (t_number == "?"):
            t_idx = len(left_text[0][:-2])
            fields["odds2"] = s[index:index+t_idx]
            index+= t_idx
        else:
            t_idx = len(left_text[0][:-1])
            fields["odds2"] = s[index:index+t_idx]
            index+=t_idx
    else:
        fields["odds2"] = s[index:]
        index+=len(s[index:]) 
    odds_count, odds_list = SplitOdds(fields["odds2"])
    fields["odds2"] = odds_list
    #print ("field 13: " + str(fields["odds2"]))
    #print ("odds_count: " + str(odds_count))
    #print ("odds_list: " + str(odds_list))
    #print (" index end: " + str(index))
    #print ("***")
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
        print ("    data is from {0}test/pages/schedule/{1}/".format(current_working_directory, year))
        print ("*** delete test data and re-run to go live ***")
    print (" ")
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(settings.data_path))
    print ("**************************")
    
    Path(settings.data_path).mkdir(parents=True, exist_ok=True) 

    pages = []
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
        print("... fetching test odds page")
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)

    DATES=[]
    TEAMS={}
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
                returns = ParseOddsStringToList(idx, teams[i].text[idx:])
                idx+=returns["index"]
                LINES.append(returns["list"])
            TEAMS[DATES[i]]=LINES

    print("... retrieving teams JSON file")
    teams_excel = "{0}teams.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
    teams_json = json.loads(excel_df.to_json())
        
    matches={}
    matches["displayName"]=teams_json["displayName"]
    returned=teams_json["displayName"]

    IDX=[]
    cdates=[]
    cteam1=[]
    cspread1=[]
    cteam2=[]
    cspread2=[]
    cwhere=[]
    ctime=[]
    chance1=[]
    chance2=[]
    index=0
    for cdate in TEAMS:
        for item in TEAMS[cdate]:
            if "Away" in item["where1"]:
                cwhere.append("Away")
            else:
                if "Home" in item["where1"]:
                    cwhere.append("Home")
                else:
                    cwhere.append("Neutral") 

            the_best = pyBlitz.GetFuzzyBest(item["team1"], matches, returned)
            cteam1.append(the_best[1])
            cspread1.append(item["odds1"][2])
            chance1.append(pyBlitz.GetChance(item["odds1"][2])["answer"] + "%")
            
            the_best = pyBlitz.GetFuzzyBest(item["team2"], matches, returned)
            cteam2.append(the_best[1])
            cspread2.append(item["odds2"][0])
            chance2.append(pyBlitz.GetChance(item["odds2"][0])["answer"] + "%")

            ctime.append(item["time"])
            y_date = cdate + ", " + str(year)
            yyyy_date = pd.to_datetime(y_date, errors='coerce')
            cdates.append(str(yyyy_date)[:10])
            index+=1
            IDX.append(index)
    
    df=pd.DataFrame(IDX,columns=['Index'])
    df['Date'] = cdates
    df['Time'] = ctime
    df['Where'] = cwhere
    df['Team 1'] = cteam1
    df['Spread 1'] = cspread1
    df['Chance 1'] = chance1
    df['Team 2'] = cteam2
    df['Spread 2'] = cspread2
    df['Chance 2'] = chance2

    print ("... creating odds JSON file")
    the_file = "{0}json/odds.json".format(settings.data_path)
    the_path = "{0}json/".format(settings.data_path)
    Path(the_path).mkdir(parents=True, exist_ok=True)
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
