import requests
import json

def getevents(saveto=None):
	EVENT_URL = 'https://images.parkrun.com/events.json'

	headers  =  {
		'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
	}	
		
	session = requests.Session()
	session.headers.update(headers)
	
	data = session.get(EVENT_URL)
	if data.ok:	
		json.dump(data.json(),open(saveto,'w'))
		print(f'** Refreshed: {saveto}')
		return data.json()
	else:
	 	return None
	
