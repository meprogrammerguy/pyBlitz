        for item in range(len(SCHED[cdate])):
            print ("length: " + str(len(SCHED[cdate])))
            print (item)
            #pdb.set_trace()
            print ("All: " + str(SCHED[cdate]))
            pdb.set_trace()
            for items in SCHED[cdate][0::16]:
                pdb.set_trace()
            #the_line=[]
            #for i in range(16):
                the_line.append(SCHED[cdate][i])
                the_sched = SCHED[cdate][i]
                print (" *** ")
                print ("one row: " + the_sched)
                pdb.set_trace()
                team1 = SCHED[cdate][1] + " " + SCHED[cdate][2] + " " + SCHED[cdate][3]
                team1 = team1.replace('PMOpenSpreadTotalML', '')
                the_best = pyBlitz.GetFuzzyBest(team1, matches, returned)
                print ("team 1: " + team1)
                print ("the_best: " + str(the_best))
                print ("***")
                pdb.set_trace()
                if the_best[1] == " ":
                    pdb.set_trace()
                pdb.set_trace()
            pdb.set_trace()
            cteam1.append(the_best[1])
            #team2 = SCHED[cdate][10] + " " + SCHED[cdate][11] + " " + SCHED[cdate][12] + " " + SCHED[cdate][13]
            #team2 = team2.replace('PMOpenSpreadTotalML', '')
            #the_best = pyBlitz.GetFuzzyBest(team2, matches, teams_json["abbreviation"])
            #print (the_best)
            #pdb.set_trace()
            #cabbr2.append(the_best[1])
            #pdb.set_trace()
            cdates.append(cdate)
            index+=1
            pdb.set_trace()
        pdb.set_trace()
