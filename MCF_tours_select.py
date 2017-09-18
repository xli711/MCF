import csv
import json
import pandas as pd
import os.path
#%%
if __name__ == '__main__':
    os.chdir("/Users/lixinhui/Dropbox (MIT)/W-FMS-BE/BE 17/git/MCF")

    with open('dataDir.json') as dataFile:
        dataDirFile = json.load(dataFile)

    dataDir = os.path.normpath(dataDirFile['dataDir'])  # data directory should be MCF Dropbox

    # set different output directory, so that temporary files do not upload to MCF Dropbox
    dataOutDir = os.path.normpath(dataDirFile['dataOutDir'])

    tours_df = pd.read_csv(dataOutDir + '/tours_data.csv')
    #print(tours_df)
#%%
    unique_purpose = tours_df.tripPurpose.unique().tolist()
    
    #extract shopping tours
    sp_condition = (tours_df['tripPurpose'] == 'Shopping')
    shopping_df = tours_df[sp_condition]
    
    #extract personal tours
    ps_condition = (tours_df['tripPurpose'] == 'Personal Errand/Task') | \
                    (tours_df['tripPurpose'] == 'Medical/Dental (Self)') | \
                    (tours_df['tripPurpose'] == 'Social')
    personal_df = tours_df[ps_condition]
    
    #extract recreation tours
    rc_condition = (tours_df['tripPurpose'] == 'Sports/Exercise') | \
                    (tours_df['tripPurpose'] == 'Recreation') | \
                    (tours_df['tripPurpose'] == 'Entertainment')
    recreation_df = tours_df[rc_condition]
    
    #extract escort tours
    es_condition = (tours_df['tripPurpose'] == 'To Accompany Someone') | \
                    (tours_df['tripPurpose'] == 'Pick Up/Drop Off')
    escort_df = tours_df[es_condition]
    
#%%
    shopping_df.to_csv(dataOutDir + '/tours_shopping.csv')
    personal_df.to_csv(dataOutDir + '/tours_personal.csv')
    recreation_df.to_csv(dataOutDir + '/tours_recreation.csv')
    escort_df.to_csv(dataOutDir + '/tours_escort.csv')
    
    
#%%
    dataFile.close()