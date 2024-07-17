    #if not found:
        #teams.append(team)
        #abbrs.append(abbr)
        #over.append(" ")

for item in teams_json["displayName"]:
    team = str(teams_json["displayName"][item]).strip()
    abbr = str(teams_json["abbreviation"][item]).strip()
    found = False
    for bpi_item in bpi_json["abbr"]:
        bpi_abbr = str(bpi_json["abbr"][bpi_item]).strip()
        bpi_team = str(bpi_json["team"][bpi_item]).strip()
        bpi = str(bpi_json["bpi"][bpi_item]).strip()
        con = str(bpi_json["confidence"][bpi_item]).strip()
        bclass = str(bpi_json["class"][bpi_item]).strip()
        if abbr == bpi_abbr:
            found = True
            bpi_teams.append(bpi_team)
            bpis.append(bpi)
            cons.append(con)
            classes.append(bclass)
       
    teams.append(team)
    abbrs.append(abbr)
    over.append(" ")
    index+=1
    IDX.append(index)
    if not found:
        bpi_teams.append(" ")
        bpis.append(" ")
        
        
        classes.append(" ")
        cons.append(0)

for i in range(len(teams), len(bpi_teams)):
        teams.append(" ")
        abbrs.append(" ")
        over.append(" ")
        index+=1
        IDX.append(index)
   











