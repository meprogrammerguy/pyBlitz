#!/usr/bin/env python3

import os.path
import sys, getopt
from datetime import datetime
from pathlib import Path
import pdb

import settings
import pyBlitz

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
        if (not first and not second):
            print ("you must input the team names to run this tool, (first and second arguments)")
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
            print ("{0} {1}% vs {2} {3}% {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"], \
                ds["scorea"], ds["scoreb"]))
        else:
            print ("{0} {1}% at {2} {3}% {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"], \
                ds["scorea"], ds["scoreb"]))

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
