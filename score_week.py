#!/usr/bin/env python3

import sys, getopt
import pyBlitz
from collections import OrderedDict
import json
import csv
import pdb
import os.path
from pathlib import Path
from datetime import datetime
import re
import scrape_schedule
from shutil import copyfile
import pandas as pd

import settings

def main(argv):
    stat_file = settings.data_path + "json/stats.json"
    week = "current"
    verbose = False
    test = False
    try:
        opts, args = getopt.getopt(argv, "hs:w:vt", ["help", "stat_file=", "week=", "verbose", "test"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-t", "--test"):
            test = True
        elif o in ("-h", "--help"):
            usage()
            exit()
        elif o in ("-s", "--stat_file"):
            stat_file = a
        elif o in ("-w", "--week"):
            week = a
        else:
            assert False, "unhandled option"
    if (test):
        testResult = pyBlitz.Test(verbose)
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        PredictTournament(week, stat_file, verbose)

def usage():
    usage = """
    -h --help                 Prints this help
    -v --verbose              Increases the information level
    -s --stat_file            stats file (json file format)
    -t --test                 runs test routine to check calculations
    -w --week                 week to predict

    """
    print (usage) 

def GetIndex(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetSchedFiles(path, templatename):
    A = []
    for p in Path(path).glob(templatename):
        A.append(str(p))
    file_list = []
    for item in range(0, 19):
        file_list.append("?")
    for item in A:
        idx = GetIndex(item)
        if (len(file_list) > idx):
            file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

def CurrentStatsFile(filename):
    if (not os.path.exists(filename)):
        return False
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if str(stat_date.date()) < str(datetime.now().date())[:10]:
        return False
    return True

def RefreshStats():
    import scrape_teams
    import scrape_bornpowerindex
    import scrape_teamrankings
    import scrape_schedule
    import scrape_espn_odds
    import combine_stats

def FindTeams(teama, teamb, dict_stats):
    FoundA = ""
    FoundB = ""
    for item in dict_stats.values():
        if (teama.lower().strip() == item["team"].lower().strip()):
            FoundA = item["team"]
        if (teamb.lower().strip() == item["team"].lower().strip()):
            FoundB = item["team"]
        if (FoundA and FoundB):
            break
    return FoundA, FoundB

def FindAbbr(teama, teamb, dict_stats):
    FoundAbbrA = ""
    FoundAbbrB = ""
    for item in dict_stats.values():
        stats = item["team"].strip()
        div = item["Class"].strip()
        abbr = item["abbr"].strip()
        if (teama.strip() == stats and div == "DIVISION 1 FBS"):
            FoundAbbrA = abbr
        if (teamb.strip() == stats and div == "DIVISION 1 FBS"):
            FoundAbbrB = abbr
    return FoundAbbrA, FoundAbbrB

def SaveOffFiles(spath, wpath, file_list):
    Path(spath).mkdir(parents=True, exist_ok=True)
    for item in file_list:
        filename = os.path.basename(str(item))
        week_path = os.path.dirname(item)
        idx =  GetIndex(filename)
        dest_file = "{0}{1}".format(spath, filename)
        if (os.path.exists(dest_file)):
            os.remove(dest_file)
        copyfile(item, dest_file)
        statname = "{0}stats{1}.json".format(wpath, idx)
        dest_file = "{0}stats{1}.json".format(spath, idx)
        if (os.path.exists(dest_file)):
            os.remove(dest_file)
        copyfile(statname, dest_file)

def SaveStats(output_file, week_path, stat_file):
    filename = os.path.basename(output_file)
    idx =  GetIndex(filename)
    dest_file = "{0}stats{1}.json".format(week_path, idx)
    copyfile(stat_file, dest_file)
    
def GetDatesByWeek(j):
    wd={}
    Sdates=[]
    for item in j.values():
        Sdates.append(item["Date"].strip())
    scheddate_set = set(Sdates)
    dates = list(scheddate_set)
    dates.sort()
    idx=0
    for x in range(25):
        bw = dates[idx]
        df = pd.Timestamp(bw)
        bdow = df.dayofweek
        idx2=0
        last = False
        for y in range(bdow, 7):
            if idx + idx2 >= len(dates):
                last = True
                lw = dates[len(dates) - 1]
                break
            ew = dates[idx + idx2]
            idx2+=1
        if last:
            break
        df = pd.Timestamp(ew)
        edow = df.dayofweek
        if edow <= bdow:
            ew = bw
            idx2-=1
        idx+=idx2
        wd[x+1] = [bw, ew]
    wd[x+1] = [bw, lw]
    return wd

def PredictTournament(week, stat_file, verbose):
    now = datetime.now()
    year = int(now.year)
    week_path = "{0}{1}/".format(settings.predict_root, year)
    sched_file = "{0}{1}/{2}json/sched.json".format(settings.predict_root, year, settings.predict_sched)
    saved_path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_saved)
    weekly_files = GetSchedFiles(week_path, "week*.csv")
    SaveOffFiles(saved_path, week_path, weekly_files)
    for p in Path(week_path).glob("week*.csv"):
        p.unlink()
    for p in Path(week_path).glob("stats*.json"):
        p.unlink()
    if (not CurrentStatsFile(stat_file)):
        print ("refreshing stats stuff")
        RefreshStats()
    if (not os.path.exists(sched_file)):
        print ("schedule file is missing, run the scrape_schedule tool to create")
        exit()
    with open(sched_file) as schedule_file:
        json_sched = json.load(schedule_file, object_pairs_hook=OrderedDict)
    if (not os.path.exists(stat_file)):
        print ("statistics file is missing, run the combine_stats tool to create")
        exit()
    with open(stat_file) as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)
    week_dates = GetDatesByWeek(json_sched)
    print ("Weekly Prediction Tool")
    print ("**************************")
    print ("Statistics file:\t{0}".format(stat_file))
    print ("\trunning for Week: {0}".format(week))
    print ("\tDirectory Location: {0}".format(week_path))
    print ("**************************")
    list_predict = []
    list_predict.append(["Index", "Date", "TeamA", "AbbrA", "ChanceA", "ScoreA", "Spread", "TeamB", \
        "AbbrB", "ChanceB", "ScoreB", "Exceptions"])
    index = 0
    for item in json_sched.values():
        start_date = week_dates[int(week)][0]
        end_date = week_dates[int(week)][1]
        if start_date >= item["Date"] and item["Date"] <= end_date:
            teama, teamb = FindTeams(item["Team 1"], item["Team 2"], dict_stats)
            abbra, abbrb = FindAbbr(teama, teamb, dict_stats)
            neutral = False
            if (item["Where"].lower().strip() == "neutral"):
                neutral = True
            settings.exceptions = []
            dict_score = pyBlitz.Calculate(teama, teamb, neutral, verbose)
            errors = " "
            if (settings.exceptions):
                for itm in settings.exceptions:
                    errors += itm + ", "
            errors = errors[:-2]
            index += 1
            if (len(dict_score) > 0):
                list_predict.append([str(index), item["Date"], item["Team 1"], \
                    abbra, dict_score["chancea"], dict_score["scorea"], dict_score["spread"], item["Team 2"], \
                    abbrb, dict_score["chanceb"], dict_score["scoreb"], errors])
            else:
                list_predict.append([str(index), item["Date"], item["Team 1"], abbra, "?", \
                    "?", "?", item["Team 2"], abbrb, "?", "?",
                    "Warning: cannot predict, both teams missing, fix the merge spreadsheets"])
                print ("Warning: Neither {0} or {1} have been found, \n\t Suggest reviewing/fixing " \
                    "the merge spreadsheet(s) and re-run".format( item["Team 1"], item["Team 2"]))
    Path(week_path).mkdir(parents=True, exist_ok=True)
    output_file = "{0}week{1}.csv".format(week_path, week)
    SaveStats(output_file, week_path, stat_file)
    predict_sheet = open(output_file, 'w', newline='')
    csvwriter = csv.writer(predict_sheet)
    for row in list_predict:
        csvwriter.writerow(row)
    predict_sheet.close()
    print ("{0} has been created.".format(output_file))
    pdb.set_trace()    
    import measure_results
    # How are we doing? Let's find Out!
    file = "{0}results.json".format(saved_path)
    if (os.path.exists(file)):
        dict_results = []
        last_week = GetIndex(week) - 1
        with open(file) as results_file:
            dict_results.append(json.load(results_file, object_pairs_hook=OrderedDict))
        if (len(dict_results) > 0):
            for idx in range(len(dict_results)):
                for item in dict_results[idx].values():
                    if (last_week > 0 and last_week == item["Week"]):
                        print ("=================================================")
                        print ("For week{0}, winning percent was: {1}%".
                            format(last_week, item["Percent Correct"]))
                        print ("=================================================")
                    if (item["Week"] == 99):
                        print ("=================================================")
                        print ("For this year so far, winning percent is: {0}%".
                            format(item["Percent Correct"]))
                        print ("=================================================")
    print ("done.")
if __name__ == "__main__":
  main(sys.argv[1:])
