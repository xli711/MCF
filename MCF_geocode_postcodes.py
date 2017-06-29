import csv
import json 
import os.path
import urllib, time


def GoogGeoAPI(address,api,delay=3):
    base = r"https://maps.googleapis.com/maps/api/geocode/json?"
    addP = "address=" + address.replace(" ","+")
    GeoUrl = base + addP + "&key=" + api
    response = urllib.request.urlopen(GeoUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw)
    if jsonData['status'] == 'OK':
        resu = jsonData['results'][0]
        finList = [resu['geometry']['location']['lat'],resu['geometry']['location']['lng']]
    else:
        finList = [None,None,None]
    time.sleep(delay) #in seconds
    return finList


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
    
    Afile = open(dataDir + '\\' + "geocode.csv")
    A = list(csv.reader(Afile))
    #aDict = csvToDict(A)

    geoR = []
    for addr in A:
        addr = addr[0] + r", Singapore"
        print(addr)
        geoR.append([])
        geoR[-1] = GoogGeoAPI(address=addr, api="")
        print(geoR[-1])
    
    with open(dataOutDir + '\\' + 'geocode_out.csv', 'w') as outfile1:
        writer = csv.writer(outfile1)
        writer.writerows(geoR)

    # Close all files        
    dataFile.close
    Afile.close

    outfile1.close
    apifile.close
    
