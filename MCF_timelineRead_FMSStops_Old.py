# Imports the OLD type of FMS data file (FMSStops.csv or stops_summary_xxxxxx.csv)
# For the new type of FMS data file (interval type), I will need to implement a new data import routine

# import other MCF functions:
from MCF_utilities import *

# TO DO: change timelineReadRevised in MCF_readRevisedFile to match the data dictionary structure below
# TO DO: add travel time info from FMS 'travel_summaries_xxxxxx.csv' to find gaps in activity logs
def timelineRead(stops, stopsPC, userSocio, dayBreakHour, timezone):
    # TO DO: implement activity breaks at dayBreakHour. Current: NO BREAKS
    # dayBreakHour: hour at which to separate the days/activities (midnight = 0); -1 for no breaks   
    dayBreakHour = 0
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    tl = [] # timeline dictionary
    iU = 0 # user index
    tl.append({})
    tl[iU]['userID'] = stops[0]['userID']    
    tl[iU]['activities'] = []
    
    n = len(stops)
    i = 0 # stop index
    while i < n:  
        
        # skip current stop row if it is a repeated stopID in FMS file
        if i < n-1:
            if stops[i]['stopID'] == stops[i+1]['stopID']: 
                i += 1
        
        # set up NEW USER if userID is different from current userID
        # Assume that stops are ordered by user IDs *** IMPORTANT
        if stops[i]['userID'] != tl[iU]['userID']:
            iU += 1
            tl.append({})
            tl[iU]['userID'] = stops[i]['userID']
            tl[iU]['activities'] = []
        
        a = tl[iU]['activities']
        
        # Convert FMS timestamps to Unix epoch timestamps
        if 'stopStart' in stops[i] and 'stopEnd' in stops[i]: # for older datasets
            stopStart = strToTime(stops[i]['stopStart'],timezone,0,False) 
            stopEnd = strToTime(stops[i]['stopEnd'],timezone,0,False) 
        elif 'startTime' in stops[i] and 'stopEnd' in stops[i]:
            stopStart = strToTime(stops[i]['startTime'],timezone,0,False) # newer datasets use 'startTime' label
            stopEnd = strToTime(stops[i]['endTime'],timezone,0,False) # newer datasets use 'endTime' label        
        else: 
            print("stopID " + str(stops[i]['stopID']) + ": start/stop time data fields not found")
            
        sTS = time.localtime(stopStart) # struct for start time  
        startDay = int(time.mktime(time.struct_time([sTS.tm_year,sTS.tm_mon,sTS.tm_mday,dayBreakHour,0,0,0,0,0])))
        eTS = time.localtime(stopEnd) # struct for end time time  
        #endDayLast = int(time.mktime(time.struct_time([eTS.tm_year,eTS.tm_mon,eTS.tm_mday,dayBreakHour,0,0,0,0,0])))

        stopEndPrevious = 0
        if len(a) == 0: # first activity for new user
            stopEndPrevious = startDay
        else:
            stopEndPrevious = a[-1]['endTime'] + 1
        
        # if the first stop does not begin at 00:00:00 or if travel gap, then insert GAP 
        # TO DO: check new FMS data formats to see how to account for gaps
        # TO DO: "none" check might only work for golden dataset
        if stops[i]['travelMode'] == "none" and stopStart > stopEndPrevious: 
            a.append({})
            a[-1]['activityType'] = "gap"
            a[-1]['activity'] = "gap"
            a[-1]['startTime'] = stopEndPrevious
            a[-1]['endTime'] = stopStart - 1
            
            sPrevTS = time.localtime(a[-1]['startTime'])
            eTS = time.localtime(a[-1]['endTime'])
            a[-1]['startDate'] = [sPrevTS.tm_year,sPrevTS.tm_mon,sPrevTS.tm_mday] 
            a[-1]['endDate'] = [eTS.tm_year,eTS.tm_mon,eTS.tm_mday] 
            
            a[-1]['startDay'] = days[sPrevTS.tm_wday] # day of activity start
            stopEndPrevious = a[-1]['endTime'] 

        if stops[i]['travelMode'] == "Other":
            stops[i]['travelMode'] = "Other (travel)"
        if stops[i]['stopType'] == "Other":
            stops[i]['stopType'] = "Other (stop)"
        if stops[i]['stopType'] == "--":
            stops[i]['stopType'] = "Other (stop)"        
        
        if len(a) == 0: # first activity for new user
            stopEndPrevious = startDay
        else:
            stopEndPrevious = a[-1]['endTime']
        
        # add travel activity first
        if stops[i]['travelMode'] != "none" and stopStart > startDay and stopStart >= stopEndPrevious:
            a.append({})
            a[-1]['stopID'] = stops[i]['stopID']
            a[-1]['stopIDprev'] = stops[i-1]['stopID'] # TO DO: revise for interval data 
            a[-1]['activityType'] = "travel"
            a[-1]['activity'] = stops[i]['travelMode'] 

            pcCurr = 0
            pcPrev = 0
            for stopPC in stopsPC:
                if stopPC['stopID'] == a[-1]['stopID']:
                    pcCurr = stopPC['postcode']  
                elif stopPC['stopID'] == a[-1]['stopIDprev']:
                    pcPrev = stopPC['postcode'] 
                
            a[-1]['postalCode'] = pcCurr
            a[-1]['postalCodePrev'] = pcPrev
            
            # When the timestamp does not include the Seconds vaule, travel activity time can be 0 minutes.
            # To compensate, insert a 58-second travel activity.
            if len(a) == 0: # first activity for new user
                a[-1]['startTime'] = startDay
            else:
                a[-1]['startTime'] = stopEndPrevious + 1          
            
            a[-1]['endTime'] = stopStart - 1
                
            sPrevTS = time.localtime(a[-1]['startTime'])
            ePrevTS = time.localtime(a[-1]['endTime'])
            a[-1]['startDate'] = [sPrevTS.tm_year,sPrevTS.tm_mon,sPrevTS.tm_mday] 
            a[-1]['endDate'] = [ePrevTS.tm_year,ePrevTS.tm_mon,ePrevTS.tm_mday] 
            a[-1]['startDay'] = days[sPrevTS.tm_wday] # day of activity start
            
            a[-1]['duration'] = float(a[-1]['endTime'] - a[-1]['startTime'])/60 # duration in minutes

            # add distances to travel activities (meters)
            a[-1]['distance'] = 0 
            a[-1]['lat'] = float(stops[i]['stopLat'])
            a[-1]['lon'] = float(stops[i]['stopLon'])
            a[-1]['latPrev'] = float(stops[i-1]['stopLat'])
            a[-1]['lonPrev'] = float(stops[i-1]['stopLon'])
            # use the distances in this order: 
            # (1) length of polyline (polylineDistance) (if in FMSStops)
            if 'EncodedPoints' in stops[i]:
                a[-1]['distance'] = polylineDistance(stops[i]['EncodedPoints'])
                a[-1]['polyline'] = stops[i]['EncodedPoints']
                
            # (2) network distance (if in FMSStops)
            elif 'travelDistNet' in stops[i]:
                a[-1]['distance'] = int(stops[i]['travelDistNet'])
                
            # (3) distance based on Google Directions API 
            # (will be implemented later; see travel_route_points for current implementation)
            
            # (4) straight-line distance between start and end stops
            else:
                a[-1]['distance'] = pos2dist(a[-1]['latPrev'],a[-1]['lonPrev'],a[-1]['lat'],a[-1]['lon'])
        elif stops[i]['travelMode'] != "none" and stopStart < stopEndPrevious:
            print("stopID " + str(stops[i]['stopID']) + ", " + str(stopStart) + " to " + str(stopEndPrevious) + ": stops are not chronologically ordered")
            
        a.append({})
        if stops[i]['stopType'] == 'Default':
            a[-1]['activityType'] = "gap"
            a[-1]['activity'] = "gap"
        else:
            a[-1]['activityType'] = "stop"            
            a[-1]['activity'] = stops[i]['stopType']  
            
        a[-1]['stopID'] = stops[i]['stopID']
        pcCurr = 0
        for stopPC in stopsPC:
            if stopPC['stopID'] == a[-1]['stopID']:
                pcCurr = stopPC['postcode']     
        a[-1]['postalCode'] = pcCurr
        
        a[-1]['startTime'] = stopStart
        a[-1]['endTime'] = stopEnd
        
        a[-1]['startDate'] = [sTS.tm_year,sTS.tm_mon,sTS.tm_mday]
        a[-1]['endDate'] = [eTS.tm_year,eTS.tm_mon,eTS.tm_mday]  
        a[-1]['duration'] = float(stopEnd - stopStart)/60 # duration in minutes   
        a[-1]['lat'] = float(stops[i]['stopLat'])
        a[-1]['lon'] = float(stops[i]['stopLon'])
        a[-1]['startDay'] = days[sTS.tm_wday] # day of activity start  
            
        # TO DO: fix start time problem for dataviz (below)
        # startTime = startDayOriginal + (startTime - startDay) #change to same day as first day
        # endTime = startDayOriginal + (endTime - startDay) # change to same day as first day
  
        i += 1
    
    # Add socioeconomic data by iterating through users
    for U in tl: 
        for uS in userSocio:
            if U['userID'] == uS['FMSid']:
                U['userCharacteristics'] = uS             
      
    
    return tl
