from collections import Counter

# t1 = map(lambda  x:  (int(x['Time'][-5:-3])*60) + int(x['Time'][-2:]), runs)

def get_stat_times(runs, k):

    l = [x['Time'] for x in runs if x['Run Date'][-4:] == k]
    return ( '-', min(l), max(l) )
    
    
def year_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
    
        
    data = [{'year': k,
             'count': v,
             'times': get_stat_times(runs, k), 
             } for k,v in c.items()]

    return sorted(data,key=lambda x: x['year'], reverse=True)     
    
def event_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Event']] += 1

    data = [{'event': k,'count': v,
             'fastest': '?', 
             'slowest': '?', 
             'average': '?'} for k,v in c.items()]

    return sorted(data,key=lambda x: x['count'], reverse=True)     
