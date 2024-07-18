for item in dict_merge.values():
    teamrankings = pyBlitz.CleanString(item['teamrankings'])
    team = pyBlitz.CleanString(item['BPI'])
    
    row_team = []
    for row in dict_teamrankings.values():
        if(row['Team'].lower().strip()==teamrankings.lower().strip()):
            row_team = row  
            break

    for row in dict_bpi.values():
        if(row['School'].lower().strip()==team.lower().strip() and row['Class'].upper().strip()=="DIVISION 1  FBS"):
            index+=1
            IDX.append(str(index))
            A.append(team)
            B.append(teamrankings)
            if (row_team):
                E.append(row_team['PLpG3'])
                F.append(row_team['PTpP3'])
                G.append(row_team['OPLpG3'])
                H.append(row_team['OPTpP3'])
            else:
                E.append("0")
                F.append("0")
                G.append("0")
                H.append("0")
            C.append(row['Ranking'])
            D.append(row['Class'])
            break

