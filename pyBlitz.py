#!/usr/bin/env python3

import os.path
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import pdb
from collections import OrderedDict
import re

import settings

def findTeams(first, second, dict_stats, verbose = True):
    teama = {}
    teamb = {}
    count = 0
    for item in dict_stats.values():
        if (item["BPI"].lower().strip() == first.lower().strip()):
            teama = item
            count += 1
        if (item["BPI"].lower().strip() == second.lower().strip()):
            teamb = item
            count += 1
        if (count == 2):
            break

    if (not teama and not teamb):
        log = "findTeams() - Could not find stats for either team [{0}] or [{1}]".format(first, second)
        settings.exceptions.append(log)
        return {}, {}
    if (not teama):
        log = "findTeams() - Could not find stats for the first team [{0}]".format(first)
        settings.exceptions.append(log)
        return {}, teamb
    if (not teamb):
        log = "findTeams() - Could not find stats for the second team [{0}]".format(second)
        settings.exceptions.append(log)
        return teama, {}
    return teama, teamb

def GetFloat(item):
    idx = re.findall('\d{1,2}[\.]{1}\d{1,2}', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return float(idx[0])

def GetPercent(thespread, dict_percent):
    aPercent = 0
    bPercent = 0
    flip = False
    if (thespread < 0):
        thespread = abs(thespread)
        flip = True
    if (thespread >= 19.5):
        if (flip):
            bPercent = 100
            aPercent = 0
        else:
            aPercent = 100
            bPercent = 0
    else:
        for item in dict_percent.values():
            if ("+" in item['Spread']):
                spread = 20
                if (flip):
                    bPercent = 100
                    aPercent = 0
                else:
                    aPercent = 100
                    bPercent = 0
                break
            else:
                spread = float(item['Spread'])
            if (spread >= thespread and thespread < (spread + .5)):
                if (flip):
                    bPercent = GetFloat(item["Favorite"])
                    aPercent = GetFloat(item["Underdog"])
                else:
                    aPercent = GetFloat(item["Favorite"])
                    bPercent = GetFloat(item["Underdog"])
                break          
    return aPercent, bPercent

def Chance(teama, teamb, dict_percent, homeTeam = 'Neutral', verbose = True):
    EffMgn = Spread(teama, teamb, verbose = False, homeTeam = homeTeam)
    if (verbose):
        print ("Chance(efficiency margin) {0}".format(EffMgn))
    aPercent, bPercent = GetPercent(EffMgn, dict_percent)
    if (verbose):
        if homeTeam == "Neutral":
            print ("Chance({0}) {1}%".format(teama["BPI"], aPercent),
                "vs. Chance({0}) {1}%".format(teamb["BPI"], bPercent))
        else:
            print ("Chance({0}) {1}%".format(teama["BPI"], aPercent),
                "at Chance({0}) {1}%".format(teamb["BPI"], bPercent))
    return aPercent, bPercent

def Tempo(teama, teamb, verbose = True):
    TdiffaScore = float(teama['PLpG3']) * float(teama['PTpP3'])
    TdiffaOScore = float(teama['OPLpG3']) * float(teama['OPTpP3'])
    TdiffbScore = float(teamb['PLpG3']) * float(teamb['PTpP3'])
    TdiffbOScore = float(teamb['OPLpG3']) * float(teamb['OPTpP3'])
    Tdiff = (TdiffaScore + TdiffbScore + TdiffaOScore + TdiffbOScore)/2.0
    if (verbose):
        print ("Tempo(tempo) {0}".format(Tdiff))
    return Tdiff

def Test(verbose):
    result = 0
    # Alabama, Clemson on 1/1/18 (stats from 1/7/18)
    # Actual Score: 24-6
    # venue was: Mercedes-Benz Super dome in New Orleans, Louisiana (Neutral Field "The Sugar Bowl")

    teama = {'BPI':"alabama", 'Ranking':118.5, 'PLpG3':64.7, 'PTpP3':.356, 'OPLpG3':18.7, 'OPTpP3':.246, 'Result1':65.1, 'Result2':17}
    teamb = {'BPI':"clemson", 'Ranking':113, 'PLpG3':79.3, 'PTpP3':.328, 'OPLpG3':12.3, 'OPTpP3':.199, 'Result1':34.9,'Result2':11}

    file = "{0}bettingtalk.json".format(settings.defaults_path)
    if (not os.path.exists(file)):
        settings.exceptions.append("Test() - bettingtalk file is missing, run the scrape_bettingtalk tool to create")
        exit()
    with open(file) as percent_file:
        dict_percent = json.load(percent_file, object_pairs_hook=OrderedDict)

    if (verbose):
        print ("Test #1 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, Testing Chance() routine")
    chancea, chanceb =  Chance(teama, teamb, dict_percent, homeTeam = 'Neutral', verbose = verbose)
    if (teama['Result1'] == chancea):
        result += 1
    if (teamb['Result1'] == chanceb):
        result += 1
    if (verbose and result == 2):
        print ("Test #1 - pass")
        print ("*****************************")
    if (verbose and result != 2):
        print ("Test #1 - fail")
        print ("*****************************")
    if (verbose):
        print ("Test #2 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, testing Score() routine")
    scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = 'Neutral')
    if (teama['Result2'] == scorea):
        result += 1
    if (teamb['Result2'] == scoreb):
        result += 1
    if (result == 4):
        return True
    return False

def Score(teama, teamb, verbose = True, homeTeam = 'Neutral'):
    tempo = Tempo(teama, teamb, False)
    if (verbose):
        print ("Score(tempo) {0}".format(tempo))
    EffMgn = Spread(teama, teamb, verbose = False, homeTeam = homeTeam)
    if (verbose):
        print ("Score(efficiency margin) {0}".format(EffMgn))
    aScore = round((tempo/2.0) + (EffMgn / 2.0))
    bScore = round((tempo/2.0) - (EffMgn /2.0))
    if (aScore < 0):
        aScore = 0
    if (bScore < 0):
        bScore = 0
    if (verbose):
        print ("Score({0}) {1} at Score({2}) {3}".format(teama["BPI"], aScore, teamb["BPI"], bScore))
    return aScore, bScore

def Spread(teama, teamb, verbose = True, homeTeam = 'Neutral'):
    EMdiff = (float(teama['Ranking']) - float(teamb['Ranking']))
    EffMgn = 0
    if (homeTeam.lower().strip() == teama["BPI"].lower().strip()):
        EffMgn = EMdiff + settings.homeAdvantage
    elif (homeTeam.lower().strip() == teamb["BPI"].lower().strip()):
        EffMgn = EMdiff - settings.homeAdvantage
    else:
        EffMgn = EMdiff
    if (verbose):
        print ("Spread(efficiency margin) {0}".format(EffMgn))
    return EffMgn

def Calculate(first, second, neutral, verbose):
    if (verbose):
        if (neutral):
            info = "{0} verses {1} at a neutral location".format(first, second)
            print (info)
        else:
            info = "Visiting team: {0} verses Home team: {1}".format(first, second)
            print (info)
    file = "{0}stats.json".format(settings.data_path)
    with open(file) as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

    file = "{0}bettingtalk.json".format(settings.data_path)
    if (not os.path.exists(file)):
        settings.exceptions.append("Calculate() - bettingtalk file is missing, run the scrape_bettingtalk tool to create")
        exit()
    with open(file) as percent_file:
        dict_percent = json.load(percent_file, object_pairs_hook=OrderedDict)

    teama, teamb = findTeams(first, second, dict_stats, verbose = verbose)
    if (not teama and not teamb):
        settings.exceptions.append("Calculate() - [{0}] and [{1}] missing from stats, can't predict".format(first, second))
        return {}
    classa = "?"
    if (teama):
        classa = teama["Class"].lower().strip()
    classb = "?"
    if (teamb):
        classb = teamb["Class"].lower().strip()
    if (classa == "?" or classb == "?"):
        settings.exceptions.append("Calculate() - [{0}] team playing [{1}] team,  Cannot predict, Fix merge spreadsheet(s)".format(classa, classb))
        dict_score = {'teama':first, 'scorea':"0", 'chancea':"0" ,'teamb':second, 'scoreb':"0", 'chanceb':"0", 'spread': 0, 'tempo':"0"}
        print ("Warning: {0} playing {1}, Cannot Predict, Fix merge spreadsheet(s)".format(first, second))
        return dict_score
    else:
        if (classa == "1a" and classb != "1a"):
            settings.exceptions.append("Calculate() - [{0}] team playing [{1}] team, {2} wins".format(classa, classb, first))
            dict_score = {'teama':first, 'scorea':"0", 'chancea':"100" ,'teamb':second, 'scoreb':"0", 'chanceb':"0", 'spread': 0, 'tempo':"0"}
            return dict_score
        if (classa != "1a" and classb == "1a"):
            settings.exceptions.append("Calculate() - [{0}] team playing [{1}] team, {2} wins".format(classa, classb, second))
            dict_score = {'teama':first, 'scorea':"0", 'chancea':"0" ,'teamb':second, 'scoreb':"0", 'chanceb':"100", 'spread': 0, 'tempo':"0"}
            return dict_score
    if (not neutral):
        chancea, chanceb =  Chance(teama, teamb, dict_percent, homeTeam = teamb["BPI"], verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = teamb["BPI"])
        spread = Spread(teama, teamb, verbose = verbose, homeTeam = teamb["BPI"])
    else:
        chancea, chanceb =  Chance(teama, teamb, dict_percent, verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose)
        spread = Spread(teama, teamb, verbose = verbose)

    tempo = Tempo(teama, teamb, verbose = verbose)

    dict_score = {'teama':first, 'scorea':"{0}".format(scorea), 'chancea':"{0}".format(chancea) ,'teamb':second, 'scoreb':"{0}".format(scoreb), 'chanceb':"{0}"
        .format(chanceb), 'spread': round(spread, 3), 'tempo':"{0}".format(int(round(tempo))) }
    if (verbose):
        print ("Calculate(dict_score) {0}".format(dict_score))
    return dict_score
