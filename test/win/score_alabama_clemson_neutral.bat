echo off
rem Test #2  Alabama vs. Clemson at a neutral venue
rem
.\scrape_outsiders.py
.\scrape_teamrankings.py
.\combine_stats.py 
.\score_matchup.py --first="alabama" --second="clemson" --neutral --verbose
