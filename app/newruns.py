import requests
import json
import datetime
import os

cJUNIOR = 2
cADULT = 1


class Event():
    def __init__(self, event):
        self.evid = event['id']
        self.evname = event['properties']['eventname']
        self.evshortname = event['properties']['EventShortName']
        self.evlongname = event['properties']['EventLongName']
        self.url_latestresults = 'https://www.parkrun.org.uk/' + self.evname + '/results/latestresults/'

    def print(self):
        print('{:<4}. {:<25}  {}'.format(self.evid, self.evshortname, self.url_latestresults))

    def get_dict(self):
        return {'id': self.evid, 'name': self.evshortname, 'latest_result': self.url_latestresults}

    def get_details(self):
        return '{:<4}. {:<25}  {}'.format(self.evid, self.evshortname, self.url_latestresults)

def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
    }

    session = requests.Session()
    session.headers.update(headers)
    return (session.get(url))


def get_last_update():
    return datetime.datetime.fromtimestamp(os.path.getctime('events.json')).strftime('%d-%b-%Y %H:%M')


def getfile(refresh=False):
    fn_events ='events.json'
    if refresh:
        data = get('https://images.parkrun.com/events.json')
        json.dump(data.json(), open(fn_events, 'w'))
        print('** refreshed')
        return data.json()

    with open(fn_events, 'r') as fin:
        return json.load(fin)

def getevents_by_filter(filter_str, countrycode='97', method='startswith'):
    data = getfile(False)
    print('DATA:', data[0])
    
    c_events = getevents(data, int(countrycode), cADULT)
    
    if method == 'startswith':
       return [Event(i) for i in c_events if i['properties']['eventname'].startswith(filter_str)]
    else:
        return [Event(i) for i in c_events if filter_str in i['properties']['eventname']]


def getevents(js, countrycode, seriesid):
    return [x for x in js['events']['features'] if
            x['properties']['countrycode'] == countrycode and x['properties']['seriesid'] == seriesid]

def get_last_newruns(lastlimit=10, country_code=97):
    js = getfile(False)

    uk = getevents(js, country_code, cADULT)

    subset = []

    for ev in uk[-lastlimit:]:
        subset.append(Event(ev))

    return subset
