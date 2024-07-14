

        dateidx = 0
        index = 0
        IDX=[]
        Y=[]
        A=[]
        B=[]
        C=[]
        D=[]
        F=[]
        G=[]
        for table in tables:
            teams=table.findAll('abbr')
            home=table.findAll('td', {"class": "home"})
            scores=table.findAll('td')
            E=[]
            for score in scores:
                data = score.find(text=True)
                if (data is not None and ("Canceled" in data or "Postponed" in data)):
                    E.append(data)
                elif data is not None and ',' in data and num_there(data):
                    E.append(data)
                else:
                    E.append("?")
            if loop == len(pages):
                for item in range(2, len(E), 7):
                    F.append(E[item])
            else:
                for item in range(2, len(E), 6):
                    F.append(E[item])
            neutral=table.findAll('tr', {'class':['odd', 'even']})
            line = 0
            count = 0
            for team in teams:
                if (line % 2 == 0):
                    if dateidx < len(dates):
                        theDate = dates[dateidx].find(text=True)
                    else:
                        theDate = "?"
                    A.append(theDate)
                    if "January" not in theDate: 
                        Y.append(year)
                    else:
                        Y.append(year + 1)
                    B.append(pyBlitz.CleanString(team['title']))
                    if loop != len(pages):
                        try:
                            if (neutral[count]['data-is-neutral-site'] == 'true'):
                                C.append("Neutral")
                            else:
                                C.append("?")
                        except KeyError as e:
                            C.append("Neutral")
                    else:
                        C.append("Neutral")
                    if (index < len(F)):
                        G.append(F[index])
                    else:
                        G.append("?")
                    count+=1
                    index+=1
                    IDX.append(index)
                else:
                    D.append(pyBlitz.CleanString(team['title']))
                    if (C[-1] == '?'):
                        C[-1] = D[-1] 
                line+=1
            dateidx+=1
        df=pd.DataFrame(IDX, columns=['Index'])
        df['Year']=Y
        df['Date']=A
        df['TeamA']=B
        df['Home']=C
        df['TeamB']=D
        df['Score']=G
        if (not df.empty):    
            filename = "{0}sched{1}.json".format(path, loop)
            with open(filename, 'w') as f:
                f.write(df.to_json(orient='index'))

            with open(filename) as sched_json:
                dict_sched = json.load(sched_json, object_pairs_hook=OrderedDict)

            filename = "{0}sched{1}.csv".format(path, loop)
            sched_sheet = open(filename, 'w', newline='')
            csvwriter = csv.writer(sched_sheet)
            count = 0
            for row in dict_sched.values():
                if (count == 0):
                    header = row.keys()
                    csvwriter.writerow(header)
                    count += 1
                csvwriter.writerow(row.values())
            sched_sheet.close()