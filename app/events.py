import requests
import json
from bs4 import BeautifulSoup

def add_anniversary_info(saveto=None):
	events = refresh_events(None).json()
	anni = get_anniversary_data(False)
	
	for ev in events['events']['features']:
		a = [x for x in anni if x['Event'] == ev['properties']['EventLongName']]
		if len(a)==0:
			ev['anniversary'] = {}
		else:
			ev['annivesary']=a[0]

	if saveto:	
		json.dump(data.json(),open(saveto,'w'))
		print(f'** Refreshed: {saveto}')
			
	return events	

def myget(url):
	headers  =  {
		'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
	}	
		
	session = requests.Session()
	session.headers.update(headers)
	
	data = session.get(url)
	return data

def refresh_events(saveto=None):
	EVENT_URL = 'https://images.parkrun.com/events.json'
	
	data = myget(EVENT_URL)
	if data.ok and saveto:	
		json.dump(data.json(),open(saveto,'w'))
		print(f'** Refreshed: {saveto}')
		
	return data

def get_anniversary_data(refresh=False):
	ANNIVERSARY_URL = 'https://wiki.parkrun.com/index.php/Anniversaries'
	data = myget(ANNIVERSARY_URL)
	if data.ok:
		page = data.text	
		soup = BeautifulSoup(page,'html.parser')
		table = soup.find('table', class_="wikitable sortable")
		rows = table.find_all('tr')
		headers = [th.text.strip().replace('\n','').replace('YYYY MM DD','') for th in rows[0].find_all('th')]
		anniveraries = []
		for d in [x for x in rows if len(x.find_all('td'))>0]:
			tds = d.find_all('td')
			tmp = {}
			for ix, td in enumerate(tds):
				tmp[headers[ix]] = td.text.strip().replace('\n','')
			
			anniveraries.append(tmp)
			
		return anniveraries

def get_anniversaries():
	anni = get_anniversary_data()
	data = json.dumps(anni)
	local_fname = os.environ['HOME'] + r'/Documents/idx/anniversaries.json'	
	with open(local_fname, 'w', encoding='utf-8') as fh:
				fh.write(data)
	print('** Refreshed:', local_fname.replace(os.environ['HOME'],''))
	return anni
