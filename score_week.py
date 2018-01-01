#!/usr/bin/env python3

import sys, getopt
import gamePredict
import pyMadness
from collections import OrderedDict
import json
import csv
import pdb
import os.path

def main(argv):
    stat_file = "stats.json"
    bracket_file = "bracket.json"
    merge_file = "merge.csv"
    output_file = "predict.csv"
    input_file = "predict.csv"
    verbose = False
    test = False
    gamepredict = False
    try:
        opts, args = getopt.getopt(argv, "hs:b:m:o:i:vtg", ["help", "stat_file=", "bracket_file=", "merge_file=", "output_file=", 
                                         "input_file=", "verbose", "test", "gamepredict"])
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
        elif o in ("-g", "--gamepredict"):
            gamepredict = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit
        elif o in ("-s", "--stat_file"):
            stat_file = a
        elif o in ("-b", "--bracket_file"):
            bracket_file = a
        elif o in ("-b", "--merge_file"):
            merge_file = a
        elif o in ("-o", "--output_file"):
            output_file = a
        elif o in ("-i", "--input_file"):
            input_file = a
        else:
            assert False, "unhandled option"
    if (test):
        testResult = pyMadness.Test(verbose)
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        PredictTournament(stat_file, bracket_file, merge_file, input_file, output_file, verbose, gamepredict)
        print ("{0} has been created.".format(output_file))

def usage():
    usage = """
    -h --help                 Prints this help
    -v --verbose              Increases the information level
    -s --stat_file            stats file                      (json file format)
    -b --bracket_file         bracket file                    (json file format)
    -m --merge_file           merge file                      (csv/spreadsheet file format)
    -i --input_file           input file gets pick overrides  (csv/spreadsheet file format)
    -o --output_file          output file                     (csv/spreadsheet file format)
    -g --gamepredict          obtain data from gamepredict.us (default is False, runs slower)
    -t --test                 runs test routine to check calculations
    """
    print (usage) 

def PredictTournament(stat_file, bracket_file, merge_file, input_file, output_file, verbose, gamepredict):
    print ("Tournament Prediction Tool")
    print ("**************************")
    print ("Statistics file: {0}".format(stat_file))
    print ("Brackets   file: {0}".format(bracket_file))
    print ("Team Merge file: {0}".format(merge_file))
    print ("Input      file: {0}".format(input_file))
    print ("Output     file: {0}".format(output_file))
    if (gamepredict):
        print (" ")
        print ("===> (data will come from gamepredict.us) <===")
        print (" ")
    print ("**************************")
    list_picks = []
    if (os.path.exists(input_file)):
        file = input_file
        with open(file) as input_file:
            reader = csv.DictReader(input_file)
            for row in reader:
                if (row["ScoreA"] >= row["ScoreB"] and row["Pick"] == "TeamB"):
                    list_picks.append([row["Index"], row["Pick"]])
                elif (row["ScoreA"] < row["ScoreB"] and row["Pick"] == "TeamA"):
                    list_picks.append([row["Index"], row["Pick"]])
    if (len(list_picks) == 0):
        print ("No pick Overrides")
    elif (len(list_picks) == 1):
        print ("Overriding one calculated pick")
    else:
        print ("Overriding {0} calculated pick(s)".format(len(list_picks)))
    dict_merge = []
    if (not os.path.exists(merge_file)):
        print ("merge file is missing, run the merge_teams tool to create")
        exit()
    file = merge_file
    with open(file) as merge_file:
        reader = csv.DictReader(merge_file)
        for row in reader:
            dict_merge.append(row)
    if (not os.path.exists(bracket_file)):
        print ("brackets file is missing, run the scrape_bracket tool to create")
        exit()
    file = bracket_file
    with open(file) as bracket_file:
        dict_bracket = json.load(bracket_file, object_pairs_hook=OrderedDict)
    for item in dict_bracket.values():
        teama, teamb = FindTeams(item["TeamA"], item["TeamB"], dict_merge)
        item[2] = teama
        item[6] = teamb
    if (not os.path.exists(stat_file)):
        print ("statistics file is missing, run the scrape_stats tool to create")
        exit()
    file = stat_file
    with open(file) as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)
    dict_predict = []
    dict_predict = LoadPredict(dict_predict, dict_bracket) 
    for round in range(0, 7):
        dict_predict = PredictRound(round, dict_predict, gamepredict, verbose)
        dict_predict = PromoteRound(round, dict_predict, list_picks)
    predict_sheet = open(output_file, 'w', newline='')
    csvwriter = csv.writer(predict_sheet)
    count = 0
    for row in dict_predict:
        csvwriter.writerow(row)
    predict_sheet.close()

def FindTeams(teama, teamb, dict_merge):
    FoundA = ""
    FoundB = ""
    for item in dict_merge:
        if (teama == item["bracket team"]):
            FoundA = item["stats team"]
            if (item["fixed stats team"]):
                FoundA = item["fixed stats team"]
        if (teamb == item["bracket team"]):
            FoundB = item["stats team"]
            if (item["fixed stats team"]):
                FoundB = item["fixed stats team"]
        if (FoundA and FoundB):
            break
    return FoundA, FoundB

def LoadPredict(dict_predict, dict_bracket):
    dict_predict.append(["Index", "SeedA", "TeamA", "ChanceA", "ScoreA",
                                      "SeedB", "TeamB", "ChanceB", "ScoreB", "Region", "Venue", "Round", "Pick"])
    index = 0
    for item in dict_bracket.values():
        if (item["Round"] != "Round"):
            index += 1
            dict_predict.append([index, item["SeedA"], item[2], "?%", "?",
                                        item["SeedB"], item[6], "?%", "?", item["Region"], item["Venue"], item["Round"], "?"])
    return dict_predict

def PredictRound(round, dict_predict, gamepredict, verbose):
    for item in dict_predict:
        if (item[11] != "Round" and (round == int(item[11]))): #Round
            if (gamepredict):
                dict_score = gamePredict.Score(item[2], item[6], True, verbose) #This will be slow
            else:
                dict_score = pyMadness.Calculate(item[2], item[6], True, verbose)
            item[3] = dict_score["chancea"]
            item[4] = dict_score["scorea"]
            item[7] = dict_score["chanceb"]
            item[8] = dict_score["scoreb"]
            if (int(item[4]) >= int(item[8])):
                item[12] = "TeamA"
            else:
                item[12] = "TeamB"
    return dict_predict

def PromoteRound(round, dict_predict, list_picks):
    if (int(round) != 6):
        promote = []
        for item in dict_predict:
            if (item[0] != "Index" and int(round) == int(item[11])):
                slot, index = GetNextIndex(item[0])
                flip = False
                #pdb.set_trace()
                for pick in list_picks:
                    if (int(pick[0]) == int(item[0])):
                        flip = True
                        #pdb.set_trace()
                        item[12] = pick[1]
                        break
                if (int(item[4]) >= int(item[8])):
                    if (flip):
                        print ("picking {0} over {1} in round {2} in match {3}".format(item[6], item[2], item[11], item[0]))
                        promote.append([index, slot, item[6]])
                    else:
                        promote.append([index, slot, item[2]])
                else:
                    if (flip):
                        print ("picking {0} over {1} in round {2} in match {3}".format(item[2], item[6], item[11], item[0]))
                        promote.append([index, slot, item[2]])
                    else:
                        promote.append([index, slot, item[6]])

        for item in dict_predict:
            for team in promote:
                if (team[0] == item[0]):
                    if (team[1] == 1):
                        item[2] = team[2]
                    else:
                        item[6] = team[2]
    return dict_predict 

def GetNextIndex(index):
    # Hundreds position is slot number 1 or 2 rest of the number is the index
    next_slot = [254, 205, 209, 235, # First Four 
                 113, 213, 114, 214, 115, 215, 116, 216, 117, 217, 118, 218, 119, 219, 165, # East
                 128, 228, 129, 229, 130, 230, 131, 231, 132, 232, 133, 233, 134, 234, 265, # West
                 143, 243, 144, 244, 145, 245, 146, 246, 147, 247, 148, 248, 149, 249, 166, # Midwest
                 158, 258, 159, 259, 160, 260, 161, 261, 162, 262, 163, 263, 164, 264, 266, # South
                 167, 267] # Final Four

    slot = int(next_slot[index - 1] / 100)
    return slot, (next_slot[index - 1] - (slot * 100))

if __name__ == "__main__":
  main(sys.argv[1:])
