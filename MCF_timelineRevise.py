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
    
    # Combine travel segments so that each trip is just ONE travel activity
    for tlU in tl:
        a = tlU['activities'] # activities per user
        n = len(a)

        i = 0 # activity index
        while i < n - 2: 
                
            if a[i]['activityType'] == "travel":
                j = i + 1
                while (a[j]['activity'] == "Change Mode/Transfer" or a[j]['activityType'] == "travel") and j < n - 1:
                    print(a[j]['activity'])
                    j += 1
#                    
#                if a[i]['activity'] == a[i+2]['activity'] and a[i+1]['activityType'] == "travel" and a[i+1]['distance'] < dT:
#                    if a[i]['activity'] in activitiesToCombine:
#                        # combine relevant attributes of adjacent stops
#                        a[i]['endTime'] = a[i+2]['endTime']
#                        a[i]['duration'] = float(a[i]['endTime'] - a[i]['startTime'] )/60 # duration in minutes  
#                        a[i]['endDate'] = a[i+2]['endDate']
#                        #print a[i+1]
#                        a.pop(i+1) # remove travel activity
#                        a.pop(i+1) # remove second stop activity
#                        n = n - 2                        
#                        combined += 1
#                    else:
#                        print a[i]['activity'] + " stopID " + a[i]['stopID'] + ": not combined"

            i += 1
            
#    print "number of stops combined: " + str(combined*2)
        

    return tl
