#!/usr/bin/env python3

import sys, getopt
import os.path
from datetime import datetime

import pyBlitz

def CurrentStatsFile(filename):
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshStats():
    import scrape_bettingtalk
    import scrape_bornpowerindex
    import scrape_teamrankings
    import scrape_abbreviations
    import combine_merge
    import combine_stats
    import measure_results

def main(argv):
    first = ""
    second = ""
    verbose = False
    neutral = False
    test = False
    try:
        opts, args = getopt.getopt(argv, "hf:s:vnt", ["help", "first=", "second=", "verbose", "neutral","test"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--neutral"):
            neutral = True
        elif o in ("-t", "--test"):
            test = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit
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
        testResult = pyBlitz.Test(verbose)
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        if (not first and not second):
            print ("you must input the team names to run this tool, (first and second arguments)")
            exit()
        if (not CurrentStatsFile("data/stats.json")):
            RefreshStats()
        dict_score = {}
        dict_score = pyBlitz.Calculate(first, second, neutral, verbose)

def usage():
    usage = """
    -h --help                 Prints this
    -v --verbose              Increases the information level
    -f --first                First Team  (The Away Team)
    -s --second               Second Team (The Home Team)
    -n --neutral              Playing on a neutral Field
    -t --test                 runs test routine to check calculations
    """
    print (usage) 

if __name__ == "__main__":
  main(sys.argv[1:])
