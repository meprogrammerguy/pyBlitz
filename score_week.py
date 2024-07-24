#!/usr/bin/env python3

import sys, getopt
import pyBlitz
from collections import OrderedDict
import json
import pdb
import os.path
from pathlib import Path
from datetime import datetime
import re
import scrape_schedule
from shutil import copyfile
import pandas as pd
import glob
import xlsxwriter
import measure_results

import settings

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

year = 0
now = datetime.now()
year = int(now.year)
if (len(sys.argv)>=3):
    year = GetNumber(sys.argv[2])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)
current_working_directory = os.getcwd()

def main(argv):
    week = "current"
    test = False
    try:
        opts, args = getopt.getopt(argv, "hw:t", ["help", "week=", "test"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    for o, a in opts:
        if o in ("-t", "--test"):
            test = True
        elif o in ("-h", "--help"):
            usage()
            exit()
        elif o in ("-w", "--week"):
            week = a
        else:
            assert False, "unhandled option"
    if (test):
        testResult = pyBlitz.Test()
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        PredictTournament(week)

def usage():
    usage = """
    -h --help                 Prints this help
    -t --test                 runs test routine to check calculations
    -w --week                 week to predict (use week 99 for the bowl games)
                                    (add the year to run for past years)
    """
    print (usage) 

def GetIndex(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

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
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])
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
        Path(wpath).mkdir(parents=True, exist_ok=True)
        if (os.path.exists(dest_file)):
            os.remove(dest_file)
        copyfile(item, dest_file)
        statname = "{0}json/stats{1}.json".format(wpath, idx)
        dest_file = "{0}json/stats{1}.json".format(spath, idx)
        dest_path = "{0}json/".format(spath, idx)
        Path(dest_path).mkdir(parents=True, exist_ok=True)
        if (os.path.exists(dest_file)):
            os.remove(dest_file)
        copyfile(statname, dest_file)

def SaveStats(output_file, week_path, stat_file):
    filename = os.path.basename(output_file)
    idx =  GetIndex(filename)
    dest_file = "{0}json/stats{1}.json".format(week_path, idx)
    spath = "{0}json/".format(week_path)
    Path(spath).mkdir(parents=True, exist_ok=True)
    copyfile(stat_file, dest_file)
    
def PredictTournament(week):
    stat_file = settings.data_path + "json/stats.json"
    week_path = "{0}{1}/".format(settings.predict_root, year)
    stats_path = "{0}{1}json/".format(settings.predict_root, year)
    sched_file = "{0}{1}/{2}json/sched.json".format(settings.predict_root, year, settings.predict_sched)
    saved_path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_saved)
    weekly_files = glob.glob("{0}week*.xlsx".format(week_path))
    SaveOffFiles(saved_path, week_path, weekly_files)
    for p in Path(week_path).glob("week*.xlsx"):
        p.unlink()
    for p in Path(stats_path).glob("stats*.json"):
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
    print ("Weekly Prediction Tool")
    print ("**************************")
    print ("Statistics file:\t{0}".format(stat_file))
    print ("Year is: {0}".format(year))
    print ("\trunning for Week: {0}".format(week))
    print ("\tDirectory Location: {0}".format(week_path))
    print ("**************************")
    list_predict = []
    list_predict.append(["Index", "Date", "TeamA", "AbbrA", "ChanceA", "ScoreA", "Spread", "TeamB", \
        "AbbrB", "ChanceB", "ScoreB", "Exceptions"])
    index = 0
    for item in json_sched.values():
        if int(week) == int(item["Week"]):
            teama, teamb = FindTeams(item["Team 1"], item["Team 2"], dict_stats)
            abbra, abbrb = FindAbbr(teama, teamb, dict_stats)
            neutral = False
            if (item["Where"].lower().strip() == "neutral"):
                neutral = True
            settings.exceptions = []
            dict_score = pyBlitz.Calculate(teama, teamb, neutral)
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
    output_file = "{0}week{1}.xlsx".format(week_path, week)
    SaveStats(output_file, week_path, stat_file)
    print ("... creating prediction spreadsheet")
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet()
    for row_num, row_data in enumerate(list_predict):
        for col_num, col_data in enumerate(row_data):
            worksheet.write(row_num, col_num, col_data)
    workbook.close()
    print ("{0} has been created.".format(output_file))
    measure_results.year = year
    measure_results.main(sys.argv[1:])
    # How are we doing? Let's find Out!
    file = "{0}json/results.json".format(saved_path)
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
