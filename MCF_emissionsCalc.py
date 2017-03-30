
# activityEmissionsCalc is separate function, so that we can calculate activity emissions one by one
# arguments:
# a: activity label, d: distance [meters] or duration [minutes], em: emissions database
# return: emissions [kg] or "unknown" if activity label is not in em (emissions database)
def activityEmissionsCalc(a, d, em):

    m = next((e for e in em if e['activity'] == a), None)
    if m is not None and 'co2KG' in m:
        
        emKg = float(float(m['co2KG']) * float(d))
    else:
        emKg = "unknown"
        
    return emKg


def timelineEmissionsCalc(tl, em):

    for tlU in tl:
        for a in tlU['activities']:
            a['emissionsKg'] = 0
             
            if a['activityType'] == "stop":
                d = a['duration'] #duration in minutes
                a['emissionsKg'] = activityEmissionsCalc(a['activity'], d, em)
            elif a['activityType'] == "travel":
                if 'travelModeDist' in a:
                    for key, dS in a['travelModeDist'].items(): # use iteritems for py2.7
                        d = float(dS)/1000 #distance in kilometers for emissions calc
                        a['emissionsKg'] += activityEmissionsCalc(key, d, em)
                else:
                    d = float(a['distance'])/1000 #distance in kilometers for emissions calc
                    a['emissionsKg'] = activityEmissionsCalc(a['activity'], d, em)                  
            else:                
                a['emissionsKg'] = "unknown" #unknown if activityType == "gap" or other
    
    return tl



# TO DO: revise per new activityLookup.csv format
def timelineEmissionsSummaries(tl):

#    emS = []
#    emS['Total'] = 0
#    
#    activityLabel = ['Home','Work','Work-Related Business','Education','Pick Up/Drop Off', \
#    'Personal Errand/Task','Meal/Eating Break','Shopping','Social','Recreation','Entertainment', \
#    'Sports/Exercise','To Accompany Someone','Other Home','Medical/Dental (Self)','Other (stop)','Change Mode/Transfer']
#    activityLabel.extend(['Car/Van','Taxi','Bus','Other (mode)','Motorcycle/Scooter','LRT/MRT','Bicycle','Foot'])   
#
#    for a in activityLabel:
#        emS[a] = 0
#        
#    for day in tl:
#    
#        for t in day['times']:
#            if t['activityType'] == "stop":
#                duration = (t['ending_time'] - t['starting_time'])/1000/60 #duration in minutes
#                t['emissionsKg'] = emissionsCalc(t['activity'], duration)
#            if t['activityType'] == "travel":
#                if t['pl'] != "unknown" and t['pl'] != "continued":
#                    t['emissionsKg'] = emissionsCalc(t['activity'], t['distance']) 
#                else:
#                    t['emissionsKg'] = 0
#            else:                
#                t['emissionsKg'] = 0
#
#
#    for a in activityLabel:
#        emS['Total'] += emS[a]
    
    return emS
