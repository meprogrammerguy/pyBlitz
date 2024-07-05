#!/bin/bash
#
# scrape pages to a test location
#   if page is there the scraper will use test data instead of "live"
#

cd $HOME
test_location="$HOME/git/pyBlitz/test/pages"
test_data="All"
# valid: All, Teams, 

#
# scrape_teams.py
#   scrape needs last years schedule files
#
if [ $test_data == "All" ] || [ $test_data == "Teams" ]
then
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
        curl -H "Accept: application/json+v3" \
            "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
            -o "w$week-y$year-t$type.html"
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
        -o "w$week-y$year-t$type.html"
#
# alabama json scrape
#
    curl -H "Accept: application/json+v3" \
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/alabama" \
        -o "alabama.json"
fi