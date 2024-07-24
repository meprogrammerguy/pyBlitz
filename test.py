#!/usr/bin/env python3

import sys, getopt
import pdb

import settings

def main(argv):
    print ("Run all Tests Tool")
    print ("**************************")
    print ("\tDirectory Location: {0}".format(settings.data_path))
    print ("===")
    print ("	A good time to run is if you corrected any merge spreadsheets")
    print ("	or possibly at the beginning of each season")
    print (" * Remember: the fewer the warnings the better and more accurate * ")
    print ("    Are the predictions")
    print ("===")
    print ("**************************")
    RunTests()
    print ("all tests done.")

def RunTests():
    import test_teamrankings
    import test_bornpowerindex
    import test_schedule
    import test_merge
    import test_stats

if __name__ == "__main__":
  main(sys.argv[1:])
