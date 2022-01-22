import requests
import json
import datetime
import os
import pprint as pp

try:
	from app.resources import country_dict, centres
	from app.geo import measure
except:
	from resources import country_dict, centres
	from geo import measure

cJUNIOR = 2
cADULT = 1

class Event():
    def __init__(self, event, centre_on='bromley'):
        self.evid = event['id']
        self.evname = event['properties']['eventname']
        self.evshortname = event['properties']['EventShortName']
        self.evlongname = event['properties']['EventLongName']
        self.first_run = event['properties']['first_run']
        self.sss_score = event['properties']['sss_score']
        self.latitude = event['geometry']['coordinates'][1]
        self.longitude = event['geometry']['coordinates'][0]        
        self.domain = 'https://' + [country_dict[ele]['base'] for ele in country_dict if country_dict[ele]['id']==event['properties']['countrycode']][0] +'/'
#        self.domain = 'https://www.parkrun.org.uk/'
        self.url_latestresults =  self.domain + self.evname + '/results/latestresults/'
        self.url_course =  self.domain + self.evname + '/course/'
        self.distance = measure((self.latitude, self.longitude), centres[centre_on])
        self.hasrun = None
        self.occurrences = None

    def __repr__(self):
    	#return '{:<4}. {:<25}  {}'.format(self.evid, self.evshortname, self.url_course)
    	return str(self.__dict__)
    	
    def print(self):
        #print('{:<4}. {:<25}  {}'.format(self.evid, self.evshortname, self.url_latestresults))
        pp.pprint(self.__dict__)
        
    def get_dict(self):
        return {'id': self.evid, 'name': self.evshortname, 'latest_result': self.url_latestresults}

    def get_details(self):
        return '{:<4}. {:<25}  {}'.format(self.evid, self.evshortname, self.url_latestresults)
        
    def set_hasrun(self,value):
        self.hasrun = value

    def set_occurrences(self,value):
        self.occurrences = value


def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
    }

    session = requests.Session()
    session.headers.update(headers)
    return (session.get(url))


def get_last_update():
    return datetime.datetime.fromtimestamp(os.path.getctime('events.json')).strftime('%d-%b-%Y %H:%M')

def get_anniversaries():
    with open('anniversaries.json','r') as fin:
        return json.loads(fin.readlines()[0])
        
def get_sss_scores():
    try:
        with open('sss.json') as fin:
            data = json.loads(fin.read())

        return {i['event']: float(i['average_sss']) for i in data }	
        
    except Exception as e:
        return None

def getfile(refresh=False):
    fn_events ='events.json'
    if refresh:
        data = get('https://images.parkrun.com/events.json')
        json.dump(data.json(), open(fn_events, 'w'))
        print('** refreshed at {}'.format(get_last_update()))
        return data.json()

    with open(fn_events, 'r') as fin:
        return json.load(fin)

def getevents_by_filter(filter_str, countrycode='97', method='startswith', centre_on='bromley'):
    data = getfile(False)
    
    c_events = getevents(data, int(countrycode), cADULT)
    
    if method == 'startswith':
       return [Event(i,centre_on) for i in c_events if i['properties']['eventname'].startswith(filter_str)]
    else:
        return [Event(i,centre_on) for i in c_events if filter_str in i['properties']['eventname']]


def getevents(js, countrycode, seriesid):
    events = [x for x in js['events']['features'] if
            x['properties']['countrycode'] == countrycode and x['properties']['seriesid'] == seriesid]
    anni = get_anniversaries()
    sss = get_sss_scores()
    
    for e in events:
        try:
            first_run = [x['First Run'] for x in anni if x['Event']==e['properties']['EventLongName']][0]
        except:
            first_run='n/a'

        e['properties']['first_run']=first_run	

        try:
            e['properties']['sss_score'] = sss[e['properties']['EventShortName']]
        except:
            e['properties']['sss_score'] = 'n/a'

    return events

def get_last_newruns(lastlimit=10, country_code=97, centre_on='bromley'):
    js = getfile(False)

    cc_ev = getevents(js, country_code, cADULT)

    subset = []
    for ev in sorted(cc_ev, key=lambda k: k['id'])[-lastlimit:]:
        subset.append(Event(ev,centre_on))

    return subset
