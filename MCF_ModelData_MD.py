import csv
import json
import os.path
import pandas as pd
import numpy as np
#%%
if __name__ == '__main__':

    with open('dataDir.json') as dataFile:
        dataDirFile = json.load(dataFile)

    dataDir = os.path.normpath(dataDirFile['dataDir'])  # data directory should be MCF Dropbox

    # set different output directory, so that temporary files do not upload to MCF Dropbox
    dataOutDir = os.path.normpath(dataDirFile['dataOutDir'])

#    with open(dataDir + '/FMSStops_all_timeline.json') as tl:
#        timeLines = json.load(tl)
#
#    #with open(dataDir + '/FMSStops_net_mtz_timeline_with_alternatives.json') as alt:
#        #alternatives = json.load(alt)
#
#    with open(dataDir + '/PostalCode_BE_measures_clusters.csv') as be:
#        beMeasures = csv.reader(be)
#        beLookUp = {row[0]: row for row in beMeasures}
#
#    farIndex = beLookUp['postcode'].index('FAR')
#    heightIndex = beLookUp['postcode'].index('avgbuildhe')
#    builtDensIndex = beLookUp['postcode'].index('built_dens')
#    luMixIndex = beLookUp['postcode'].index('Use_mix')
#    busIndex = beLookUp['postcode'].index('busstops')
#    mrtIndex = beLookUp['postcode'].index('mrt')
#    intersectIndex = beLookUp['postcode'].index('countjunct')
#    fourwayDensIndex = beLookUp['postcode'].index('perc_fourw')
#    pathLengIndex = beLookUp['postcode'].index('lenfootpat')
#    porousIndex = beLookUp['postcode'].index('porousarea')
    
    costs = pd.read_csv(dataDir + '/OPcosts.314', sep='\s+')
    trips = pd.read_csv(dataDir + '/FMSStops_all_BE.csv')
#%%
    trips_w = trips.loc[trips['tripPurpose'] == 'Work']
    uniqDest = trips_w['dPostCode'].unique()

#%%
    #kIndex = beLookUp['postcode'].index('Kmeans_clust')
    #lcaIndex = beLookUp['postcode'].index('LCA_clust')

    entries = []
    ID = 0

    for user in timeLines:
        if 'userCharacteristics' in user: 
            usChar = user['userCharacteristics']
            activities = user['activities']
            for episode in activities:
                if episode['activityType'] == 'travel' and episode['distance'] != 0 and episode['postalCode'] != 0 and episode['postalCodePrev'] != 0:
                    # Determine trip purpose
                    currentIndex = activities.index(episode)
                    purposeFound = False
                    tripPurpose = ''
    
                    downstreamEpisodes = activities[currentIndex+1:];
    
                    for downstreamEpisode in downstreamEpisodes:
                        #print(downstreamEpisode)
                        #print(downstreamEpisodes.index(downstreamEpisode))
                        if downstreamEpisode['activityType'] == 'stop' and downstreamEpisode['activity'] != 'Change Mode/Transfer':
                            tripPurpose = downstreamEpisode['activity']
                            purposeFound = True
                            break
    
                    if not purposeFound:
                        tripPurpose = 'Not Found'
    
                    # Create entry
    
                    entries.append([ID, user['userID'], episode['activity'], tripPurpose, episode['startDay'],
                                    episode['startTime'], episode['endTime'], 
                                    episode['postalCodePrev'],
                                    beLookUp[episode['postalCodePrev']][farIndex],
                                    beLookUp[episode['postalCodePrev']][heightIndex], 
                                    beLookUp[episode['postalCodePrev']][builtDensIndex],
                                    beLookUp[episode['postalCodePrev']][luMixIndex],
                                    beLookUp[episode['postalCodePrev']][busIndex],
                                    beLookUp[episode['postalCodePrev']][mrtIndex],
                                    beLookUp[episode['postalCodePrev']][intersectIndex],
                                    beLookUp[episode['postalCodePrev']][fourwayDensIndex],
                                    beLookUp[episode['postalCodePrev']][pathLengIndex],
                                    beLookUp[episode['postalCodePrev']][porousIndex],
                                    episode['postalCode'],
                                    beLookUp[episode['postalCode']][farIndex], 
                                    beLookUp[episode['postalCode']][heightIndex],
                                    beLookUp[episode['postalCode']][builtDensIndex],
                                    beLookUp[episode['postalCode']][luMixIndex],
                                    beLookUp[episode['postalCode']][busIndex],
                                    beLookUp[episode['postalCode']][mrtIndex],
                                    beLookUp[episode['postalCode']][intersectIndex],
                                    beLookUp[episode['postalCode']][fourwayDensIndex],
                                    beLookUp[episode['postalCode']][pathLengIndex],
                                    beLookUp[episode['postalCode']][porousIndex],
                                    usChar['H2_DwellingType'], usChar['H3_Ethnic'], usChar['H4_TotalPax'],
                                    usChar['H5_VehAvailable'], usChar['H8_BikeQty'], usChar['P1_Age'], usChar['P2_Gender'],
                                    usChar['P3c_NoLicense'], usChar['P5_Employ'], usChar['P6Industry'], usChar['P6_Occup'],
                                    usChar['P7_WorkHrs']])
    
                    ID += 1
#%%
    with open(dataOutDir + '/data.csv', 'w', newline='') as data:
        try:
            writer = csv.writer(data)
            writer.writerow(('ID', 'userID', 'mode', 'tripPurpose', 'startDay', 'startTime', 'endTime', 
                             'oPostCode', 'oFAR', 'oAvgBldgHeight', 'oBuiltDens', 'oLuMix', 'oBus', 'oMRT', 'oIntersect', 'oFourWayDens', 'oFootpathLeng', 'oPorousArea', 
                             'dPostCode', 'dFAR', 'dAvgBldgHeight', 'dBuiltDens', 'dLuMix', 'dBus', 'dMRT', 'dIntersect', 'dFourWayDens', 'dFootpathLeng', 'dPorousArea', 
                             'dwellingType','ethnicity', 'HHSize', 'vehicles', 'bikes', 'age', 'gender', 'noLicense', 'employed',
                             'industry', 'occupation', 'workHrs'))  # Header row
            # Variables that should have been included:
            #'carTT', 'carCost', 'carEmission', 'mrtTT', 'mrtCost', 'mrtEmission',
            #'busTT', 'busCost', 'busEmission', 'walkTT', 'walkCost', 'walkEmission',
            for row in entries:
                writer.writerow(row)  # Data rows

        finally:
            data.close()
    dataFile.close()
    tl.close()
    be.close()
