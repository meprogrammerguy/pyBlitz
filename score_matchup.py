#!/usr/bin/env python3

import os, os.path
import sys, getopt
from datetime import datetime
from pathlib import Path
import pdb
from pynotifier import NotificationClient, Notification
from pynotifier.backends import platform
import subprocess
from collections import OrderedDict
import pandas as pd
from collections import OrderedDict
import json

import settings
import pyBlitz

def GetShorterTeams(f, s, db):
    first = ""
    second = ""
    for item in db["displayName"]:
        if f == db["displayName"][item]:
            first = db["shortDisplayName"][item]
        if s == db["displayName"][item]:
            second = db["shortDisplayName"][item]
        if first and second:
            break
    return first, second

def ParseResult(s):
    result={}
    y = s.splitlines()
    t1 = y[1].split("data: ")
    t2 = y[3].split("data: ")
    chk = y[4].split("form: ")
    chk2 = chk[1].split("|")
    result["first"] = t1[1]
    result["second"] = t2[1]
    if "TRUE" in chk2[0]:
        verbose = True
    else:
        verbose = False
    if "TRUE" in chk2[1]:
        neutral = True
    else:
        neutral = False
    result["verbose"] = verbose
    result["neutral"] = neutral
    return result
    
def CurrentStatsFile(filename):
    if (not os.path.exists(filename)):
        return False
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshStats():
    import scrape_teams
    import scrape_bornpowerindex
    import scrape_teamrankings
    import scrape_schedule
    import scrape_espn_odds
    import combine_stats

def main(argv):
    cwd = os.getcwd()
    
    print("... retrieving teams spreadsheet")
    team_file = '{0}teams.xlsx'.format(settings.data_path)
    if (os.path.exists(team_file)):
        excel_df = pd.read_excel(team_file, sheet_name='Sheet1')
        team_json = json.loads(excel_df.to_json())
    else:
        print ("    *** run scrape_teams and then come back ***")
        exit()

    first = ""
    second = ""
    neutral = False
    test = False
    try:
        opts, args = getopt.getopt(argv, "hf:s:nt", ["help", "first=", "second=", "neutral","test"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    for o, a in opts:
        if o in ("-n", "--neutral"):
            neutral = True
        elif o in ("-t", "--test"):
            test = True
        elif o in ("-h", "--help"):
            usage()
            exit()
        elif o in ("-f", "--first"):
            first = a
        elif o in ("-s", "--second"):
            second = a
        else:
            assert False, "unhandled option"
    print ("Score Matchup Tool")
    print ("**************************")
    usage()
    print ("**************************")
    if (test):
        testResult = pyBlitz.Test()
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        run_gui = '{0}/score_matchup_gui.sh'.format(cwd)
        from_bash = subprocess.run([run_gui], capture_output=True)
        result = ParseResult(from_bash.stdout.decode("utf-8"))
        first, second = GetShorterTeams(result["first"], result["second"], team_json)
        verbose = result["verbose"]
        neutral = result["neutral"]
        if (not first and not second):
            print ("Score Matchup Tool")
            print ("**************************")
            usage()
            print ("**************************")
            exit()

        Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
        stat_file = "{0}json/stats.json".format(settings.data_path)
        if (not CurrentStatsFile(stat_file)):
            RefreshStats()
        ds = {}
        settings.exceptions = []
        ds = pyBlitz.Calculate(first, second, neutral)
        if (settings.exceptions):
            print (" ")
            print ("\t*** Warnings ***")
            for item in settings.exceptions:
                print (item)
            print ("\t*** Warnings ***")
            print (" ")
        if (not ds):
            exit()
        if (neutral):
            answer = "{0} {1}% vs {2} {3}% {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"], \
                ds["scorea"], ds["scoreb"])
        else:
            answer = "{0} {1}% at {2} {3}% {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"], \
                ds["scorea"], ds["scoreb"])
        print (answer)
        blitz_icon = '{0}/football.ico'.format(cwd)
        c = NotificationClient()
        c.register_backend(platform.Backend())
        notification = Notification(title='pyBlitz Predictor', message=answer,\
            icon_path=blitz_icon, duration=20)
        c.notify_all(notification)

def usage():
    usage = """
    -h --help                 Prints this
    -f --first                First Team  (The Away Team)
    -s --second               Second Team (The Home Team)
    -n --neutral              Playing on a neutral Field
    -t --test                 runs test routine to check calculations
    """
    print (usage) 

if __name__ == "__main__":
  main(sys.argv[1:])
