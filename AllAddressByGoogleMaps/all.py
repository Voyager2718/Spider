import urllib.request, json
from math import radians, cos, sin, asin, sqrt, pi
import time

API_ID = 'YOUR_GOOGLE_API_ID'

def readLine(file, passHead = 0):
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

def writeReversely(array,file):
    """
    Reverse latitude and longitude.
    """
    fp = open(file,'w+')
    for item in array:
            fp.write(item[0] + ',')
            fp.write(item[1] + ',')
            fp.write(item[2] + ',')
            fp.write(item[4] + ',')
            fp.write(item[3] + '\n')
    fp.close()

def offset(coord, offsetting):
    """
    Swifting to another coordinate.
    """
    R=6378137
    dn, de = offsetting[0], offsetting[1]
    lon, lat = coord[0], coord[1]
    dLon = dn/(R*cos(pi*lat/180))
    dLat = de/R
    lon0 = lon + dLon * 180/pi
    lat0 = lat + dLat * 180/pi
    return (lon0, lat0)

def distance(coord0, coord1):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lon1,lat1 = coord0[0],coord0[1]
    lon2,lat2 = coord1[0],coord1[1]
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def extractAddress(JSON):
    results = JSON['results']
    res = []
    for item in results:
        res += [item['vicinity']]
    return res

#Google pagination API may not response for a while, so just push to the list to get the result in the future.
delayedRequest = []

def getAddresses(coord, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, pagetoken = None):
    if pagetoken:
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=' + pagetoken + '&language=' + str(lang) + '&key=' + str(api_id)
    else:
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)
    print(url) 
    value = urllib.request.urlopen(url).read().decode('utf-8')
    jsonValue = json.loads(value)
    if jsonValue['status'] != 'OK' and jsonValue['status'] != 'ZERO_RESULTS':
        if 'error_message' in jsonValue:
            print('Error:', jsonValue['error_message'])
        else:
            print(str(jsonValue['status']))
        return [{'json': jsonValue, 'url': url}]
    if 'next_page_token' in jsonValue:
        return extractAddress(jsonValue) + getAddresses(coord, keyword, api_id, lang, radius, jsonValue['next_page_token'])
    return extractAddress(jsonValue)

def writeRawResults(results, file):
    fp = open(file, 'w+')
    fp.write(json.dumps(results, ensure_ascii=False))
    fp.close()

def runThrough(cities, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, file = 'test.csv'):
    results = []
    for c in cities:
        results += [(c[0],c[1],c[2],getAddresses((c[3],c[4]), keyword, api_id=api_id, lang=lang, radius=radius))]
    writeRawResults(results, file)    
    return results

def getAddressesLength(array):
    l = []
    for i in array:
        l += [len(i[3])]
    return l