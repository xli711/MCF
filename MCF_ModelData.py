import csv
import json
import os.path

if __name__ == '__main__':

    with open('dataDir.json') as dataFile:
        dataDirFile = json.load(dataFile)

    dataDir = os.path.normpath(dataDirFile['dataDir'])  # data directory should be MCF Dropbox

    # set different output directory, so that temporary files do not upload to MCF Dropbox
    dataOutDir = os.path.normpath(dataDirFile['dataOutDir'])

    with open(dataDir + '/FMSStops_net_mtz_timeline.json') as tl:
        timeLines = json.load(tl)

    #with open(dataDir + '/FMSStops_net_mtz_timeline_with_alternatives.json') as alt:
        #alternatives = json.load(alt)

    with open(dataDir + '/PostalCode_BE_measures_clusters.csv') as be:
        beMeasures = csv.reader(be)
        beLookUp = {row[0]: row for row in beMeasures}

    kIndex = beLookUp['postcode'].index('Kmeans_clust')
    lcaIndex = beLookUp['postcode'].index('LCA_clust')

    entries = []
    ID = 0

    for user in timeLines:
        usChar = user['userCharacteristics']
        activities = user['activities']
        for episode in activities:
            if episode['activityType'] == 'travel':
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
                                episode['startTime'], episode['endTime'], episode['postalCodePrev'],
                                usChar['H2_DwellingType'], usChar['H3_Ethnic'], usChar['H4_TotalPax'],
                                usChar['H5_VehAvailable'], usChar['H8_BikeQty'], usChar['P1_Age'], usChar['P2_Gender'],
                                usChar['P3c_NoLicense'], usChar['P5_Employ'], usChar['P6Industry'], usChar['P6_Occup'],
                                usChar['P7_WorkHrs']])

                ID += 1

    with open(dataOutDir + '/data.csv', 'w', newline='') as data:
        try:
            writer = csv.writer(data)
            writer.writerow(('ID', 'userID', 'mode', 'tripPurpose', 'startDay', 'startTime', 'endTime', 'postalCode',
                             'postalCodePrev', 'carTT', 'carCost', 'carEmission', 'mrtTT', 'mrtCost', 'mrtEmission',
                             'busTT', 'busCost', 'busEmission', 'walkTT', 'walkCost', 'walkEmission', 'oPostCode',
                             'oKCluster', 'oLCACluster', 'dPostCode', 'dKCluster', 'dLCACluster', 'dwellingType',
                             'ethnicity', 'HHSize', 'vehicles', 'bikes', 'age', 'gender', 'noLicense', 'employed',
                             'industry', 'occupation', 'workHrs'))  # Header row

            for row in entries:
                writer.writerow(row)  # Data rows

        finally:
            data.close()
    dataFile.close()
    tl.close()
    be.close()
