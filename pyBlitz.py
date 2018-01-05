#!/usr/bin/env python3

import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import pdb
from scipy.stats import norm
from collections import OrderedDict

def findTeams(first, second, verbose = True, file = "stats.json"):
    teama = {}
    teamb = {}
    count = 0

    with open(file) as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

    for item in dict_stats.values():
        if (item["Team"].lower() == first.lower()):
            teama = item
            count += 1
        if (item["Team"].lower() == second.lower()):
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

def Chance(teama, teamb, std = 15.38, homeAdvantage = 7.897, homeTeam = 'none', verbose = True):
    EffMgn = Line(teama, teamb, verbose = False, homeTeam = homeTeam, homeAdvantage = homeAdvantage)
    if (verbose):
        print ("Chance(efficiency margin) {0}".format(EffMgn))
    bPercent = norm.cdf(0, EffMgn, std)
    aPercent = 1.0 - bPercent
    aPercent = int(round(aPercent * 100.0))
    bPercent = int(round(bPercent * 100.0))
    if (verbose):
        print ("Chance({0}) {1}%".format(teama["Team"], aPercent), "vs. Chance({0}) {1}%".format(teamb["Team"], bPercent))
    return aPercent, bPercent

def Tempo(teama, teamb, verbose = True):
    Tdiff = (float(teama['PLpG']) * float(teamb['OPTpP']) + (float(teamb['PLpG']) * float(teama['OPTpP']))) / 200.0
    if (verbose):
        print ("Tempo(tempo) {0}".format(Tdiff * 100))
    return Tdiff

def Test(verbose):
    result = 0
    # Alabama, Clemson on 1/1/18 (stats from 1/3/18)
    # Actual Score: 24-6
    # venue was: Mercedes-Benz Superdome in New Orleans, Louisiana (Neutral Field "The Sugar Bowl")
    teama = {'Team':"alabama", 'S&P+M':20.8, 'PLpG':64.7, 'OPTpP':.246, 'OOPTpG':19, 'Result1':52, 'Result2':17}
    teamb = {'Team':"clemson", 'S&P+M':15.3, 'PLpG':79.3, 'OPTpP':.199, 'OOPTpG':10, 'Result1':48,'Result2':16}
    if (verbose):
        print ("Test #1 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, Testing Chance() routine")
    chancea, chanceb =  Chance(teama, teamb, homeTeam = 'none', verbose = verbose)
    if (teama['Result1'] == chancea):
        result += 1
    if (teamb['Result1'] == chanceb):
        result += 1
    if (verbose and result == 2):
        print ("Test #1 - pass")
    else:
        print ("Test #1 - fail")
    if (verbose):
        print ("Test #2 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, testing Score() routine")
    scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = 'none')
    if (teama['Result2'] == scorea):
        result += 1
    if (teamb['Result2'] == scoreb):
        result += 1
    if (result == 4):
        return True
    return False

def Score(teama, teamb, verbose = True, homeAdvantage = 7.897, homeTeam = 'none'):
    tempo = Tempo(teama, teamb, False)
    if (verbose):
        print ("Score(tempo) {0}".format(tempo * 100))
    EffMgn = Line(teama, teamb, verbose = False, homeTeam = homeTeam, homeAdvantage = homeAdvantage)
    if (verbose):
        print ("Score(efficiency margin) {0}".format(EffMgn))
    aScore = int(round((tempo * 100) + (EffMgn / 2.0)))
    bScore = int(round((tempo * 100) - (EffMgn / 2.0)))
    if (verbose):
        print ("Score({0}) {1}".format(teama["Team"], aScore), "vs. Score({0}) {1}".format(teamb["Team"], bScore))
    return aScore, bScore

def Line(teama, teamb, verbose = True, homeAdvantage = 7.897, homeTeam = 'none'):
    tempo = Tempo(teama, teamb, False)
    if (verbose):
        print ("Line(tempo) {0}".format(tempo * 100))
    EMdiff = (float(teama['S&P+M']) - float(teamb['S&P+M'])) * tempo
    EffMgn = 0
    if homeTeam == teama["Team"]:
        EffMgn = EMdiff + homeAdvantage
    elif homeTeam == teamb["Team"]:
        EffMgn = EMdiff - homeAdvantage
    else:
        EffMgn = EMdiff
    if (verbose):
        print ("Line(efficiency margin) {0}".format(EffMgn))
    return EffMgn

def Calculate(first, second, neutral, verbose):
    if (verbose):
        if (neutral):
            info = "{0} verses {1} at a neutral location".format(first, second)
            print (info)
        else:
            info = "Visiting team: {0} verses Home team: {1}".format(first, second)
            print (info)

    teama, teamb = findTeams(first, second, verbose = verbose)
    if (not teama or not teamb):
        return {}
    if (not neutral):
        chancea, chanceb =  Chance(teama, teamb, homeTeam = teamb["Team"], verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
        line = Line(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
    else:
        chancea, chanceb =  Chance(teama, teamb, verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose)
        line = Line(teama, teamb, verbose = verbose)

    tempo = Tempo(teama, teamb, verbose = verbose)

    dict_score = {'teama':first, 'scorea':"{0}".format(scorea), 'chancea':"{0}%".format(chancea) ,'teamb':second, 'scoreb':"{0}".format(scoreb), 'chanceb':"{0}%".format(chanceb), 'line':int(round(line)), 'tempo':"{0}".format(int(round(tempo * 100))) }
    if (verbose):
        print ("Calculate(dict_score) {0}".format(dict_score))
    return dict_score
