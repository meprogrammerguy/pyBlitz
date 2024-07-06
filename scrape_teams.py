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

def ErrorToJSON(e, y):
    s = str(e)
    x = '"message": "{0}", "file": "{0}"'.format(s, y)
    x = "<http>{" + x + "}</http>"
    return x

year = 0
now = datetime.datetime.now()
year = int(now.year)
if (len(sys.argv)>=2):
    year = GetNumber(sys.argv[1])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)
year -= 1
current_working_directory = os.getcwd()

def main(argv):
    url = []
    test_files = "{0}/test/pages/schedule/{1}/*.html".format(current_working_directory, year)
    url = glob.glob(test_files)

    starturl = "http://www.espn.com/college-football/schedule"

    print ("Scrape Teams Tool")
    print ("**************************")
    if not url:
        print ("*** Live ***")
        print ("data is from {0}".format(starturl))
    else:
        print ("*** Test data ***")
        print ("    data is from {0}/test/pages/schedule/{1}/".format(current_working_directory, year))
        print ("*** delete test data and re-run to go live ***")
    print (" ")
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(settings.data_path))
    print ("**************************")
    
    now_time = str(now).split(".")[0]
    print (now_time)

    excel_file = "{0}teams.xlsx".format(settings.data_path)
    spreadsheet=False
    if Path(excel_file).is_file():
        print("... retrieving teams spreadsheet")
        excel_df = pd.read_excel(excel_file, sheet_name='Sheet1')
        teams_json = json.loads(excel_df.to_json())
        spreadsheet=True
        if teams_json["created"]["0"] is None:
            spreadsheet=False
        else:
            print(" ")
            print ("        spreadsheet created date shows: " + teams_json["created"]["0"])
                
    if spreadsheet:
        print(" ")
        print("===      To recreate: edit {0} and blank out the creation date, and rerun scraper ===".format(excel_file))
        print(" ")
        print ("done.")
        sys.exit()
    Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
    
    if not url:
        url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))   
        if (year == int(now.year)):
            for week in range(1, 17):
                url.append("{0}/_/week/{1}/seasontype/2".format(starturl, week))
            url.append("{0}/_/week/1/seasontype/3".format(starturl))                
        else:
            for week in range(1, 17):
                url.append("{0}/_/week/{1}/year/{2}/seasontype/2".format(starturl, week, year))
            url.append("{0}/_/week/1/year/{1}/seasontype/3".format(starturl, year))
        pages = []
        print("... fetching schedule pages")
        for item in url:
            req = Request(url=item, \
            headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
            try:
                page = urlopen(req)
            except HTTPError as e:
                page = ErrorToJSON(e, url)
            pages.append(BeautifulSoup(page, "html5lib"))
    else:
        pages = []
        print("... fetching test schedule pages")
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)

    ABBR=[]

    for page in pages:
        tbodys = page.findAll('tbody', attrs = {'class':'Table__TBODY'})
        for tbody in tbodys:
            a_texts = tbody.findAll('a')
            for a_text in a_texts:
                ABBR.append(a_text)
           
    abbrev=[]
    for items in ABBR[4::8]:
        the_list=items.text.replace(',', '').split()
        for each_one in the_list[:4:2]:
            if not each_one.isdigit():
                abbrev.append(each_one)
    abbrev = list(set(abbrev))
    
    pages = []
    print("... fetching from espn API, saving locally")
    for item in abbrev:
        url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{0}".format(item)
        req = Request(url=url, \
        headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        try:
            page = urlopen(req)
        except HTTPError as e:
            page = ErrorToJSON(e, url)
        soup = BeautifulSoup(page,"html5lib")

        the_file = "{0}abbrev/{1}.json".format(settings.data_path, item.lower())
        the_path = "{0}abbrev".format(settings.data_path)
        Path(the_path).mkdir(parents=True, exist_ok=True)
        with open(the_file, 'w') as f:
            f.write(soup.text)
        f.close()
        pages.append(soup)

    pages=[]
    print("... retrieving espn API files locally")
    for item in abbrev:
        the_file = "{0}abbrev/{1}.json".format(settings.data_path, item.lower())
        with open(the_file, 'r') as file:
            data = file.read()
            pages.append(json.loads(data))
        file.close()

    id=[]
    abbreviation=[]
    shortDisplayName=[]
    displayName=[]
    name=[]
    nickname=[]
    location=[]
    standingSummary=[]
    for page in pages:
        if "team" in page:
            team = page["team"]
        else:
            team = page
        if "code" in team:
            print ("error code: {0}".format(team["code"]))
            if "message" in team:
                print ("    message: {0}".format(team["message"]))
            if "file" in team:
                print ("    in file: {0}".format(team["file"]))
            print ("... skipping")
            continue
        if "id" in team:
            id.append(team["id"])                    
        if "abbreviation" in team:
            abbreviation.append(team["abbreviation"])
        if "shortDisplayName" in team:
            shortDisplayName.append(pyBlitz.CleanString(team["shortDisplayName"]))
        if "displayName" in team:
            displayName.append(pyBlitz.CleanString(team["displayName"]))
        if "name" in team:
            name.append(pyBlitz.CleanString(team["name"]))
        if "nickname" in team:
            nickname.append(pyBlitz.CleanString(team["nickname"]))
        if "location" in team:
            location.append(pyBlitz.CleanString(team["location"]))
        if "standingSummary" in team:
            standingSummary.append(pyBlitz.CleanString(team["standingSummary"]))

    ids={}
    abbreviations={}
    shortDisplayNames={}
    displayNames={}
    names={}
    nicknames={}
    locations={}
    standingSummarys={}
    for i in range(len(id)):
        ids.update({i:id[i]}) 
        abbreviations.update({i:abbreviation[i]}) 
        shortDisplayNames.update({i:shortDisplayName[i]}) 
        displayNames.update({i:displayName[i]}) 
        names.update({i:name[i]}) 
        nicknames.update({i:nickname[i]}) 
        locations.update({i:location[i]})
        if i < len(standingSummary):
            standingSummarys.update({i:standingSummary[i]})
    
    rows={'created': {0: now_time}}
    rows.update({"id":ids})
    rows.update({"abbreviation":abbreviations}),
    rows.update({"shortDisplayName":shortDisplayNames})
    rows.update({"displayName":displayNames})
    rows.update({"name":names})
    rows.update({"nickname":nicknames})
    rows.update({"location":locations})
    rows.update({"standingSummary":standingSummarys})
    
    print ("... creating teams spreadsheet")
    df = pd.DataFrame(rows)    
    df.to_excel(excel_file, index=False) 
 
    print ("... creating teams JSON file")
    excel_df = pd.read_excel(excel_file, sheet_name='Sheet1')
    json_str = excel_df.to_json()
    the_file = "{0}teams.json".format(settings.data_path)
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)
    with open(the_file, 'w') as f:
        f.write(json_str)
    f.close()

    for root, dirs, files in os.walk(settings.data_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
