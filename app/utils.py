import requests
import os
import datetime
import app.extract as e
import json
from collections import Counter
import string
import statistics
import re
import datetime
import math

EVENT_URL = 'https://images.parkrun.com/events.json'

def find_in_list_dict(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None
    
class Runner():
	
	base = 'https://www.parkrun.org.uk/results/athleteeventresultshistory/?athleteNumber={}&eventNumber=0'
	def run(self):
		pass
		
	def __init__(self, id):
		self.id = id
		self.url = Runner.base.format(self.id)
		self.runs = None
		self.cached = None
		self.updated_dt = None
		self.fullname = None
		self.name = None
				
	def get_runs(self, filter=None, refresh=True):
		local_fname = '{}.pkr'.format(self.id)
		def save_local(data):
			with open(local_fname, 'w', encoding='utf-8') as fh:
				fh.write(data)
		
		def get_local():
			with open(local_fname, 'r', encoding='utf-8') as fh:
				return json.loads(fh.read())
		
		print('** Filter: {} Refresh: {} - File {} in {} **'.format(
					filter, refresh,
					local_fname, 
					os.getcwd()
					)
			)
						
		if refresh or not os.path.exists(local_fname):
			page = get(self.url).text
			data = e.extract_tables(page)[3]
#			s = json.dumps(data)
			self.cached = 'new'
			#save_local(json.dumps(data))
			save_local(json.dumps((countries, data)))

		else:
			countries, data = get_local()
			self.cached = 'cached'
		
		self.updated_dt = get_file_details(local_fname)
		self.run_count = len(data['runs'])
		try:
			self.fullname = data['title'][:data['title'].index('-')].strip()
		except:
			self.fullname = data['title']

		self.name = self.fullname[:self.fullname.index(' ')]
		if not filter:
			self.runs = data['runs']
		else:
			self.runs = [x for x in data['runs'] if x['Event'].lower().startswith(filter.lower())]
			
		self.countries = countries
		self.caption = data['caption']
		
		self.threshold = '00:00'				
		
	#	event_counter = self.count_by()
	#	self.missing = {x.upper() for x in event_counter if event_counter[x]==0}
	#	self.letters = {x:event_counter[x] for x in event_counter if event_counter[x]!=0}
		
		event_occ = Counter(x['Event'] for x in self.runs)
		for x in self.runs:
 			x['occurrences'] = event_occ[x['Event']]		
		self.fastest = '-'
		self.slowest = '-'
		self.average = '-'
		  		
		self.stats = self.get_stats()
		self.challenges = self.get_challenges()

	def holiday_runs(self, month, day):
		dts = [datetime.datetime.strptime(x['Run Date'],'%d/%m/%Y') for x in self.runs]
		
		yrs = []
		for i in range(min(dts).year, max(dts).year + 1 ):
 			if datetime.datetime(i, month, day, 0, 0) in dts: 
 				runs = [x['Event'] for x in self.runs if x['Run Date'] == '{:02d}/{:02d}/{}'.format(day, month, i)]
 				yrs.append('{}: {}'.format(i, ', '.join(runs)))
 				
		if len(yrs) == 0:
			return '-'
		else:
			return '{}~{}'.format(len(yrs), '~'.join(yrs))

			
	def get_challenges(self):
		challenges = {}
		if len(self.runs) == 0:
			return challenges
			
		challenges['Last run'] = '{} at {}'.format(fdate(self.runs[0]['Run Date']), self.runs[0]['Event'])
		challenges['Current series'] = self.current_series()
		challenges['Parkruns this year'] = self.stats['_YR_' + str(datetime.datetime.now().year)]
		challenges['Total number of runs'] = self.run_count
		challenges['Events run'] = len([x for x in self.stats if x.startswith('_EVENT_')])
		
		challenges['Number of PBs'] = self.stats['_PB']
		last_PB_ix = find_in_list_dict(self.runs,'PB?','PB')  or 0
		challenges['Last PB'] = '{} at {} ({} runs ago)'.format(
									fdate(self.runs[last_PB_ix]['Run Date']),
									self.runs[last_PB_ix]['Event'],
									last_PB_ix) 
		
		bingo = Counter([datetime.datetime.strptime(x['Run Date'],'%d/%m/%Y').strftime('%d-%b') for x in self.runs])
		challenges['Calendar Bingo'] = '{}~Most common date: {} times on {}'.format(
						len(bingo), 
						bingo.most_common(1)[0][1], 
						bingo.most_common(1)[0][0]) 
		
		challenges['Alphabet A-Z']    = self.alphabet()
		challenges['Stopwatch 00-59'] = self.stopwatch()
		challenges['Position 00-99']  = self.position()
		challenges['Fibonacci series'] = self.num_series('Fibonacci')
		challenges['Primes series']    = self.num_series('Prime')
		challenges['Cowell Club'] = self.cowell()
		challenges['Lockdown']    = self.lockdown()

		challenges['Total parkrun distance'] = '{}km'.format(self.run_count * 5) 
		
		key = max({x for x in self.stats if x.startswith('_YR_')}, 
						key=lambda key: self.stats[key])
		challenges['Most parkruns in a year'] = '{} in {}'.format(self.stats[key], key.replace('_YR_',''))
				
		key = max({x for x in self.stats if x.startswith('_EVENT_')}, 
						key=lambda key: self.stats[key])		
		challenges['Most common event'] = '{} at {}'.format(self.stats[key], key.replace('_EVENT_',''))
		challenges['Singleton events'] = '{}'.format(len([x for x in self.stats if x.startswith('_EVENT_') and self.stats[x]==1]))
		
		pix = 0
		ev = sorted([self.stats[x] for x in self.stats if x.startswith('_EVENT_')], reverse=True)
		for ix, element in enumerate(ev):
			if element>ix:
				pix = ix+1
			else:
				break		
		challenges['p-index'] = pix
		
		rn = sorted(set([int(x['Run Number']) for x in self.runs]))
		wix = sorted(list(
				set(range(1,max(rn)))
				-set(rn)))[0]-1
		challenges['Wilson-index'] = wix
		
		challenges['Parkrun birthday'] = '{} at {}'.format(
						fdate(self.runs[-1]['Run Date']), 
						self.runs[-1]['Event']
						)
		
		yr = sorted([x.replace('_YR_','') for x in self.stats if x.startswith('_YR_')])
		challenges['Years running'] = '{} ({} to {})'.format(len(yr), yr[0], yr[-1])

		challenges['Tourist Quotient'] = '{:%}'.format(
							len([x for x in self.stats if x.startswith('_EVENT_')]) / self.run_count
							)
		streak = 0
		seen = []
		for ele in [x['Event'] for x in self.runs]:
			if ele in seen: break
			else:
				streak+=1
				seen.append(ele)
    
		challenges['Current tourism streak'] = streak
		challenges['Longest tourism streak'] = 'tbc'
		challenges['Total distance travelled'] = 'tbc'
		
		challenges['Countries visited'] = '🌍 {} ({})'.format(len(self.countries),  ', '.join(self.countries))
		
		for k,v in [('Time', '⏱ Time'), ('AgeGrade','Age grading'), ('Pos', '🏅 Position')]:
			element = ['{:>4}'.format(t[k]) for t in self.runs]	
			challenges[v + ' (range)'] = '{} --> {}'.format(min(element).strip(), max(element).strip())
		
		times = [sum(x * int(t) for x, t in zip([60, 1], ele['Time'].split(":"))) for ele in self.runs]
		challenges['Average run time'] = '{}'.format(datetime.timedelta(seconds=round(statistics.mean(times))))
		challenges['Total run time']   = '⏱ {}'.format(str(datetime.timedelta(seconds=sum(times))))
		
		challenges['Christmas Day'] = self.holiday_runs(12,25)
		challenges['New Year Day'] = self.holiday_runs(1,1)

		challenges['Bushy Pilgrimage'] = fdate(self.regex_test('bushy','Run Date', 'single'))
		challenges['Bee Gees'] = self.regex_test('^B|^G', 'Event','list')
		challenges['Pirates'] = '🏴‍☠️ {}'.format( self.regex_test('^C|^R', 'Event','list'))
		challenges['Compass'] = '🧭 {}'.format(self.regex_test('north|east|south|east', 'Event', 'list'))
		challenges['Full Ponty'] = self.regex_test('ponty', 'Event', 'list')		

		
		return challenges

	def lockdown(self):
		evs = [x['Run Date'] for x in self.runs if x['Run Date'] in ('14/03/2020', '24/07/2021')]
		if len(evs) == 2:
			return 'Last & First'
		elif len(evs) == 1 and evs[0].endswith('2020'):
			return 'Last before lockdown'
		elif  len(evs) == 1 and evs[0].endswith('2021'):
			return 'First after lockdown'
		else:
			return '-'

	def num_series(self,name):
		series_dict = {
			'Fibonacci':  [1,2,3,5,8,13,21,34,55,89,144,233,377,630],
			'Prime':      [2,3,5,7,11,13,17,17,19,23,29,31,37,41,43,47]
		}
		series = series_dict[name]
		
		matching = set([int(x['Run Number']) for x in self.runs if int(x['Run Number']) in series])
		missing = set(series) - set(matching)
		
		if len(series) == len(matching):
			return '💹 100% - (first {} numbers of {} series)'.format(len(series),name)
		else:
			return '💹 {:0.0%} - missing {} out of {}~Missing: {}'.format(
							len(matching)/len(series),
							len(missing),
							len(series),
							', '.join([str(x) for x in sorted(missing)])
							)
							
	def alphabet(self):
		#alphabet (discounts X, so only 25 letters)
		event_counter = self.count_by()
		missing = {x.upper() for x in event_counter if event_counter[x]==0 and x != 'x'}
		if len(missing) == 0:
			return '🔤 100% - All letters (except X)'
		else:
			return '🔤 {:0.0%} - {} letters (missing {})'.format(
							(25 - len(missing))/25,
							25 - len(missing),
							', '.join(sorted(missing))
							)

	def stopwatch(self):
		k = len({x for x in self.stats if self.stats[x]!=0 and x.startswith('_SEC_')})
		if k == 60:
			return '⏱ 100% - 60 out of 60'
		else:  
			return '⏱ {:0.0%} - {} out of 60~Missing: {}'.format(
		 				k/60,
						k, 
						', '.join(sorted({x.replace('_SEC_','') for x in self.stats if self.stats[x]==0 and x.startswith('_SEC_')})) 
						)
	def position(self):
		k = len({x for x in self.stats if self.stats[x]!=0 and x.startswith('_POS_')})
		if k == 100:
			return '💯 100% - 100 out of 100'
		else:  
			return '💯 {:0.0%} {} out of 100~Missing: {}'.format(
						k/100,
						k, 
						', '.join(sorted({x.replace('_POS_','') for x in self.stats if self.stats[x]==0 and x.startswith('_POS_')})) 
						)
	
		
	def cowell(self):
		levels = {0: '-',
				  1: 'Quarter',
				  2: '🐮 Half',
				  3: '🐮 Three quarter'
		}
				  
		evs = len([x for x in self.stats if x.startswith('_EVENT_')])

		if evs > 99:
			return '🐮 Full'
		else:
			return levels[math.floor(evs/25)]
			
	def regex_test(self, pattern, attribute, returntype):
		lst = sorted(set([x[attribute] for x in self.runs if re.search(pattern, x['Event'], re.IGNORECASE)]))	
		if returntype == 'single':
			return lst[0] if len(lst) > 0 else '-'
		else:
			return '~'.join(lst) if len(lst) > 0 else '-'
				
	def run_gen(self):
		ix = -1
		
		while True:
			ix+=1
			yield self.runs[ix]
	
	def convert_date(self, strdate, format='%d/%m/%Y'):
		return datetime.datetime.strptime(strdate,format)
		
	def current_series(self):
		try:
			diff = 0 
			num_runs = 0
			seq = self.run_gen()
			first_run = next(seq)
			current_run = first_run
			current_dt = self.convert_date(current_run['Run Date'])
			
			while diff < 8:
				num_runs += 1
				prev_run = next(seq)
				prev_dt = self.convert_date(prev_run['Run Date'])
				diff = (current_dt - prev_dt).days
				
				current_run = prev_run
				current_dt = prev_dt
			
			if num_runs == 1:
				return '{} - {} at {}'.format(
						num_runs, 
						datetime.datetime.strftime(prev_dt+datetime.timedelta(days=diff),'%d-%b-%Y'),
						first_run['Event']
						)	
			else:
				return '{}~From: {} at {} to {} at {}'.format(
						num_runs,	
						datetime.datetime.strftime(prev_dt+datetime.timedelta(days=diff),'%d-%b-%Y'),
						current_run['Event'],
						fdate(self.runs[0]['Run Date']),
						self.runs[0]['Event']
						)	
		except Exception as e:
			return 'Unavailable'
					
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
		stats.update({'_POS_{:02}'.format(s):0 for s in range(100)})
		stats.update('_SEC_' + t['Time'][-2:] for t in self.runs) 	
		stats.update('_PB' for t in self.runs if t['PB?']!='')
		stats.update('_YR_' + t['Run Date'][-4:] for t in self.runs)
		stats.update('_EVENT_' + t['Event'] for t in self.runs)
		stats.update('_POS_' + t['Pos'][-2:].zfill(2) for t in self.runs)
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

def fdate(src, src_format='%d/%m/%Y',target_format='%d-%b-%Y'):
	try:
		return datetime.datetime.strptime(src, src_format).strftime(target_format)
	except:
		return src
# -----------
# MAIN
# -----------
if __name__ == '__main__':
#	for r in (184594, 4327482):
	runners = []
	for r in (184594,4327482,6594419, 2564629):
		o = Runner(r)
		o.get_runs(None,False)
		runners.append(o)
#		runner.append Runner(r)
		#print(runner)
#		runner.get_runs(None, False)
		print(o)