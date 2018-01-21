echo off
rem Test #3 Clemson (visitor) Alabama (home)
rem 
.\scrape_bettingtalk.py
.\scrape_bornpowerindex.py
.\scrape_teamrankings.py
.\combine_stats.py 
.\score_matchup.py --first="clemson" --second="alabama" --verbose
