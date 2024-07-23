#!/bin/bash
#
# script to scrape schedule by year
#   if page is there the scraper will use test data instead of "live"
#
green='\033[0;32m'
red='\033[0;31m'
NC='\033[0m'
the_count=( "$#" )
the_args=( "$@" )
if [ $the_count -gt 1 ]
then
    echo -e "      ${red}test_scrape_year.sh${NC}"
    echo " "
    echo -e "${red}no arguments: current year, one argument: year in yyyy${NC}"
    echo " "
    echo -e "${red}... exiting${NC}"
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
echo -e "           ${green}weekly schedule scrape${NC}"
while true
do
    count=$[count + 1]
    week=$(printf "%02d" $count)
    curl -H "Accept: application/json+v3" \
        "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
        -o "-w$week-y$year-t$type.html"
        
    test=$(cat "$HOME/git/pyBlitz/test/pages/schedule/$year/-w$week-y$year-t$type.html" | grep ">No Data Available<")
    if [[ $test ]]
    then
        echo "week: $week I am done"
        rm "$HOME/git/pyBlitz/test/pages/schedule/$year/-w$week-y$year-t$type.html"
        break
    fi
done
#
# bowl games scrape
#
echo -e "           ${green}bowl games scrape${NC}"
week=01
type=3
curl -H "Accept: application/json+v3" \
    "https://www.espn.com/college-football/schedule/_/week/$week/year/$year/seasontype/$type" \
    -o "-w$week-y$year-t$type.html"
#
# alabama json scrape
#
echo -e "           ${green}alabama team scrape${NC}"
curl -H "Accept: application/json+v3" \
    "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/ala" \
    -o "ala.json"
#
# espn odds scrape
#
echo -e "           ${green}ESPN odds scrape${NC}"
curl -H "Accept: application/json+v3" "https://www.espn.com/college-football/odds" -o "odds.html"
#
# bornpowerindex scrape
#
echo -e "           ${green}bornpowerindex pages scrape${NC}"
for i in $(seq 1 6);
do
	curl  -d "getClassName=on&class=$i&sort=team" \
    -H "Accept: application/json+v3text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" \
    -H "Host: www.bornpowerindex.com" \
    -H "Connection: keep-alive" \
    -H "Content-Length: 33" \
    -H "Cache-Control: max-age=0" \
    -H "Origin: http://www.bornpowerindex.com" \
    -H "Upgrade-Insecure-Requests: 1" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36" \
    -H "DNT: 1" \
    -H "Referer: http://www.bornpowerindex.com/M_COL_FB_CLASS.shtml" \
    -H "Accept-Encoding: gzip, deflate" \
    -H "Accept-Language: en-US,en;q=0.9" \
    -X POST "http://www.bornpowerindex.com/cgi-bin/DBRetrieve.pl" \
    -o "bornpowerindex$i.html"
done
#
# scrape teamrankings pages
#
echo -e "           ${green}teamrankings pages scrape${NC}"
curl -H "Accept: application/json+v3" \
    "https://www.teamrankings.com/college-football/stat/plays-per-game" \
    -o "teamrankings_ppg.html"
curl -H "Accept: application/json+v3" \
    "https://www.teamrankings.com/college-football/stat/points-per-play" \
    -o "teamrankings_ppp.html"
curl -H "Accept: application/json+v3" \
    "https://www.teamrankings.com/college-football/stat/opponent-points-per-game" \
    -o "teamrankings_oppg.html"
curl -H "Accept: application/json+v3" \
    "https://www.teamrankings.com/college-football/stat/opponent-points-per-play" \
    -o "teamrankings_oppp.html"

echo " "
echo -e "${green}done.${NC}"
