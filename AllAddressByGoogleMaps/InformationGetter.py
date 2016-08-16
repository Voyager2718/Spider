import urllib.request, urllib.parse, json
from urllib.error import HTTPError
from math import radians, cos, sin, asin, sqrt, pi
import time
import os

API_ID = 'YOUR_GOOGLE_API_ID'

banks = ['平安银行','宁波银行','浦发银行','华夏银行','民生银行','招商银行','南京银行','兴业银行','北京银行','农业银行','交通银行','工商银行','光大银行','建设银行','中国银行','中信银行']

banks_hq = {
    '平安银行' : (22.5407058,114.1075029),
    '宁波银行' : (29.8097237,121.5420964),
    '浦发银行' : (31.2378726,121.4899615),
    '华夏银行' : (39.9076986,116.4202794),
    '民生银行' : (39.9060149,116.3715725),
    '招商银行' : (22.5368386,114.0225838),
    '南京银行' : (32.0544521,118.7841394),
    '兴业银行' : (26.0928929,119.3020881),
    '北京银行' : (39.9172526,116.3578085),
    '农业银行' : (39.9085414,116.4227061),
    '交通银行' : (31.2395722,121.5040103),
    '工商银行' : (39.9087474,116.3656513),
    '光大银行' : (39.9182534,116.3635837),
    '建设银行' : (39.9129233,116.3581889),
    '中国银行' : (39.9076719,116.3734256),
    '中信银行' : (39.9308017,116.4350518)
}

def getCities(file, passHead = 1):
    """
    Get all cities and its' coordinate.
    """
    fp = open(file,'r+')
    line = fp.readline()
    array = []
    while(line != ''):
        if passHead > 0:
            passHead -= 1
            line = fp.readline()
            continue
        array += [line.replace('\n','').split(',')]
        line = fp.readline()
    fp.close()
    return array

def distance(coord0, coord1):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    r = 6371e3
    lat1,lon1 = coord0[0],coord0[1]
    lat2,lon2 = coord1[0],coord1[1]
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def getOtherPages(token, api_id = API_ID, lang = 'zh-CN'):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=' + str(lang) + '&pagetoken=' + str(token) + '&key=' + str(api_id)
    return query(url)

def getResults(coord, keyword, api_id = API_ID, type = 'bank', lang = 'zh-CN', radius = 10000):
    keyword = urllib.parse.quote(keyword) 
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=' + str(type) +'&location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)
    return query(url)

def query(url):
    while True:
        try:
            results = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            if results['status'] == 'OK' or results['status'] == 'ZERO_RESULTS':
                if 'next_page_token' in results:
                    return {'token' : results['next_page_token'], 'results' : results['results']}
                return {'results' : results['results']}
            print('-' * 50)
            if 'error_message' in results:
                print('Status: ' + str(results['status']) + ' Error:', results['error_message'])
            else:
                print('Status: ' + str(results['status']))
            print('-' * 50)
            if results['status'] == 'OVER_QUERY_LIMIT':
                raise Exception('Over limit.')
            if results['status'] == 'REQUEST_DENIED':
                raise Exception('Request denied.')
            print('Got a "INVALID_REQUEST" error. Retry later...')
            print('URL:\n\t' + url)
            return {'url' : url}
        except HTTPError:
            print('Got a HTTP error. Retrying...')

def getResultsInCitiesDelayed(cities, keyword, api_id = API_ID, type = 'bank', lang = 'zh-CN', radius = 10000):
    num = 0
    results = []
    ids = []
    for city in cities:
        num += 1
        print('Running in method delay...' + keyword + ' ' + str(num) + '/' + str(len(cities)))
        result = getResults((city[3],city[4]), keyword, api_id, type, lang, radius)
        for res in result['results']:
            if res['id'] not in ids:
                results += [(city[0], city[1], city[2], res)]
                ids += [res['id']]
    rnum = 0    
    while True:
        haveUnread = False
        for result in results:
            if 'token' in result[3]:
                print('Re-reading...' + str(rnum))
                re_read = getOtherPages(result[3]['token'], api_id, lang)
                if 'url' not in re_read:
                    del result[3]['token']
                    result[3]['result'] += re_read['result']
                    if 'token' in re_read:
                        result[3]['token'] = re_read['token']
        haveUnread = False
        for result in results:
            if 'token' in result[3]:
                haveUnread = True
        if not haveUnread:
            break
    return results

def extractCoords(data):
    coords = []
    for item in data:
        coords += [(item[3]['geometry']['location']['lat'],item[3]['geometry']['location']['lng'])]
    return coords

def extractAddresses(data):
    coords = []
    for item in data:
        coords += [item[3]['vicinity']]
    return coords

def runAll(cities, extractFunction, source = banks, api_id = API_ID, type = 'bank', lang = 'zh-CN', radius = 10000):
    results = {}
    for s in source:
        results[s] = extractFunction(getResultsInCitiesDelayed(cities, s, 'AIzaSyCcJUqHWucOoG9r1nscshfBRQE6oycDY04', type, lang, radius))
    return results

def averageDistance(headQuarter, locations):
    dist = []
    for item in locations:
        if type(item[0]) == float and type(item[1]) == float:
            dist += [distance(item,headQuarter)]
    return sum(dist)/len(locations)

def getAllAverageDistance(headQuarters, banksLocations):
    dict = {}
    for loc in banksLocations:
        dict[loc] = averageDistance(headQuarters[loc], banksLocations[loc])
    return dict

def writeCoords(coords, file):
    fp = open(file, 'w+')
    for i in range(len(coords) - 1):
        fp.write(str(coords[i][0]) + ',' + str(coords[i][1]) + '\n')
    fp.write(str(coords[i][0]) + ',' + str(coords[i][1]))
    fp.close()

def writeAllCoords(banks_coords):
    for item in banks_coords:
        writeCoords(banks_coords[item], item + '.csv')