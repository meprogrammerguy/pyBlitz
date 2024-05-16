#!/usr/bin/env python3

import sys, getopt
import pdb
import os.path
from datetime import datetime

import settings
import scrape_schedule

def main(argv):
    now = datetime.now()
    year = int(now.year)
    stat_file = "{0}stats.json".format(settings.data_path)
    sched_file = "{0}{1}/{2}sched1.json".format(settings.predict_root, year, settings.predict_sched)
    print ("Scrape all pages Tool")
    print ("**************************")
    print ("Statistics file:\t{0}".format(stat_file))
    print ("\tDirectory Location: {0}".format(settings.data_path))
    print ("===")
    print ("	A good time to run is as an easy initial setup")
    print ("	or possibly at the beginning of each season")
    print ("===")
    print ("**************************")
    if (not CurrentStatsFile(stat_file)):
        RefreshStats()
    if (not CurrentSchedFile(sched_file, year)):
        RefreshSched(year)
    print ("done.")

def CurrentStatsFile(filename):
    if (not os.path.exists(filename)):
        return False
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def CurrentSchedFile(filename, year):
    if (not os.path.exists(filename)):
        return False
    sched = os.path.getmtime(filename)
    sched_date = datetime.fromtimestamp(sched)
    if sched_date.year < year:
        return False
    return True

def RefreshStats():
    import scrape_abbreviations
    #import scrape_bettingtalk          (this is no longer free/missing?, removing it on 5/16/2024)
    import scrape_bornpowerindex
    import scrape_teamrankings
    import combine_merge
    import combine_stats

def RefreshSched(year):
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])

if __name__ == "__main__":
  main(sys.argv[1:])
