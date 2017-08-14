import csv
import json
import os.path
#%%
if __name__ == '__main__':
    os.chdir("/Users/lixinhui/Dropbox (MIT)/W-FMS-BE/BE 17/git/MCF")

    with open('dataDir.json') as dataFile:
        dataDirFile = json.load(dataFile)

    dataDir = os.path.normpath(dataDirFile['dataDir'])  # data directory should be MCF Dropbox

    # set different output directory, so that temporary files do not upload to MCF Dropbox
    dataOutDir = os.path.normpath(dataDirFile['dataOutDir'])

    with open(dataDir + '/FMSStops_all_timeline.json') as tl:
        timeLines = json.load(tl)
        
#%%
    with open(dataDir + '/mode_priority_lookup.csv') as modeCsv:
        modePriority = csv.reader(mode)
        modeLookup = {row[1]: int(row[0]) for row in modePriority}
#%%
    #kIndex = beLookUp['postcode'].index('Kmeans_clust')
    #lcaIndex = beLookUp['postcode'].index('LCA_clust')

    entries = []
    tours = []
    ID = 0

    for user in timeLines:
        if 'userCharacteristics' in user: 
            usChar = user['userCharacteristics']
            activities = user['activities']
            for episode in activities:
                if episode['activityType'] == 'stop' and episode['activity'] == 'Home':
                    # Determine trip purpose
                    currentIndex = activities.index(episode)
                    
                    stops = 0
                    purposeFound = False
                    tripPurpose = ''
                    
                    homePostCode = episode['postalCode']
                    destPostCode = ''
                    
                    modeCode = 16
                    duration = 0
                    
                    tour = []
                    tour.append(episode)
    
                    downstreamEpisodes = activities[currentIndex+1:];
    
                    for downstreamEpisode in downstreamEpisodes:
                        #print(downstreamEpisode)
                        #print(downstreamEpisodes.index(downstreamEpisode))
                        if downstreamEpisode['activity'] != 'Home':
                            tour.append(downstreamEpisode)
                            if downstreamEpisode['activityType'] == 'stop' and downstreamEpisode['activity'] != 'Change Mode/Transfer' and downstreamEpisode['duration'] > duration:
                                stops += 1
                                duration = downstreamEpisode['duration']
                                tripPurpose = downstreamEpisode['activity']
                                destPostCode = downstreamEpisode['postalCode']
                                purposeFound = True
                                primaryIndex = downstreamEpisodes.index(downstreamEpisode)
                            elif downstreamEpisode['activityType'] == 'travel' and downstreamEpisode['distance'] != 0:
                                if downstreamEpisode['activity'] in list(modeLookup.keys()) and modeLookup[downstreamEpisode['activity']] < modeCode:
                                    modeCode = modeLookup[downstreamEpisode['activity']]
                        else:
                            tour.append(downstreamEpisode)
                            break
                    
                    if not purposeFound:
                        tripPurpose = 'Not Found'
                    mode = list(modeLookup.keys())[list(modeLookup.values()).index(modeCode)]
                    
                    
                    
                    tourStartTime = episode['startTime']
                    tourEndTime = tour[-1]['startTime']
                    
                    # Create entry
                    if len(tour) > 2:
                        tours.append(tour)
                        entries.append([ID, user['userID'], tripPurpose, mode, stops, homePostCode, destPostCode, tourStartTime, tourEndTime,
                                        usChar['H2_DwellingType'], usChar['H3_Ethnic'], usChar['H4_TotalPax'],
                                        usChar['H5_VehAvailable'], usChar['H8_BikeQty'], usChar['P1_Age'], usChar['P2_Gender'],
                                        usChar['P3c_NoLicense'], usChar['P5_Employ'], usChar['P6Industry'], usChar['P6_Occup'],
                                        usChar['P7_WorkHrs']])
        
                        ID += 1
#%%
    with open(dataOutDir + '/tours_data.csv', 'w', newline='') as data:
        try:
            writer = csv.writer(data)
            writer.writerow(('ID', 'userID', 'tripPurpose', 'mode', 'stops', 'homePostCode', 'destPostCode', 'tourStartTime', 'tourEndTime',
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
    modeCsv.close()
