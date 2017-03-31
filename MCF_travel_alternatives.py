# DO NOT run this file to 'test' what happens.
# Run this file only when ready to gather final results for routes between new stops.

## This file contains a routine for identifying intermediate points in a travel route,
## based on Google Directions. The API key has a limited quota, so be careful about the number of API calls.

import simplejson, urllib
import re
import time
import operator
import os
import sys
import argparse
import math
from collections import defaultdict
from polyline.codec import PolylineCodec

REMOVE_HTML_TAGS = r'<[^>]+>'

GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
DIRECTIONS_BASE_URL = 'https://maps.googleapis.com/maps/api/directions/json'

def geocode(address, **geo_args):
    geo_args.update({
        'address': address
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    return result['results']

def reverse_geocode(lat, lng):
    geo_args = {
        'latlng': "%s,%s" % (lat, lng)
    }

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    return result['results']


def output_routes(mode, routes, stops, nS):
#    timings = defaultdict(lambda: 0)
#    distances = defaultdict(lambda: 0)
#    print 'routes: ', len(routes)
#    
#    for route in routes:
#        print 'legs: ', len(route['legs'])
#        points_dist = 0
#        pCount = 2
#        lat = stops[nS][8]
#        lon = stops[nS][9]
#        lat_prev = float(lat)
#        lon_prev = float(lon)
#
#        for leg in route['legs']:
#            print 'Distance: ', leg['distance']['text']
#            print 'Duration: ', leg['duration']['text']
#
#                
#            for step in leg['steps']:
#                travel_mode = step['travel_mode']
#                if travel_mode == 'TRANSIT':
#                    travel_mode = step['transit_details']['line']['vehicle']['type']
#                    num_stops = step['transit_details']['num_stops']
#                else:
#                    num_stops = 0
#                step_distance = step['distance']['value']
#                step_duration = step['duration']['value']/60
#                params = [stops[nS+1][0], stops[nS+1][1], stops[nS+1][2], stops[nS+1][3], stops[nS+1][4], stops[nS+1][5], travel_mode, step_distance, step_duration, num_stops ]
#                
#                with open('travel_compare.csv','a+') as outf:
#                    outf.write("%s,%s,%s,%s,%s,%s,%s,%d,%d,%d\n" % tuple(params))
#
#
#                if 'html_instructions' in step:
#                    direction_text = re.sub(REMOVE_HTML_TAGS, ' ', step['html_instructions'])
#                else:
#                    direction_text = '(no direction text)'
#
#                distance = step['distance']
#                duration = step['duration']
#                encoded_direction_text = direction_text.encode('latin1', errors='ignore')
#                print "%s (%s, %s, %s)" % (encoded_direction_text, travel_mode,
#                    duration['text'], distance['text'])
#                timings["%s-%s" % (mode, travel_mode)] += duration['value']
#                distances["%s-%s" % (mode, travel_mode)] += distance['value']
#                
#                points = PolylineCodec().decode(step['polyline']['points'])
#
#                for point in points:
#                        points_dist += pos2dist(lat_prev,lon_prev,point[0],point[1])
#                        print 'distance: ', points_dist
#                        if points_dist > dist_range:
#                            params = [stops[nS+1][0], stops[nS+1][1], pCount, stops[nS+1][2], travel_mode, point[0], point[1] ]
#                            with open('points.csv','a+') as outf:
#                                outf.write("%s,%s,%s,%s,%s,%.7f,%.7f\n" % tuple(params))
#                            pCount += 1
#                            print 'new point at: ', points_dist
#                            points_dist = 0
#                        lat_prev = point[0]
#                        lon_prev = point[1]
#    with open('points.csv','a+') as outf:
#        params = [stops[nS+1][0], stops[nS+1][1], pCount, stops[nS+1][2], travel_mode, lat_f, lon_f]
#        outf.write("%s,%s,%s,%s,%s,%s,%s\n" % tuple(params))                            
#
    return 'none', 'none'

def travelAlternatives(tl, apiKey):
    I_KNOW_WHAT_I_AM_DOING = True
    apiCount = 0
    travelModeDist = 0
    tlUAlt = []
    
    if (I_KNOW_WHAT_I_AM_DOING):
        
        modes = ['walking', 'driving', 'bus', 'subway'] # TO DO: specify 'bicycling' where available
        transitModes = ['bus', 'subway'] # TO DO: add other transit modes, if necessary
        modesMap = {'walking':'Foot', 'driving':'Car/Van', 'bus':'Bus', 'subway':'LRT/MRT'} # mapping for Singapore FMS modes
        
        for tlU in tl:
            tlUAlt.append({})
            tlUAlt[-1]['userID'] = tlU['userID']
            tlUAlt[-1]['activities'] = []
            tlAlt = tlUAlt[-1]['activities']
            
            for a in tlU['activities']:
                if a['activityType'] == "travel" and a['activity'] == "Foot" and float(a['distance']) <= 500:
                    a['travelAlt'] = 'Foot travel distance less than 500m' # do not collect alternatives for short trips
                    
                elif a['activityType'] == "travel":
                    a['travelAlt'] = []
                    tlAlt.append({})
                    tlAlt[-1]['activity'] = a['activity']
                    tlAlt[-1]['stopID'] = a['stopID']
                    tlAlt[-1]['stopIDprev'] = a['stopIDprev']
                    tlAlt[-1]['altModes'] = []
                         
                    # add ~4 years to ensure date is in future & is on same day of week as original date, for use in google directions API
                    # TO DO: change date to future time for any FMS file (4 years is for 2013 dataset) 
                    dTdiff = a['startTime'] - 1366603200 # 1366603200 is earliest timestamp in FMS_net_mtz.csv
                    dT = 1366603200 + dTdiff % (7*24*60*60) #change current timestamp to same week as earliest timestamp
                              
                    departureTime = dT + (4*52-2)*7*24*60*60 - 12*60*60
                                        
                    #print("original: " + str(a['startTime']) + " diff: " + str(dTdiff) + " new time: " + str(dT) + " future time: " + str(departureTime))
                    lat_f = a['lat'] 
                    lon_f = a['lon']
                    lat = a['latPrev']
                    lon = a['lonPrev']
                    source = '%s,%s' % (lat, lon)
                    destination = '%s,%s' % (lat_f, lon_f)
                    
                    for mode in modes:
                        # Currently only queries Google's first route option                         
                        # TO DO: get alternative routes (set alternatives to 'true')
                        # TO DO: get alternative travel times (other than best_guess)
                        params = {
                                'origin': source,
                                'destination': destination,
                                'mode': mode,
                                'region': 'sg',
                                'alternatives': 'false',
                                'departure_time': departureTime,
                                'traffic_model': 'best_guess',
                                'key': apiKey
                                }
                                
                        if mode in transitModes:
                            params['mode'] = 'transit'
                            params['transit_mode'] = mode
            
                        url = DIRECTIONS_BASE_URL + '?' + urllib.parse.urlencode(params) # use urllib.urlencode in py2.7
                        url_out = urllib.request.urlopen(url) # use urllib.urlopen in py2.7
                        data = simplejson.load(url_out)
                        apiCount += 1
                        
                        while data['status'] == 'OVER_QUERY_LIMIT':
                            print('Pausing for five minutes...')
                            time.sleep(3)
                            url_out = urllib.request.urlopen(url)
                            data = simplejson.load(url_out)
                            apiCount += 1
                        
                        a['travelAlt'].append({})
                        a['travelAlt'][-1]['googleMode'] = mode
                        a['travelAlt'][-1]['activity'] = modesMap[mode]
                        #a['travelAlt'][-1]['transferDuration'] = 0
                         
                        #print(mode + ': ' + source + ' - ' + destination)
                        tlAlt[-1]['altModes'].append({})
                        tlAlt[-1]['altModes'][-1]['mode'] = mode
                             
                        if len(data['routes']) > 0:              
                            tlAlt[-1]['altModes'][-1]['route'] = data['routes'][0]
                             
                            leg = data['routes'][0]['legs'][0]
                            travelModeDist = dict.fromkeys(['Car/Van','Taxi','Bus','Other (travel)','Motorcycle/Scooter','LRT/MRT','Bicycle','Foot'],0)
    
                            a['travelAlt'][-1]['duration'] = leg['duration']['value']/60
                             
                            if mode == 'walking':
                                travelModeDist['Foot'] = leg['distance']['value']
                                
                            elif mode == 'driving':
                                a['travelAlt'][-1]['durationInTraffic'] = leg['duration_in_traffic']['value']/60
                                travelModeDist['Car/Van'] = leg['distance']['value']
                                
                            else: 
                                a['travelAlt'][-1]['transfers'] = -1
                                 
                                if 'departure_time' in leg:
                                    a['travelAlt'][-1]['startTime'] = leg['departure_time']['value']
                                    a['travelAlt'][-1]['endTime'] = leg['arrival_time']['value']
                                else:
                                    a['travelAlt'][-1]['transfers'] = "Not found"                                
                                    #print("Departure time not found")
                                    #print(leg)

                                for step in leg['steps']:
                                    if step['travel_mode'] == "WALKING": 
                                        travelModeDist['Foot'] += step['distance']['value']
                                        
                                    elif step['travel_mode'] == "TRANSIT": 
                                        a['travelAlt'][-1]['transfers'] += 1
                                        
                                        if step['transit_details']['line']['vehicle']['type'] == "SUBWAY" or step['transit_details']['line']['vehicle']['type'] == "TRAM":
                                            travelModeDist['LRT/MRT'] += step['distance']['value']   
                                        elif step['transit_details']['line']['vehicle']['type'] == "BUS":
                                            travelModeDist['Bus'] += step['distance']['value']   
                                        else:
                                            print("Transit type not recognized: " + step['transit_details']['line']['vehicle']['type'])
                            
                            a['travelAlt'][-1]['travelModeDist'] = dict(travelModeDist)

                        else:
                            tlAlt[-1]['altModes'][-1]['route'] = "NONE"
                            print("NO ROUTE")

                        time.sleep(0.02)
                        
            print("API calls: " + str(apiCount))
        
    else:
        print("Check MCF_travel_alternatives.py before calling travelAlternatives() function.")
    
    
        
    return tl, tlUAlt