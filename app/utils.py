import requests
import os
import datetime
import app.extract as e
import json
from collections import Counter
import string
import statistics

EVENT_URL = 'https://images.parkrun.com/events.json'

class Runner():
	
	base = 'https://www.parkrun.org.uk/results/athleteeventresultshistory/?athleteNumber={}&eventNumber=0'
	
	def __init__(self, id):
		self.id = id
		self.url = Runner.base.format(self.id)
		self.runs = None
		self.cached = None
		self.updated_dt = None
		self.fullname = None
		self.name = None
				
	def get_runs(self, refresh=True):
		local_fname = '{}.pkr'.format(self.id)
		def save_local(data):
			with open(local_fname, 'w', encoding='utf-8') as fh:
				fh.write(data)
		
		def get_local():
			with open(local_fname, 'r', encoding='utf-8') as fh:
				return json.loads(fh.read())
						
		if refresh or not os.path.exists(local_fname):
			page = get(self.url).text
			data = e.extract_tables(page)[3]
#			s = json.dumps(data)
			self.cached = 'new'
			save_local(json.dumps(data))
		else:
			data = get_local()
			self.cached = 'cached'
		
		self.updated_dt = get_file_details(local_fname)
		self.run_count = len(data['runs'])
		self.fullname = data['title'][:data['title'].index('-')].strip()
		self.name = self.fullname[:self.fullname.index(' ')]
		self.runs = data['runs']
		self.caption = data['caption']		
		
		event_counter = self.count_by()
		self.missing = {x.upper() for x in event_counter if event_counter[x]==0}
		self.letters = {x:event_counter[x] for x in event_counter if event_counter[x]!=0}
		
		self.stats = self.get_stats()
		self.challenges = self.get_challenges()
		
#		self.stopwatch_ticks = 'Seconds: {} out of 60'.format(
#							len({x for x in self.stats if self.stats[x]!=0 and x.startswith('_SEC_')})
#						)
#		self.stopwatch_missing = ','.join({x for x in self.stats if self.stats[x]==0 and x.startswith('_SEC_')})
	
	def get_challenges(self):
		challenges = {}
		challenges['Stopwatch'] = '{} out of 60 (missing {})'.format(
							len({x for x in self.stats if self.stats[x]!=0 and x.startswith('_SEC_')}),
							','.join(sorted({x.replace('_SEC_','') for x in self.stats if self.stats[x]==0 and x.startswith('_SEC_')})) 
						)
		challenges['Alphabet'] = '{} letters (missing {})'.format(
							len(self.letters),
							','.join(self.missing)
						)
		challenges['Total number of runs'] = self.run_count
		challenges['Total parkrun distance'] = '{}km'.format(self.run_count * 5) 
		challenges['Number of PBs'] = self.stats['_PB']
		challenges['Events run'] = len([x for x in self.stats if x.startswith('_EVENT_')])
		
		key = max({x for x in self.stats if x.startswith('_YR_')}, 
																		key=lambda key: self.stats[key])
		challenges['Most parkruns in a year'] = '{} in {}'.format(self.stats[key], key.replace('_YR_',''))
		challenges['Parkruns this year'] = self.stats['_YR_' + str(datetime.datetime.now().year)]
				
		key = max({x for x in self.stats if x.startswith('_EVENT_')}, 
																		key=lambda key: self.stats[key])		
		challenges['Most common event'] = '{} at {}'.format(self.stats[key], key.replace('_EVENT_',''))
		challenges['Singleton events'] = '{}'.format(len([x for x in self.stats if x.startswith('_EVENT_') and self.stats[x]==1]))
		
		pix = 0
		ev = sorted([ss[self.stats] for x in self.stats if x.startswith('_EVENT_')], reverse=True)
		for ix, element in enumerate(ev):
			if element>ix:
				pix = ix
			else:
				break		
		challenges['p-index'] = pix-1
		
		rn = sorted(set([int(x['Run Number']) for x in self.runs]))
		wix = sorted(list(
				set(range(1,max(rn)))
				-set(rn)))[0]-1
		challenges['Wilson-index'] = wix
		
		challenges['Parkrun birthday'] = self.runs[-1]['Run Date']
		challenges['Years running'] = 'tbc'						
		challenges['Tourist Quotient'] = '{:%}'.format(
												len([x for x in self.stats if x.startswith('_EVENT_')]) / self.run_count
											)
		challenges['Longest tourism streak'] = 'tbc'
		challenges['Total distance travelled'] = 'tbc'
		challenges['Countries visited'] = 'tbc'		
		
		for k,v in [('Time', 'Time'), ('AgeGrade','Age grading'), ('Pos', 'Position')]:
			element = ['{:>4}'.format(t[k]) for t in self.runs]	
			challenges[v + ' (range)'] = '{} --> {}'.format(min(element).strip(), max(element).strip())
		
		times = [sum(x * int(t) for x, t in zip([60, 1], ele['Time'].split(":"))) for ele in self.runs]
		challenges['Average run time'] = '{}'.format(datetime.timedelta(seconds=round(statistics.mean(times))))
		challenges['Total run time']   = '{}'.format(str(datetime.timedelta(seconds=sum(times))))
		challenges['Last run'] = self.runs[0]['Run Date']

		return challenges
					
	def __str__(self):
		challenges = ''
		for c in self.challenges: 
			challenges += '{:<40} {}\n'.format(c, self.challenges[c])
		return 'Runner: {} | {} | {} | {} | {}\nChallenges:\n{}'.format(
									 self.id, 
									 self.name, 
									 len(self.runs), 
									 self.cached or '-', 
									 self.updated_dt,
									 challenges
									 )
	def __repr__(self):
		return self.__str__()
	
	def get_stats(self):
		stats = Counter({'_SEC_{:02}'.format(s):0 for s in range(60)})
		stats.update('_SEC_' + t['Time'][-2:] for t in self.runs) 	
		stats.update('_PB' for t in self.runs if t['PB?']!='')
		stats.update('_YR_' + t['Run Date'][-4:] for t in self.runs)
		stats.update('_EVENT_' + t['Event'] for t in self.runs)
		return stats
		
	def count_by(self):
		counter = Counter({l:0 for l in string.ascii_lowercase})
		counter.update(t['Event'][0].lower() for t in self.runs) 
		return counter


#
# helpers
#			
def get(url):
	headers  =  {
		'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
	}	
		
	session = requests.Session()
	session.headers.update(headers)
	return(session.get(url))

def get_file_details(fname):
	t = os.path.getmtime(fname)
	return datetime.datetime.fromtimestamp(t)
	
# -----------
# MAIN
# -----------
if __name__ == '__main__':
#	for r in (184594, 4327482):
	runners = []
	for r in (184594,4327482,6594419, 2564629):
		o = Runner(r)
		o.get_runs(False)
		runners.append(o)
#		runner.append Runner(r)
		#print(runner)
#		runner.get_runs(False)
		print(o)