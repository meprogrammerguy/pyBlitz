#!/bin/bash
title="pyBlitz-Predictor"
location="$PWD/data"
cd $location

IFS=$(echo -en "\n\b")
away_team=$(yad --completion --entry="" --entry-label="Away Team" --title=$title $(cat $PWD/teams.txt) |\
	while IFS= read -r cmd;
    do
        away_team=${cmd}
        echo ${away_team}
    done)
away_button=$?
echo "button: ${away_button}"
echo "data: ${away_team}"
home_team=$(yad --completion --entry="" --entry-label="Home Team" --title=$title $(cat $PWD/teams.txt) |\
	while IFS= read -r cmd;
    do
        home_team=${cmd}
        echo ${home_team}
    done)
home_button=$?
echo "button: ${home_button}"
echo "data: ${home_team}"
team_text=$(echo "${away_team} @ ${home_team}")
form=$(yad --form --text="${team_text//&/&amp;}" --text-align center \
	--title=$title --field="Verbose":CHK \
	--field="Neutral Field":CHK)
form_button=$?
echo "form: ${form}"
