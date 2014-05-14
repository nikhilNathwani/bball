    #repeat above for team_misc stats
    team_misc_div= query_soup.find('div', {"class" : "table_container", "id" : "div_team_misc"})
    team_misc_header= team_misc_div.find("thead").findAll('tr')[-1] #first tr is an "over-header" to be ignored
    indices= []
    not_scale_indices= []
    for i,elem in enumerate(team_misc_header.findAll('th')): 
        if elem['data-stat'] not in statsToIgnore:
            indices += [i]
        if elem['data-stat'] in statsToNotScale:
            not_scale_indices += [i]

    team_misc_stats= team_misc_div.find("tbody").findAll("tr")
    for row in team_misc_stats:
        arraysToAddTo= [all_stats]
        stats= row.findAll('td')
        isLgRank= False
        if stats[0].text.encode("ascii","ignore")=="Lg Rank":
            arraysToAddTo += [only_league_ranks]
            isLgRank= True
        else: 
            arraysToAddTo += [only_raw_values]
        for j in indices:
            for arr in arraysToAddTo:
                value= float(stats[j].text.encode("ascii","ignore"))
                scale= 1
                if j not in not_scale_indices: #meaning j needs scaling
                    if year==1999 and isLgRank==False: scale= float(82)/float(50)
                    if year==2012 and isLgRank==False: scale= float(82)/float(66)
                arr += [value * scale]
                
id, 