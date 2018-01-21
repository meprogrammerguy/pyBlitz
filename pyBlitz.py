#!/usr/bin/env python3

import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import pdb
from collections import OrderedDict
import re

homeAdvantage = 7.897

def findTeams(first, second, dict_stats, verbose = True):
    teama = {}
    teamb = {}
    count = 0

    for item in dict_stats.values():
        if (item["Team"].lower().strip() == first.lower().strip()):
            teama = item
            count += 1
        if (item["Team"].lower().strip() == second.lower().strip()):
            teamb = item
            count += 1
        if (count == 2):
            break
    if (verbose and count < 2):
        if (not teama):
            print ("Could not find stats for {0}".format(first))
        if (not teamb):
            print ("Could not find stats for {0}".format(second))
        return {}, {}
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
            print ("Chance({0}) {1}%".format(teama["Team"], aPercent),
                "vs. Chance({0}) {1}%".format(teamb["Team"], bPercent))
        else:
            print ("Chance({0}) {1}%".format(teama["Team"], aPercent),
                "at Chance({0}) {1}%".format(teamb["Team"], bPercent))
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
    # venue was: Mercedes-Benz Superdome in New Orleans, Louisiana (Neutral Field "The Sugar Bowl")

    teama = {'Team':"alabama", 'Ranking':118.5, 'PLpG3':64.7, 'PTpP3':.356, 'OPLpG3':18.7, 'OPTpP3':.246, 'Result1':65.1, 'Result2':17}
    teamb = {'Team':"clemson", 'Ranking':113, 'PLpG3':79.3, 'PTpP3':.328, 'OPLpG3':12.3, 'OPTpP3':.199, 'Result1':34.9,'Result2':11}

    with open("data/bettingtalk.json") as percent_file:
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
        print ("Score({0}) {1} at Score({2}) {3}".format(teama["Team"], aScore, teamb["Team"], bScore))
    return aScore, bScore

def Spread(teama, teamb, verbose = True, homeTeam = 'Neutral'):
    EMdiff = (float(teama['Ranking']) - float(teamb['Ranking']))
    EffMgn = 0
    if (homeTeam.lower().strip() == teama["Team"].lower().strip()):
        EffMgn = EMdiff + homeAdvantage
    elif (homeTeam.lower().strip() == teamb["Team"].lower().strip()):
        EffMgn = EMdiff - homeAdvantage
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

    with open("data/stats.json") as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

    with open("data/bettingtalk.json") as percent_file:
        dict_percent = json.load(percent_file, object_pairs_hook=OrderedDict)

    teama, teamb = findTeams(first, second, dict_stats, verbose = verbose)
    if (not teama or not teamb):
        return {}
    if (not neutral):
        chancea, chanceb =  Chance(teama, teamb, dict_percent, homeTeam = teamb["Team"], verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
        spread = Spread(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
    else:
        chancea, chanceb =  Chance(teama, teamb, dict_percent, verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose)
        spread = Spread(teama, teamb, verbose = verbose)

    tempo = Tempo(teama, teamb, verbose = verbose)

    dict_score = {'teama':first, 'scorea':"{0}".format(scorea), 'chancea':"{0}%".format(chancea) ,'teamb':second, 'scoreb':"{0}".format(scoreb), 'chanceb':"{0}%".format(chanceb), 'spread': round(spread, 3), 'tempo':"{0}".format(int(round(tempo * 100))) }
    if (verbose):
        print ("Calculate(dict_score) {0}".format(dict_score))
    return dict_score
