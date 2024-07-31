#!/usr/bin/env python3

import json
import pdb
from collections import OrderedDict
import os.path
from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import sys
import glob

import settings
import pyBlitz
import scrape_schedule

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def GetIndex(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def RefreshScheduleFiles():
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])

def HaveIWon(d, ta, tb, sa, sb, j):
    have_won = False
    for x in j:
        teama_won = False
        if (d == j[x]["Date"]) and (ta == j[x]["Team 1"]) and (tb ==  j[x]["Team 2"]):
            if j[x]["Score 1"] > j[x]["Score 2"]:
                teama_won = True
                if sa > sb:
                    have_won = True
            else:
                if sb > sa:
                    have_won = True
    return have_won

def myPercent(v1, v2):
    if v2 <= 0:
        return "0%"
    try:
        answer = float(v1/v2)
    except ValueError:
        return 0
    return str("{:.0f}".format(answer*100)) + "%"

year = 0
now = datetime.now()
year = int(now.year)
if (len(sys.argv)>=2):
    year = GetNumber(sys.argv[1])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)
current_working_directory = os.getcwd()

def main(argv):
    saved_path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_saved)
    sched_path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

    print ("Measure Actual Results Tool")
    print ("**************************")
    print (" ")
    print ("Year is: {0}".format(year))
    print ("Directory location: {0}".format(saved_path))
    print ("**************************")

    Path(sched_path).mkdir(parents=True, exist_ok=True)
    RefreshScheduleFiles()

    file = '{0}json/sched.json'.format(sched_path)
    if (not os.path.exists(file)):
        print ("schedule file is missing, run the scrape_schedule tool to create")
        exit()
    with open(file) as schedule_file:
        json_sched = json.load(schedule_file, object_pairs_hook=OrderedDict)
    
    Path(saved_path).mkdir(parents=True, exist_ok=True)
    file = '{0}week1.xlsx'.format(saved_path)
    if (not os.path.exists(file)):
        print ("Cannot measure results until week 2 or later, exiting")
        exit()

    week_files = glob.glob("{0}week*.xlsx".format(saved_path))
    list_week = []
    for file in week_files:
        excel_df = pd.read_excel(file, sheet_name='Sheet1')
        teams_json = json.loads(excel_df.to_json())
        teams_json['Week'] = GetIndex(file)
        list_week.append(teams_json)
 
    IDX=[]
    W=[]
    index = 0
    T=[]
    U=[]
    C=[]
    P=[]
    grand_total_games = 0
    grand_count_predicted = 0
    grand_count_wins = 0
    for item in list_week:
        week = item["Week"]
        total_games = len(item["Index"])
        grand_total_games+=total_games
        if week == 99:
            W.append("bowls")
        else:
            W.append("{:03d}".format(week))
        T.append(total_games)
        index+=1
        IDX.append(index)
        count_predicted=0
        count_wins=0
        for i in range(len(item["Index"])):
            scorea = item["ScoreA"][str(i)]
            if str(scorea).strip() == "?":
                scorea = "0"
            scoreb = item["ScoreB"][str(i)]
            if str(scoreb).strip() == "?":
                scoreb = "0"
            if int(scorea) + int(scoreb) > 0:
                game_won = HaveIWon(item["Date"][str(i)], item["TeamA"][str(i)], \
                    item["TeamB"][str(i)], item["ScoreA"][str(i)], item["ScoreB"][str(i)], json_sched)
                if game_won:
                    count_wins+=1
                count_predicted+=1
        grand_count_predicted+=count_predicted
        grand_count_wins+=count_wins
        U.append(total_games - count_predicted)
        C.append(count_wins)
        P.append(myPercent(count_wins, count_predicted))

    W.append("totals")             #grand totals row
    T.append(grand_total_games)
    index+=1
    IDX.append(index)
    U.append(grand_total_games - grand_count_predicted)
    C.append(grand_count_wins)
    P.append(myPercent(grand_count_wins, grand_count_predicted))

    df=pd.DataFrame(IDX,columns=['Index'])
    df['Week']=W
    df['Total Games']=T
    df['Count Unpredicted']=U
    df['Count Correct']=C
    df['Percent Correct']=P

    print ("... creating results JSON file")
    the_file = "{0}json/results.json".format(saved_path)
    the_path = "{0}json/".format(saved_path)
    Path(the_path).mkdir(parents=True, exist_ok=True)
    with open(the_file, 'w') as f:
        f.write(df.to_json(orient='index'))
    f.close()
    
    print ("... creating results spreadsheet")
    excel_file = "{0}results.xlsx".format(saved_path)
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.close()
    print ("done.")

if __name__ == "__main__":
    main(sys.argv[1:])
