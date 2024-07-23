#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import sys
import glob

import settings
import scrape_schedule

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def CalcPercent(total, skip, correct):
    try:
        return  round(correct / (total - skip) * 100., 2)
    except ZeroDivisionError:
        return None

def GetPercent(item):
    #pdb.set_trace()
    newstr = item.replace("%", "")
    newstr = newstr.replace("?", "")
    if (newstr.strip()==""):
        return -1
    return float(newstr)

def GetIndex(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def GetFiles(path, templatename):
    A = []
    files = Path(path).glob(templatename)
    for p in files:
        A.append(p)
    file_list = []
    for item in range(0, 19):
        file_list.append("?")
    for item in A:
        idx = GetIndex(item)
        if (len(file_list) > idx):
            file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

def CurrentScheduleFiles(filename):
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshScheduleFiles():
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])

def GetActualScores(score1, score2):
    if (score1.strip() == "canceled"):
        return -3, -3
    if (score1.strip() == "postponed"):
        return -2, -2
    if (score1.strip() == "?"):   # not yet Played Game
        return -1, -1
    return scorea, scoreb

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
        print ("Weekly files are missing, run the score_week tool to create")
        exit()

    week_files = glob.glob("{0}week*.xlsx".format(saved_path))
    list_week = []
    for file in week_files:
        excel_df = pd.read_excel(file, sheet_name='Sheet1')
        teams_json = json.loads(excel_df.to_json())
        teams_json['Week'] = GetIndex(file)
        list_week.append(teams_json)
    
    IDX=[]
    A=[]
    B=[]
    C=[]
    D=[]
    E=[]
    index = 0
    alltotal = 0
    allskip = 0
    allcorrect = 0
    count = 0
    total = 0
    skip = 0
    correct = 0
    for item in json_sched.values():
        week = int(item["Week"])
        total += 1
        chancea = -1
        abbra = ""
        abbrb = ""
        teama = ""
        teamb = ""
        if (index < len(list_week) and list_week[index]["Week"] == week):
            chancea = GetPercent(list_week[index]["ChanceA"])
            chanceb = GetPercent(list_week[index]["ChanceB"])
            pdb.set_trace()
            abbra = list_week[index]["AbbrA"]
            abbrb = list_week[index]["AbbrB"]
            teama = list_week[index]["TeamA"]
            teamb = list_week[index]["TeamB"]
        index += 1
        scorea, scoreb = GetActualScores(item["Score 1"], item["Score 2"])
        if ((int(chancea) == 0 and int(chanceb) == 0) or scorea < 0 or scoreb < 0):
            if (teama != "" and teamb != "" and "tickets" not in item["Score 1"]):
                if (item["Score1 "].lower() == "canceled"):
                    print ("***\nGame skipped\n\n\t[{0} vs {1}] \n\tabbreviation(s) [{2}] [{3}] Score {4}\n\tcanceled\n***\n"
                        .format(teama, teamb, abbra, abbrb, item["Score"]))
                elif (item["Score 1"].lower() == "postponed"):
                    print ("***\nGame skipped\n\n\t[{0} vs {1}] \n\tabbreviation(s) [{2}] [{3}] Score {4}\n\tpostponed\n***\n"
                        .format(teama, teamb, abbra, abbrb, item["Score 1"]))
                else:
                    if (item["Score 1"] != "?"):
                        print ("***\nGame skipped\n\n\t[{0} vs {1}] \n\tabbreviation(s) [{2}] [{3}] Score {4}\n\treview your merge files\n***\n".format(teama, teamb, abbra, abbrb, item["Score 1"]))
            skip += 1
        else:
            if (chancea >= 50 and (scorea >= scoreb)):
                correct += 1
            if (chancea < 50 and (scorea < scoreb)):
                correct += 1
        count += 1
        IDX.append(count)
        A.append(week)
        B.append(total)
        C.append(skip)
        D.append(correct)
        E.append(CalcPercent(total, skip, correct))
        print ("week{0} total={1}, skip={2}, correct={3} Percent={4}%".format(week, total, skip, correct, \
            CalcPercent(total, skip, correct)))
        alltotal = alltotal + total
        allskip = allskip + skip
        allcorrect = allcorrect + correct
    count += 1
    IDX.append(count)
    A.append(99)
    B.append(alltotal)
    C.append(allskip)
    D.append(allcorrect)
    E.append(CalcPercent(alltotal, allskip, allcorrect))

    print ("====================================================================")
    print ("Totals total={0}, skip={1}, correct={2} Percent={3}%".format(alltotal, allskip, allcorrect, \
        CalcPercent(alltotal, allskip, allcorrect)))
    print ("====================================================================")

    df=pd.DataFrame(IDX,columns=['Index'])
    df['Week']=A
    df['Total Games']=B
    df['Count Unpredicted']=C
    df['Count Correct']=D
    df['Percent Correct']=E

    file = "{0}results.json".format(saved_path)
    with open(file, 'w') as f:
        f.write(df.to_json(orient='index'))

    with open(file) as results_json:
        dict_results = json.load(results_json, object_pairs_hook=OrderedDict)

    file = "{0}results.csv".format(saved_path)
    results_sheet = open(file, 'w', newline='')
    csvwriter = csv.writer(results_sheet)
    count = 0
    for row in dict_results.values():
        if (count == 0):
            header = row.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(row.values())
    results_sheet.close()
    print ("done.")

if __name__ == "__main__":
    main(sys.argv[1:])
