#!/bin/bash
#
# scrape pages to a test location
#   if page is there the scraper will go there instead of "live"
#

cd $HOME
test_location="$HOME/git/pyBlitz/test/pages"

#
# scrape_abbreviations.py
#   scrape needs last years schedule files
#

year=$(date +%Y)
year=$[year - 1]
abbrev_schedule="$test_location/schedule/$year"
cd $test_location
mkdir -p $abbrev_schedule
cd $abbrev_schedule

type=2 
count=0
while true
do
    count=$[count + 1]
    week=$(printf "%02d" $count)
    curl -H  "Accept: application/json+v3" \
        "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
        -o "w$week-y$year-t$type.html" # | python -m json.tool
    test=$(cat "/home/jsmith/git/pyBlitz/test/pages/schedule/2023/w$week-y$year-t$type.html" | grep ">No Data Available<")
    if [[ $test ]]
    then
        echo "week: $week I am done"
        rm "/home/jsmith/git/pyBlitz/test/pages/schedule/2023/w$week-y$year-t$type.html"
        break
    fi
done
#
# bowl games scrape
#
week=01
type=3
curl -H "Accept: application/json+v3" \
    "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
    -o "w$week-y$year-t$type.html" # | python -m json.tool
    
curl -H "Accept: application/json+v3" \
    "https://www.espn.com/college-football/team/_/id/103" \
    -o "boston-college.html" # | python -m json.tool

curl -H "Accept: application/json+v3" \
    "https://www.espn.com/college-football/game/_/gameId/401539475/oregon-washington" \
    -o "oregon-washington.html" # | python -m json.tool
    
    
# https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/alabama
# https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
# https://www.espn.com/college-football/game/_/gameId/401539475/oregon-washington