import urllib.request, urllib.parse, json
from math import radians, cos, sin, asin, sqrt, pi
import time

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
    """
    Extract address from JSON.
    """
    results = JSON['results']
    res = []
    for item in results:
        res += [item['vicinity']]
    if 'next_page_token' in JSON:
        print('Extended page detected.')
        res += [{'token': JSON['next_page_token']}]
    return res

def getAddressesLength(array):
    l = []
    for i in array:
         l += [len(i[3])]
    return l

#Google pagination API may not response for a while, so just push to the list to get the result in the future.
#def __init__(self):
#   self.__delayedRequests = []

def getAddresses(coord, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000, pagetoken = None):
    keyword = urllib.parse.quote(keyword) 
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)
    if pagetoken:
        url += '&pagetoken=' + pagetoken
    jsonValue = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    if jsonValue['status'] != 'OK' and jsonValue['status'] != 'ZERO_RESULTS':
        if 'error_message' in jsonValue:
            print('Error:', jsonValue['error_message'])
        else:
            print(str(jsonValue['status']))
        return [{'status': str(jsonValue['status']), 'url': url}]
    return extractAddress(jsonValue)

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

def re_read(data, api_id = API_ID, lang = 'zh-CN'):
    num = 0
    unread = False
    while True:
        for d in data:
            for i in range(len(d[3])):
                if type(d[3][i]) == dict:
                    num += 1
                    print('Re-reading item...' + str(num))
                    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=' + str(lang) + '&pagetoken=' + str(d[3][i]['token']) + '&key=' + str(api_id)
                    jsonValue = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
                    if jsonValue['status'] == 'INVALID_REQUEST':
                        unread = True
                        continue
                    unread = unread or False #Bug here.
                    del d[3][i]
                    d[3] += extractAddress(jsonValue)
                    time.sleep(1)
        if not unread:
            break
    return data
    

def writeRawResults(results, file):
    fp = open(file, 'w+')
    fp.write(json.dumps(results))
    fp.close()

def run(bank, file='TODO', api_id = API_ID, threads=1):
    cities = readLine('cities.csv', 1)
    return re_read(runThrough(cities,bank, api_id,radius=10000,file=file), api_id)