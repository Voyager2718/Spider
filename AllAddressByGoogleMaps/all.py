import urllib.request, json
from math import radians, cos, sin, asin, sqrt

API_ID = 'YOUR_GOOGLE_API_ID'

def readLine(file):
    fp = open(file,'r+')
    line = fp.readline()
    array = []
    while(line != ''):
            array += [line.replace('\n','').split(',')]
            line = fp.readline()
    fp.close()
    return array



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
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

def getAddresses(coord, keyword, api_id = API_ID, lang = 'zh-CN', radius = 5000):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)  
    value = urllib.request.urlopen(url).read().decode('utf-8')
    jsonValue = json.loads(value)
    if jsonValue['status'] == 'REQUEST_DENIED':
        print('Error:', jsonValue['error_message'])
        print(url)
        return None
    return extractAddress(jsonValue)

def writeReversely(array,file):
    fp = open(file,'w+')
    for item in array:
            fp.write(item[0] + ',')
            fp.write(item[1] + ',')
            fp.write(item[2] + ',')
            fp.write(item[4] + ',')
            fp.write(item[3] + '\n')
    fp.close()