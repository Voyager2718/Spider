import urllib.request, urllib.parse, json
from urllib.error import HTTPError
from math import radians, cos, sin, asin, sqrt, pi
import time
import os

API_ID = 'YOUR_GOOGLE_API_ID'

banks = ['平安银行','宁波银行','浦发银行','华夏银行','民生银行','招商银行','南京银行','兴业银行','北京银行','农业银行','交通银行','工商银行','光大银行','建设银行','中国银行','中信银行']

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

def getAddressesAndCoordinates(coord, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, pagetoken = None):
    keyword = urllib.parse.quote(keyword) 
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=bank&location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)
    if pagetoken:
        url += '&pagetoken=' + pagetoken
    catchLoop = True
    while catchLoop:
        catchLoop = False
        try:
            jsonValue = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            if jsonValue['status'] != 'OK' and jsonValue['status'] != 'ZERO_RESULTS':
                if 'error_message' in jsonValue:
                    print('Error:', jsonValue['error_message'])
                else:
                    print(str(jsonValue['status']))
                return [{'status': str(jsonValue['status']), 'url': url}]
            return extractAddressAndCoordinate(jsonValue)
        except HTTPError:
            print('Got a HTTP error. Retrying...')
            catchLoop = True

def runThrough(cities, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, file = 'test.json'):
    num = 0
    allAddr = []
    results = []
    for c in cities:
        addr = getAddresses((c[3],c[4]), keyword, api_id=api_id, lang=lang, radius=radius)
        addr2 = []
        for a in addr:
            if a not in allAddr:
                allAddr += [a]
                addr2 += [a]
        results += [[c[0],c[1],c[2],addr2]]
        num += 1
        print('Running...' + str(num))
    return results

def runThroughWithCoordinates(cities, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, file = 'test.json'):
    num = 0
    allAddr = []
    results = []
    for c in cities:
        addr = getAddressesAndCoordinates((c[3],c[4]), keyword, api_id=api_id, lang=lang, radius=radius)
        addr2 = []
        for a in addr:
            if a not in allAddr:
                allAddr += [a]
                addr2 += [a]
        results += [[c[0],c[1],c[2],addr2]]
        num += 1
        print('Running...' + str(num))
    return results

def re_read(data, api_id = API_ID, lang = 'zh-CN'):
    num = 0
    while True:
        for d in data:
            for i in range(len(d[3])):
                if type(d[3][i]) == dict:
                    num += 1
                    print('Re-reading item...' + str(num))
                    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=bank&language=' + str(lang) + '&pagetoken=' + str(d[3][i]['token']) + '&key=' + str(api_id)
                    jsonValue = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
                    if jsonValue['status'] == 'INVALID_REQUEST':
                        continue
                    del d[3][i]
                    d[3] += extractAddress(jsonValue)
        for dd in data:
            for i in range(len(d[3])):
                if type(d[3][i]) == dict:
                    continue
        break
    return data

def writeRawResults(results, file):
    fp = open(file,'w+')
    for item in results:
        for i in range(len(item[3])):
                fp.write(str(item[0])+'\\')
                fp.write(str(item[1])+'\\')
                fp.write(str(item[2])+'\\')
                fp.write(str(item[3][i].replace('\u200e',''))+'\n')
    fp.close()

def writeRawResultsWithCoords(results, file):
    fp = open(file,'w+')
    for item in results:
        for i in range(len(item[3])):
                fp.write(str(item[0])+'\\')
                fp.write(str(item[1])+'\\')
                fp.write(str(item[2])+'\\')
                fp.write(str(item[3][i][0].replace('\u200e',''))+'\\')
                fp.write(str(item[3][i][1])+'\\')
                fp.write(str(item[3][i][2])+'\n')
    fp.close()

def run(bank, api_id = API_ID, file='cities.csv', radius=5000, lang = 'zh-CN', threads=1, ):
    cities = getCities(file)
    d = runThrough(cities, bank, api_id=api_id, radius=radius, lang = lang)
    addresses = re_read(d, api_id=api_id)
    return addresses

def autoRunThrough(api_id = API_ID, file = 'cities.csv', radius = 5000, lang = 'zh-CN'):
    results = {}
    cities = getCities(file)
    for b in banks:
        results[b] = runThrough(cities, b, api_id, radius = radius, lang = lang)
    return results  

def writeQuantity(data, file):
    fp = open(file, 'w+')
    for item in data:
        fp.write(str(item[0])+'\\')
        fp.write(str(item[1])+'\\')
        fp.write(str(item[2])+'\\')
        fp.write(str(len(item[3]))+'\n')
    fp.close()

def extractCoordinates(data):
    coords = []
    for d in data:
        for item in d[3]:
            coords += [(item[1],item[2])]
    return coords

def getCoordinates(data, api_id = API_ID):
    coord = []
    num = 0
    for item in data:
        for i in item[3]:
            num += 1
            url = 'https://maps.googleapis.com/maps/api/geocode/json?type=bank&language=zh-CN&address=' + str(urllib.parse.quote(item[2]) + urllib.parse.quote(i)) + '&key=' + str(api_id)
            jsonValue = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            if jsonValue['status'] == 'OK':
                coord += [(float(jsonValue['results'][0]['geometry']['location']['lat']), float(jsonValue['results'][0]['geometry']['location']['lng']))]
                print('Got..' + str(num))
                continue
            print('No result..' + jsonValue['status'] + '\n\t' + str(url))
    return coord

def writeCoords(coords, file):
    fp = open(file, 'w+')
    for item in coords:
        fp.write(str(item[0]) + ',' + str(item[1]) + '\n')
    fp.close()

def averageDistance(hearQuarter, l):
    dist = []
    for item in l:
        if type(item[0]) == float and type(item[1]) == float:
            dist += [distance(item,hearQuarter)]
    return sum(dist)/len(l)

def writeJson(j, file):
    fp = open(file,'w+')
    fp.write(str(j))
    fp.close()