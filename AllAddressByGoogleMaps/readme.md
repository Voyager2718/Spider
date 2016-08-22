Resume
==
Last week, my girl friend was writing her financial paper. She needs a data called *Headquarter to sub branch distance* in China. However, after have asked nearly all the sellers on *Taobao*, we cannot find out anyone who can collect this data. So I decided to help my girl to get this data. This passage will describe how we can get all the data by using Google Maps API. I found so many unforeseeable exceptions while developing this project. This passage will also tell you what are the problems as well as how to resolve them.

----
Google API
==
First of all, we have to register a Google API key, and while I was using the API, it was free and provided 150,000 queries per day.
We need to go to https://console.developers.google.com/ to get an API key, create a project, then enable the *Google Place API Web Service* at API manager.
After have enabled this API, we can get data from Google Maps.

----
urllib
==
In Python 3, we need to use *urllib* to fire a request and get data. (It's almost the same in Python 2. Please check it on http://Python.org)
What we need is **urllib.request**, **urllib.parse** and **HTTPError** in **urllib.error**.
Moreover, we still need to handle json and do some math calculations. 
So we just import them into out project.
```Python
import urllib.request, urllib.parse, json
from urllib.error import HTTPError
from math import radians, cos, sin, asin, sqrt, pi
import time
import os
```

----
Prelude
==
We need to do find out all the addresses for all the listed banks in China. So let's just define some information like the name of bank, the coordinate of headquarters of banks.
```Python
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
```

----
Cities's coordinates
==
I believe that most sub branch banks are in cities. So I found a list that contents all cities and its's coordinates in China. And we convert it into csv file so that we can use it easily.
The csv file that we needs shall be like
```Text
P0,P1,P2,Longitude,Latitude,Size
广东省,广州市,荔湾区,23.13,113.27,0
...
```
I uploaded to my GitHub, here's the link: 
https://github.com/Voyager2718/Spider/blob/develop/AllAddressByGoogleMaps/cities.csv
Then we should define a function to read the csv file.
```Python
def getCities(file, passHead = 1):
    """
    Get all cities and its' coordinate.
    @param passHead: How many head line should be ignored.
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
```
This function is quite simple, just read the file and return a list that contains all single lines.
And the second parameter is used for ignoring head lines.

----
Distance between 2 coordinates
==
I found this function on [StackOverflow](http://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula) that can be used. But I modified a little to make it more clear and adapt to Google API. The 2 parameters are coordinates that formed into a tuple (Like `(23.13,113.27)`).
```Python
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
```
The unit of return value is kilometer.

----
Google Place API
==
API parameters
--
According to [Google Place API](https://developers.google.com/places/web-service/search), we need to create a request to the following URL to get data.
`https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&types=food&name=cruise&key=YOUR_API_KEY`
Where
|parameter|Detail|
|---------|-----------------------------------------------|
|key      |The API key that we applied above.             |
|location |The coordinates that we want to search.        |
|radius   |The radius of the range that we want to search.|

or
|parameter|Detail|
|---------|-----------------------------------------------|
|key      |The API key that we applied above.             |
|pagetoken|Page token for multi-pages.                    |

are **required**. It means that we can either choose parameters on the first table or parameters on the second table.
In this project, we need other optional parameters.
|parameter|Detail|
|---------|-----------------------------------------------|
|language |The language that we want in return JSON.      |
|keyword  |The keyword of the POI that we want.           |
|types    |The type of POI that we want.                  |

As we can see on [Google Place API](https://developers.google.com/places/web-service/search), it will return only 20 POI per request and 60 POI in total. And if there are other pages, the API will return the JSON with a specifics key **next_page_token**. So if we found the key **next_page_token** in the return JSON, we shall request for other results.
<br />
**However, according to a question on [StackOverflow](http://stackoverflow.com/questions/18724736/google-place-invalid-request-while-sending-request-to-get-next-page-results) and my experience, if we request for other pages after have gotten the first page immediately, the API will very likely to return an *INVALID_REQUEST* exception. Although the official documents said that the API will delay for *a while*, however, I found it may delay for *3-5 minutes* which makes this delay unacceptable. So we *have to* request for other pages after a couple of minutes. We will see how to handle this problem in the following chapters.**

<br />
Then we just form 2 functions to establish the URL that we want.
```Python
def getOtherPages(token, api_id = API_ID, lang = 'zh-CN'):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=' + str(lang) + '&pagetoken=' + str(token) + '&key=' + str(api_id)
    return query(url)

def getResults(coord, keyword, api_id = API_ID, type = 'bank', lang = 'zh-CN', radius = 10000):
    keyword = urllib.parse.quote(keyword) 
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?types=' + str(type) +'&location=' + str(coord[0]) + ',' + str(coord[1]) + '&radius=' + str(radius) + '&keyword=' + str(keyword) + '&language=' + str(lang) + '&key=' + str(api_id)
    return query(url)
```
`urllib.parse.quote(keyword) ` will encode the keyword into *URL percent-coding* so that we can use Unicode (to support different characters apart from ASCII) in the request.

----
Query
--
After have established the URL, we should query for information.
Then we should define a function **query** like
```Python
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
```
While requesting for information, the API might sometimes return a 500 error, 503 error, etc. Then `urllib.request.urlopen()` will raise a **HTTPError**. But we shall not give up and we need to request again. So we should put the codes into an infinite loop and break it if request has succeed. 
That's the reason why we use
```Python
while True:
	try:
		urllib.request.urlopen(something)
	except HTTPError:
		print('HTTPError')
```
Then we shall put a bunch of **if** to catch different kind of conditions.
If the status of the request is `'OK'` or `'ZERO_RESULTS'`, then we determine if `'next_page_token'` is in the return JSON. If there is, we return the page token and leave it to be handled in the upper structure. Else we just return the results.
And we handle other conditions in that bunch of **if**.
Finally, it leave us only `'INVALID_REQUEST'` error which is likely means that we shall request the URL later as we've talked about above. So we just return the URL.

----
Get all results
--
As we talked about above, we need to get other pages with delay. So we have to define another function to handle **next_page_token** at the end of all requests.
```Python
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
```
First of all, we do not need duplicated values, so we should have a list **ids** that contains all unique **id**.
And the structure
```Python
for res in result['results']:
	if res['id'] not in ids:
		...
```
will check if the **id** is in the list. If not, we shall add the result to the list **results**.
Then we need to re-read all the results to check if there are other page needs to be read. So we use `for result in results` to check if there is `'token'` in each result. If there is and there is no error (No `'url'` in result. If there's `'url'`, it means that the API has returned a **INVALID_REQUEST**, so that we need to leave it alone and wait for the next round of re-read.) , we process a re-read and add the results into the list **results**. 
And finally, we need to check it again to see if there'are still any `'next_page_token'` that needs to be re-read.
We should loop infinitely if there're always a `'next_page_token'` so that we put our codes into a `while True` loop and break it if there is no more `'next_page_token'`.

----
Extract results
==
The results of request is an **Object** that contains all results from API. So we have to define functions to extract the results that satisfy us.
In this cast, we should define a function
```Python
def extractCoords(data):
    coords = []
    for item in data:
        coords += [(item[3]['geometry']['location']['lat'],item[3]['geometry']['location']['lng'])]
    return coords
```
to extract all coordinates.

----
Run for all banks
==
To reduce our works, we shall define a function that run for all banks.
```Python
def runAll(cities, extractFunction, source = banks, api_id = API_ID, type = 'bank', lang = 'zh-CN', radius = 10000):
    results = {}
    for s in source:
        results[s] = extractFunction(getResultsInCitiesDelayed(cities, s, api_id, type, lang, radius))
    return results
```
This function will run for all banks that are listed in **banks** and return a dictionary that indicates results for all banks like
```
{'平安银行':[results],'宁波银行':[results],...}
```

----
Average distance
==
Finally we need to define functions to calculate average distance for each banks.
```Python
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
```
`getAllAverageDistance` will return the average distance for each banks in a dictionary.

----
Test
==
```Text
>>> all = runAll(getCities('cities.csv'),extractCoords,api_id='AIzaSyCcJUqHWucOoG9r1nscshfBRQE6oycDY04')
Running in method delay...平安银行 1/3179
Running in method delay...平安银行 2/3179
Running in method delay...平安银行 3/3179
Running in method delay...平安银行 4/3179
Running in method delay...平安银行 5/3179
Running in method delay...平安银行 6/3179
Running in method delay...平安银行 7/3179
```
Finally it will return values that we want.
Don't worry, my API ID has been changed. ;)

----
Project address
==
Try to check on my [GitHub](https://github.com/Voyager2718/Spider/tree/develop/AllAddressByGoogleMaps) to find the entire code.
<br />
(Branch **Master** recommended. Branch **new_algo** contains the algorithm that request immediately. So we will have to wait for a lone time because of the API delay)
