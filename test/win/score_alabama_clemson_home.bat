echo off
rem Test #1 Alabama (visitor) Clemson (home)
rem 
.\scrape_outsiders.py
.\scrape_teamrankings.py
.\combine_stats.py 
.\score_matchup.py --first="alabama" --second="clemson" --verbose
