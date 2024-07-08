#!/bin/bash
#
# script to scrape schedule by year
#   if page is there the scraper will use test data instead of "live"
#
the_count=( "$#" )
the_args=( "$@" )
if [ $the_count -gt 1 ]
then
    echo "      test_scrape_year.sh"
    echo " "
    echo "no arguments: current year, one argument: year in yyyy"
    echo " "
    echo "... exiting"
    exit 1
fi
if [ $the_count -eq 0 ]
then
    year=$(date +%Y)
fi
if [ $the_count -eq 1 ]
then
    year=$the_args
fi

cd $HOME
test_location="$HOME/git/pyBlitz/test"
schedule="$test_location/pages/schedule/$year"
cd $test_location
mkdir -p $schedule
cd $schedule

type=2 
count=0
while true
do
    count=$[count + 1]
    week=$(printf "%02d" $count)
    curl -H "Accept: application/json+v3" \
        "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
        -o "w$week-y$year-t$type.html"
        
    test=$(cat "$HOME/git/pyBlitz/test/pages/schedule/$year/w$week-y$year-t$type.html" | grep ">No Data Available<")
    if [[ $test ]]
    then
        echo "week: $week I am done"
        rm "$HOME/git/pyBlitz/test/pages/schedule/$year/w$week-y$year-t$type.html"
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
    "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/ala" \
    -o "ala.json"

echo " "
echo "done."