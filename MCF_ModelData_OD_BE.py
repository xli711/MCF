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
#%%
    #Step 1: origin/destination postal code to sample lookup
    shopping_df = pd.read_csv(dataOutDir + '/tours_shopping.csv')
    sample_pc_df = pd.read_csv(dataDir + '/PostalCodeLookup_150m_Sample.csv')
    sample_lookup = sample_pc_df.set_index('PC_original')['PC_sample'].to_dict()
    shopping_df['homePC_sample'] = shopping_df['HITShomePC'].map(sample_lookup) ## Two of the HITS home postal codes could not be matched to sample
    shopping_df['destPC_sample'] = shopping_df['destPostCode'].map(sample_lookup)
#%%    
    #Step 2: BE measures lookup for all unique postal codes
    pc_be_df = pd.read_csv(dataDir + '/PostalCode_BE_measures_clusters.csv')
    PCoriginal_all = sample_pc_df.PC_original.unique().tolist()
    PCoriginal_be_df = pc_be_df[pc_be_df['postcode'].isin(PCoriginal_all)]  
    PCoriginal_be_df['pc_sample'] = PCoriginal_be_df['postcode'].map(sample_lookup)
    PCsample_be_df = PCoriginal_be_df.drop_duplicates(subset=['pc_sample']) #keeps the first record for each unique sample postcode
    #PCsample_all = PCsample_be_df.pc_sample.unique().tolist()
#%%
    #Step3: alternative destinations match
    shopping_alt_condition = (PCsample_be_df['retail'] > 0) | (PCsample_be_df['smallretai'] > 0)
    shopping_alt_be_df = PCsample_be_df[shopping_alt_condition]
    shopping_alt_be_df.to_csv(dataOutDir + '/shopping_alt_dest.csv')
#%% 
    #Step4: availability, travel time, and cost lookup for each destination alternative in each mode
    #map postal code to mtz
    pc_mtz = pd.read_csv(dataDir + '/sample_pc_mtz.csv', encoding = 'ISO-8859-1')
    mtz_lookup =  pc_mtz.set_index('postcode')['MTZ_1169'].to_dict()
    
    #map postal code to sample postal code first
    shopping_alt_be_df['PC_s'] = shopping_alt_be_df['postcode'].map(sample_lookup)
    #then map sample postal code to mtz
    shopping_df['homeMTZ'] = shopping_df ['homePC_sample'].map(mtz_lookup)
    shopping_df['destMTZ'] = shopping_df ['destPC_sample'].map(mtz_lookup)
    shopping_alt_be_df ['MTZ'] = shopping_alt_be_df['PC_s'].map(mtz_lookup)
    all_pc = pc_mtz.postcode.unique().tolist()
#%%    
    #read in the MTZ OD cost matrix and define functions to look up travel time/cost
    costs = pd.read_csv(dataDir + '/OPcosts.314', sep='\s+')
    costs_origins = costs.origin.unique().tolist()
    costs['ptTT'] = costs['OPivt'] + costs['OPaux'] + costs['OPwtt']
    
    def carTT_lookup(originMtz, destMtz):
        return costs.loc[(originMtz == costs.origin) & (destMtz == costs.dest), 'OPTim']
    
    def carCost_lookup(originMtz, destMtz):
        return costs.loc[(originMtz == costs.origin) & (destMtz == costs.dest), 'OPERP']
    
    def ptTT_lookup(originMtz, destMtz):
        return costs.loc[(originMtz == costs.origin) & (destMtz == costs.dest), 'ptTT']
    
    def ptCost_lookup(originMtz, destMtz):
        return costs.loc[(originMtz == costs.origin) & (destMtz == costs.dest), 'OPcos']
#%%
    #create a dataframe for model data, set up lookup variables
    shopping_data_df = shopping_df.copy()
    pc_builta_lookup = PCsample_be_df.set_index('pc_sample')['sum_builta'].to_dict()
    pc_lumix_lookup = PCsample_be_df.set_index('pc_sample')['Use_mix'].to_dict()
    pc_junct_lookup = PCsample_be_df.set_index('pc_sample')['countjunct'].to_dict()
    
    shopping_data_df['oBuiltA'] = shopping_data_df['homePC_s'].map(pc_builta_lookup)
    shopping_data_df['oLumix'] = shopping_data_df['homePC_s'].map(pc_lumix_lookup)
    shopping_data_df['oJunct'] = shopping_data_df['homePC_s'].map(pc_junct_lookup)   
    
    shopping_data_df['dBuiltA'] = shopping_data_df['destPC_s'].map(pc_builta_lookup)
    shopping_data_df['dLumix'] = shopping_data_df['destPC_s'].map(pc_lumix_lookup)
    shopping_data_df['dJunct'] = shopping_data_df['destPC_s'].map(pc_junct_lookup)   
#%%
    #add columns of travel cost/time + BE measures for each destination alternative
    counter = 0
    shopping_data_df['dest_idx'] = 0
    for idx, row in shopping_alt_be_df.iterrows():
        counter += 1
        destMTZ = int(row['MTZ'])
        shopping_data_df['carTT'+str(counter)] = 0
        
        ### the following loop took too long to run, needs improvement
        for idx, row in shopping_data_df.iterrows():
            originMTZ = int(row['homeMTZ'])
            shopping_data_df.set_value(idx, 'carTT'+str(counter), carTT_lookup(originMTZ, destMTZ))
#           shopping_data_df.set_value(idx, 'carCost'+str(counter), carCost_lookup(originMTZ, destMTZ))
#           shopping_data_df.set_value(idx, 'ptTT'+str(counter), ptTT_lookup(originMTZ, destMTZ))
#           shopping_data_df.set_value(idx, 'ptCost'+str(counter), ptCost_lookup(originMTZ, destMTZ))
            if row['destMTZ'] == destMTZ:
                shopping_data_df.set_value(idx, 'dest_idx', counter)

        #add BE measures for each destination alternative
        shopping_data_df['builtA' + str(counter)] = shopping_data_df['homePC_s'].map(pc_builta_lookup)
        shopping_data_df['lumix' + str(counter)] = shopping_data_df['homePC_s'].map(pc_lumix_lookup)
        shopping_data_df['junct' + str(counter)] = shopping_data_df['homePC_s'].map(pc_junct_lookup)
#        print(row['PC_s'])
#%%
    shopping_data_df.to_csv(dataOutDir + '/shopping_data.csv')
    shopping_alt_be_df.to_csv(dataOutDir + '/shopping_alt_be.csv')
    
    dataFile.close()
        
        