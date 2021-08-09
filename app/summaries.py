from collections import Counter
import time
# t1 = map(lambda  x:  (int(x['Time'][-5:-3])*60) + int(x['Time'][-2:]), runs)
def get_avg(lst):
    m = map(lambda  x:  (int(x['Time'][-5:-3])*60) + int(x['Time'][-2:]), lst)
    return time.strftime('%H:%M:%S', time.gmtime(sum(m)/len(lst)))

def get_ystat_times(runs, k):

    l = [x['Time'] for x in runs if x['Run Date'][-4:] == k]
    return ( get_avg(l), min(l), max(l) )
    
def get_estat_times(runs, k):

    l = [x['Time'] for x in runs if x['Event'] == k]
    return ( get_avg(l), min(l), max(l) )
    
def year_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
    
        
    data = [{'year': k,
             'count': v,
             'times': get_ystat_times(runs, k), 
             } for k,v in c.items()]

    return sorted(data,key=lambda x: x['year'], reverse=True)     
    
def event_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Event']] += 1

    data = [{'event': k,
             'count': v,
             'times': get_estat_times(runs, k), 
             } for k,v in c.items()]

    return sorted(data,key=lambda x: x['count'], reverse=True)     
