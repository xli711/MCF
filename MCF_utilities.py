from polyline.codec import PolylineCodec
import math
import time

def csvToDict(csvFile):
# Convert CSV list to dict with keys = column headers
    cD = []
    nR = len(csvFile)
    nC = len(csvFile[0])
    for i in range(0,nR-2):
        cD.append({})
        for j in range(0,nC-1):
            cD[i][csvFile[0][j]] = csvFile[i+1][j]  
    
    return cD

def dictToCSV(cD):
# TO DO: Convert dictionary structure to CSV file with column headers = keys
    
    return cD

def pos2dist(lat1,lon1,lat2,lon2):
    km_per_deg_la = 111.3237
    km_per_deg_lo = 111.1350
    km_la = km_per_deg_la * (lat1-lat2)

    if abs(lon1-lon2) > 180:
        dif_lo = abs(lon1-lon2)-180
    else:
        dif_lo = abs(lon1-lon2)

    km_lo = km_per_deg_lo * dif_lo * math.cos((lat1+lat2)*math.pi/360)
    dist = math.sqrt(math.pow(km_la,2) + math.pow(km_lo,2))
    
    return dist


def polylineDistance(pl):
    points = PolylineCodec().decode(pl)
    points_dist = 0
    pointFirst = True
    lat_prev = points[0][0]
    lon_prev = points[0][1]
    
    for point in points:
        if pointFirst:
            lat_prev = point[0]
            lon_prev = point[1]
            pointFirst = False
        else: 
            points_dist += pos2dist(lat_prev,lon_prev,point[0],point[1])       
            lat_prev = point[0]
            lon_prev = point[1]
            
    return points_dist


def strToTime(timeStr, timezone, weeks, dayStart):
    # Returns timestamp in timeStr

    timeStrSplit = [ timeStr.strip().split(' ') ]

    
    
    if '/' in timeStrSplit[0][0]:
        # older datasets contain a mix of two timestamp formats (possibly due to inconsistent post-processing)
        # The seconds info has been removed from the first timestamp:
        dt = time.strptime(timeStrSplit[0][0] + ' ' + timeStrSplit[0][1], "%m/%d/%Y %H:%M") 
    elif '-' in timeStrSplit[0][0]:
        timeStrCheck = [ timeStrSplit[0][0].strip().split('-') ]
        if int(timeStrCheck[0][0]) > 2000:
           # newer datasets use "%Y-%m-%d %H:%M:%S" and report time in UTC
            dt = time.strptime(timeStrSplit[0][0] + ' ' + timeStrSplit[0][1], "%Y-%m-%d %H:%M:%S") 
        else:
            dt = time.strptime(timeStrSplit[0][0] + ' ' + timeStrSplit[0][1], "%d-%m-%Y %H:%M:%S") 
    else:
        print("unrecognized date format: " + timeStr)
    
    # Timestamp structures do not contain time zone info, so we need to change 
    # the time to the correct time zone manually (e.g. +0800 for singapore, if timestamp is UTC)
    dtAdd =  int(time.mktime(dt)) + timezone*60*60 

    # FOR INTERVIEW DATAVIZ ONLY: advance the date to a week in the future
    # dtAdd =  dtAdd + weeks*7*24*60*60

    # if dayStart is true, return the timestamp for the start of the day
    if (dayStart):
        dtAdd = int(time.mktime(time.struct_time([dt.tm_year,dt.tm_mon,dt.tm_mday,0,0,0,0,0,0]))) + timezone*60*60 

        # FOR INTERVIEW DATAVIZ ONLY: advance the date to a week in the future
        # dtAdd = dtAdd + weeks*7*24*60*60 

    return dtAdd
