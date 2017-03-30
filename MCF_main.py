# Imports the OLD type of FMS data file (FMSStops.csv or stops_summary_xxxxxx.csv)
# For the new type of FMS data file (interval type), we will need to implement a new data import routine

import csv
import json 
import os.path
import sys
from numbers import Number

# import other MCF functions:
from MCF_emissionsCalc import *
from MCF_utilities import *
from MCF_timelineRevise import *
from MCF_timelineRead_FMSStops_Old import * # change this file import, in order to use different timelineRead function
from MCF_travel_alternatives import *

if __name__ == '__main__':
   
    # Change the data directories in dataDir.json to your local directory. 
    # Then, do not re-commit dataDir.json. Do not add data files to the GIT repository.
    with open('dataDir.json') as dataFile:    
        dataDirFile = json.load(dataFile)
        
    dataDir = os.path.normpath(dataDirFile['dataDir']) # data directory should be MCF Dropbox
    
    # set different output directory, so that temporary files do not upload to MCF Dropbox
    dataOutDir = os.path.normpath(dataDirFile['dataOutDir'])  
    
    apifile = open(dataDir + '\\' + 'apiKey.txt', 'r')    
    googleApiKey = apifile.readline()
    
    # Activity code lookup file
    # contains only AVERAGE CO2 per minute or km. 
    # Future estimations (e.g. with emissions ranges) will require a new file format.
    Afile = open(dataDir + '\\' + dataDirFile['activityLookup'])
    A = list(csv.reader(Afile))
    aDict = csvToDict(A)
    
	# Stop ID to Postal Code mapping file
    stopPCfile = open(dataDir + '\\' + dataDirFile['FMSDataPostalCode'])
    stopPC = list(csv.reader(stopPCfile))
    stopPCDict = csvToDict(stopPC)

    # FMS User ID to HITS socioeconomic data file
    # TODO: extend to other user datafiles, including FMS presurvey
    usFile = open(dataDir + '\\' + dataDirFile['FMSUserSocio'])
    us = list(csv.reader(usFile))
    usDict = csvToDict(us)


    # FMS data file input
    # IMPORTANT: make sure there are TWO returns after the last data line, so that the CSV reader will read in the last data line 
    stopFile = open(dataDir + '\\' + dataDirFile['FMSData']) # in dataDir.json, set the data filename
    stopsT = list(csv.reader(stopFile))
    
    stopsDict = csvToDict(stopsT) # change CSV file (with headers in first row) to python Dictionary

    timezone = 8 # Singapore timezone - use for NEWER DATA FILES ONLY, which are in UTC
    timezone = 0 # Use 0 for FMSStops_net_mtz.csv
    dayBreakHour = -1 # set to: do not break up activities across days
    timeline1 = timelineRead(stopsDict, stopPCDict, usDict, dayBreakHour, timezone) # Construct timelines with ORIGINAL stops
    
    # REVISE THE ACTIVITY TIMELINE
    # combine stops of particular types (e.g. work) when close together (e.g. within 350m)
    # NOTE: Run this routine on the timeline BEFORE calculating emissions
    distanceTolerance = 250
    # TO DO: add the combine option/switch to the activityLookup file
    activitiesToCombine = ['Home','Work','Work-Related Business','Education','Pick Up/Drop Off','Other Home','Other (stop)']
    timeline1 = stopsRevise(timeline1, distanceTolerance, activitiesToCombine) 
    timeline1 = travelRevise(timeline1)
    
    timeline1 = timelineEmissionsCalc(timeline1, aDict) # add emissions info to timeline1

    #============================
    # TO DO: revise TRAVEL activities in order to reduce travel sequence types (e.g. walk-mrt-walk)
    # timeline1 = stopsRevise(timeline1) 
    
    # TO DO: include user characteristics from HITS 2012 data (works with golden dataset only)
    # timeline1 = addHITS(timeline1) 
    
    # TO DO: include postcode-level residential energy use from EMA data 
    # timeline1 = addEMA(timeline1) 
    
    
    #==============================================================================
    #### The following code is for the manually revised Timeline function. Do not remove. ###
    #timeline2 = timelineReadRevised(stopsT) # Construct timelines with REVISED stops
    
    # Find differences between ORIGINAL and REVISED timelines, and view original/diff/revised timelines for comparative analysis
    # tDiff, gisCSVo, gisCSV = timelineDiff(timeline1, timeline2) 
    # timelineAll = timelineCombine(timeline1,tDiff,timeline2)
    # with open('data.json', 'w') as outfile:
    #     json.dump(timelineAll, outfile)
    
    # with open('gis_orig_gl.csv', 'wb') as csvfile:
    #     cw = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     for row in gisCSV:
    #         cw.writerow(row)
    # 
    # with open('gis_rev_gl.csv', 'wb') as csvfile:
    #     cw = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     for row in gisCSV:
    #         cw.writerow(row)
    # End REVISION Function code
    #==============================================================================
    
    with open(dataOutDir + '\\' + dataDirFile['FMSData'][0:-4] + '_timeline.json', 'w') as outfile1:
         json.dump(timeline1, outfile1, indent=4, sort_keys=True) # Change to indent=None to make minimized JSON file
    
    tlTravelAltFile = dataOutDir + '\\' + dataDirFile['FMSData'][0:-4] + '_alternatives.json'
    if os.path.exists(tlTravelAltFile):
        print("alternative travel data file already exists")
        #stops = [ row.strip().split(',') for row in file('FMSStops.csv') ]
    else:
        # Run this routine only if you need the travel alternatives for the current timeline.
        # This routine uses up the Google Directions API Key allowance.
        print(googleApiKey)
        tlAlt = travelAlternatives(timeline1, googleApiKey)
        with open(tlTravelAltFile, 'w') as outfile2:
            json.dump(tlAlt, outfile2, indent=4, encoding="utf-8", sort_keys=True) # Change to indent=None to make minimized JSON file
            outfile2.close
    # TO DO: convert JSON/data dictionary to CSV field format    
    
    # Close all files        
    dataFile.close
    Afile.close
    stopPCfile.close
    usFile.close
    stopFile.close
    outfile1.close
    
