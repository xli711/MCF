# NOTE: Ensure that these functions remain compatible with any MCF "timeline" data dictionary
# NOTE: Run this routine on the timeline BEFORE calculating emissions
# arguments:
# tl: timeline data dictionary, dT: distance tolerance for combining stops
def stopsRevise(tl, dT, activitiesToCombine):

    combined = 0
    
    # Combine nearby, sequential stops of the same type
    for tlU in tl:
        a = tlU['activities']
        n = len(a)

        i = 0 # activity index
        while i < n - 2: 
                
            # TO DO: make compatible with interval format, which can have stops without travel activities between stops
            # TO DO: revise the stopIDs for travel activities, based on combined stops?
            if a[i]['activityType'] == "stop":
                if a[i]['activity'] == a[i+2]['activity'] and a[i+1]['activityType'] == "travel" and a[i+1]['distance'] < dT:
                    if a[i]['activity'] in activitiesToCombine:
                        # combine relevant attributes of adjacent stops
                        a[i]['endTime'] = a[i+2]['endTime']
                        a[i]['duration'] = float(a[i]['endTime'] - a[i]['startTime'] )/60 # duration in minutes  
                        a[i]['endDate'] = a[i+2]['endDate']
                        #print a[i+1]
                        a.pop(i+1) # remove travel activity
                        a.pop(i+1) # remove second stop activity
                        n = n - 2                        
                        combined += 1
                    #else:
                        #print a[i]['activity'] + " stopID " + a[i]['stopID'] + ": not combined"

            i += 1
            
    print("number of stops combined: " + str(combined*2))
    return tl

def travelRevise(tl):
   #revise TRAVEL activities in order to reduce travel sequence types (e.g. walk-mrt-walk)
    combined = 0
    travelModeDist = 0
    
    # Combine travel segments so that each trip is just ONE travel activity
    for tlU in tl:
        a = tlU['activities'] # activities per user
        n = len(a)

        i = 0 # activity index
        while i < n - 2: 
                
            if a[i]['activityType'] == "travel":
                j = i + 1
                while (a[j]['activity'] == "Change Mode/Transfer" or a[j]['activityType'] == "travel") and j < n :
                    #print(a[j]['activity'] + " " + a[j]['stopID'])
                    j += 1

                if j > i + 1:
                    distance = 0
                    transfers = 0
                    transferDuration = 0
                    travelModeDist = dict.fromkeys(['Car/Van','Taxi','Bus','Other (travel)','Motorcycle/Scooter','LRT/MRT','Bicycle','Foot'],0)
                    
                    aFirst = dict(a[i])
                    a[i]['travelSegments'] = []
                    a[i]['travelSegments'].append({})
                    a[i]['travelSegments'][0] = aFirst
                    
                    for tS in range(i+1,j):
                        a[i]['travelSegments'].append({})
                        a[i]['travelSegments'][-1] = dict(a[tS])
                 
                    for tS in range(i,j):
                        # combine relevant attributes of adjacent travel segments
                        #print(str(i) + " " + str(tS-i) + " " + str(j))

                        
                        if a[tS]['activity'] == "Change Mode/Transfer":
                            transfers += 1
                            transferDuration += a[tS]['duration'] # duration in minutes 
                            
                        elif a[tS]['activityType'] == "travel":
                            travelModeDist[a[tS]['activity']] += a[tS]['distance']
                            distance += a[tS]['distance']
                        else:
                            print("Error in travel segment aggregation")
                        
                    a[i]['endTime'] = a[j-1]['endTime']
                    a[i]['endDate'] = a[j-1]['endDate']
                    a[i]['lat'] = a[j-1]['lat']
                    a[i]['lon'] = a[j-1]['lon']
                    a[i]['postalCode'] = a[j-1]['postalCode']
                    a[i]['stopID'] = a[j-1]['stopID']
                    a[i]['duration'] = float(a[j-1]['endTime'] - a[i]['startTime'])/60 # duration in minutes  
                    a[i]['distance'] = distance
                    a[i]['travelModeDist'] = dict(travelModeDist)
                    a[i]['transfers'] = transfers
                    a[i]['transferDuration'] = transferDuration
                     
                    if a[i]['travelModeDist']['LRT/MRT'] > 0:
                        a[i]['activity'] = "LRT/MRT"
                    elif a[i]['travelModeDist']['Bus'] > 0: 
                        a[i]['activity'] = "Bus" 
                    elif a[i]['travelModeDist']['Car/Van'] > 0: 
                        a[i]['activity'] = "Car/Van" 
                    elif a[i]['travelModeDist']['Taxi'] > 0: 
                        a[i]['activity'] = "Taxi" 
                    elif a[i]['travelModeDist']['Motorcycle/Scooter'] > 0: 
                        a[i]['activity'] = "Motorcycle/Scooter" 
                    elif a[i]['travelModeDist']['Other (travel)'] > 0: 
                        a[i]['activity'] = "Other (travel)" 
                    elif a[i]['travelModeDist']['Bicycle'] > 0: 
                        a[i]['activity'] = "Bicycle" 
                    elif a[i]['travelModeDist']['Foot'] > 0: 
                        a[i]['activity'] = "Foot" 
       
        
                    print(a[i]['activity'] + " " + str(transfers))
                    print(a[i]['travelModeDist'])
                    
                    for tS in range(i+1,j):
                        a.pop(i+1) # remove travel and transfer activities                      
                    
                    combined += j - i
                    n = len(a)

            i += 1
            
    print ("number of travel segments combined: " + str(combined))
        

    return tl
