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
from MCF_timelineRead_FMSStops_Old import *

if __name__ == '__main__':
   
    # Activity code lookup file
    # contains only AVERAGE CO2 per minute or km. 
    # Future estimations (e.g. with emissions ranges) will require a new file format.
    Afile = open('activityLookupSingapore.csv')
    Areader = csv.reader(Afile)
    A = list(Areader)
    aDict = csvToDict(A)
    
    # FMS stops file input
    stopFile = open('FMSStops_net_mtz.csv') # golden dataset (weekdays only)
    stopsT = list(csv.reader(stopFile))
    
    stopsDict = csvToDict(stopsT) # change CSV file (with headers in first row) to python Dictionary

    timezone = 8 # Singapore timezone - use for NEWER DATA FILES ONLY, which are in UTC
    timezone = 0 # Use 0 for FMSStops_net_mtz.csv
    dayBreakHour = -1 # set to: do not break up activities across days
    timeline1 = timelineRead(stopsDict, dayBreakHour, timezone) # Construct timelines with ORIGINAL stops
    
    # combine stops of particular types (e.g. work) when close together (e.g. within 350m)
    # NOTE: Run this routine on the timeline BEFORE calculating emissions
    distanceTolerance = 350
    # TO DO: add the combine option/switch to the activityLookup file
    activitiesToCombine = ['Home','Work','Work-Related Business','Education','Pick Up/Drop Off','Other Home','Other (stop)']
    timeline1 = stopsRevise(timeline1, distanceTolerance, activitiesToCombine) 
    
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
    
    with open('timeline.json', 'w') as outfile:
         json.dump(timeline1, outfile, indent=4, encoding="utf-8", sort_keys=True) # Change to indent=None to make minimized JSON file
    
    # TO DO: convert JSON/data dictionary to CSV field format    
    
    # Close all files        
    Afile.close()
    stopFile.close()

