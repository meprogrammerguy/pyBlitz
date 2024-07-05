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
from collections import OrderedDict
import contextlib
import os, sys, stat, time
import datetime
from pathlib import Path
import re
import glob
import gzip

import settings
import pyBlitz

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def read_file(file):
    try:
        f = gzip.open(file, 'r')
    except gzip.BadGzipFile:
        f = open(file, 'r')
    return f

def gzip_str(string_: str) -> bytes:
    return gzip.compress(string_.encode())


def gunzip_bytes_obj(bytes_obj: bytes) -> str:
    return gzip.decompress(bytes_obj).decode()

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

    excel_file = "{0}teams.xlsx".format(settings.data_path)
    ti_c = os.path.getctime(excel_file)
    ti_m = os.path.getmtime(excel_file)
    c_ti = time.ctime(ti_c)
    m_ti = time.ctime(ti_m)
    print(" ")
    print(f"        {excel_file} was created at {c_ti} and was last modified at {m_ti}")
    print("===      To recreate: edit {0} and blank out the creation date, and rerun scraper ===".format(excel_file))
    print(" ")
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
        for item in url:
            req = Request(url=item, \
                          headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
            try:
                page = urlopen(req)
            except HTTPError as e:
                page = e.read()
            pages.append(BeautifulSoup(page, "html5lib"))
    else:
        pages = []
        for item in url:
            with open(item, 'r') as file:
                page = file.read().rstrip()
            pages.append(BeautifulSoup(page, "html5lib"))
    Path(settings.data_path).mkdir(parents=True, exist_ok=True)

    index = 0
    A=[]
    B=[]
    C=[]
    D=[]
    E=[]
    F=[]
    G=[]
    H=[]
    I=[]
    J=[]
    K=[]
    for page in pages:
        body = page.findAll('body')
        names = page.findAll('span', attrs = {'class':'Table__Team'})
        names2 = page.findAll('div', attrs = {'class':'Table__Team'})
        tdates = page.findAll('div', attrs = {'class':'Table__Title'})
        titles = page.findAll('th', attrs = {'class':'Table__TH'})
        tbodys = page.findAll('tbody', attrs = {'class':'Table__TBODY'})
        #the_links = page.findAll('div', text="Link")
        for name in names:
            A.append(pyBlitz.CleanString(name.text).split())
            J.append(name) # get IDs from here too
        for title in titles:
            B.append(title.text)
        for tbody in tbodys:
            C.append(tbody)
            # (C[0].td.a) gives me team id
            a_texts = tbody.findAll('a')
            for a_text in a_texts:
                G.append(a_text)
            D.append(tbody.text)
        for ids in C:
            H.append(ids.td.a)
        #pdb.set_trace()
        for tdate in tdates:
            E.append(tdate)
            F.append(tdate.text)
    new_items = []
    for items in A:
        new_items.append([item for item in items if not item.isdigit()])
    A = []
    for item in new_items:
        the_string = ""
        for piece in item:
            the_string = the_string + piece + " "
        A.append(the_string[:-1])
    A = list(set(A))
    H = list(set(H))
    J = list(set(J))
    #       (Pdb) print (G[4].text)
    #               OHIO 41, GASO 21
    #       the step is 8: 4, 12, 20 ...
    #
    #       [start:stop:step]
    # mylist = [1,2,3,4,5,6,7,8,9,10]
    # for i in mylist[::2]:
    #   print (i)
    #       prints 1 3 5 7 9
    
    abbrev=[]
    for items in G[4::8]:
        the_list=items.text.replace(',', '').split()
        for each_one in the_list[:4:2]:
            if each_one == "M-OH":
                each_one = "OHIO"
            if not each_one.isdigit():
                abbrev.append(each_one)
    abbrev = list(set(abbrev))
    pages = []
    for item in abbrev:
        url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{0}".format(item)
        req = Request(url=url, \
        headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        #try:
            #page = urlopen(req)
        #except HTTPError as e:
            #page = e.read()
        #soup = BeautifulSoup(page,"html5lib")
        #print ("got soup")
        #pdb.set_trace()
        #print (url)
        #if item == "M-OH":
            
            #print (page.decode("ISO 8859-1"))
            #print (soup.text)
            #pdb.set_trace()
        #site_json=json.loads(soup.text)
        #print ("got site_json")
        #pdb.set_trace()
        #pages.append(site_json)
        #the_page=BeautifulSoup(page, "html5lib")
        #the_file = "{0}/abbrev/{1}.json".format(settings.data_path, item.lower())
        #the_path = "{0}/abbrev".format(settings.data_path)
        #Path(the_path).mkdir(parents=True, exist_ok=True)
        #with open(the_file, 'w') as f:
            #json.dump(site_json, f)
        #f.close()
        #with open(the_file, 'w', encoding='utf-8') as f:
            #json.dump(page.text, f, ensure_ascii=False, indent=4)
        #f = open(the_file, "w")
        #f.write(page.text)
        #f.close()

        #pages.append(BeautifulSoup(page, "html5lib"))
    pages=[]
    for item in abbrev:
        the_file = "{0}/abbrev/{1}.json".format(settings.data_path, item.lower())
        with open(the_file, 'r') as file:
            data = file.read()
            pages.append(json.loads(data))
        file.close()
    #print ("got pages from files")
    #pdb.set_trace()
    id=[]
    abbreviation=[]
    shortDisplayName=[]
    displayName=[]
    name=[]
    nickname=[]
    location=[]
    standingSummary=[]
    count = 0
    for page in pages:
        #print (str(count))
        #print (page)
        #if page == None or page == '':
            #pdb.set_trace()
            #continue
        #print (json_obj)
        #if count >= 163:
            #pdb.set_trace()
        
        if page["team"]:
            team = page["team"]            
            if team["id"]:
                id.append(team["id"])                    
            if team["abbreviation"]:
                abbreviation.append(team["abbreviation"])
                print (str(count) + " " + team["abbreviation"])
            if team["shortDisplayName"]:
                shortDisplayName.append(team["shortDisplayName"])
            if team["displayName"]:
                displayName.append(team["displayName"])
            if team["name"]:
                name.append(team["name"])
            if team["nickname"]:
                nickname.append(team["nickname"])
            if team["location"]:
                location.append(team["location"]) 
            if "standingSummary" in team:
                standingSummary.append(team["standingSummary"])
        count = count + 1
    
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
    
    rows={'created': {0: c_ti}}
    rows.update({"id":ids})
    rows.update({"abbreviation":abbreviations}),
    rows.update({"shortDisplayName":shortDisplayNames})
    rows.update({"displayName":displayNames})
    rows.update({"name":names})
    rows.update({"nickname":nicknames})
    rows.update({"location":locations})
    rows.update({"standingSummary":standingSummarys})

    pdb.set_trace()    

    df = pd.DataFrame(rows)    
    df.to_excel(excel_file, index=False) 
 
    for root, dirs, files in os.walk(settings.data_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    print ("done.")

if __name__ == "__main__":
  main(sys.argv[1:])
