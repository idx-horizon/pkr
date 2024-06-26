from collections import Counter
import time
# t1 = map(lambda  x:  (int(x['Time'][-5:-3])*60) + int(x['Time'][-2:]), runs)


def get_avg(lst):
    try:
        m = map(lambda x: (int(x[-8:-6]) * 60 * 60) + (int(x[-5:-3]) * 60) + int(x[-2:]), lst)
    except:
        print(x)
    return time.strftime('%H:%M:%S', time.gmtime(sum(m)/len(lst)))


def get_ystat_times(runs, k):

    l = [x['Time'].zfill(8) if len(x['Time']) > 5 else '00:' + x['Time'] for x in runs if x['Run Date'][-4:] == k]
    return (get_avg(l), min(l), max(l))
    

def get_estat_times(runs, k):

    l = [x['Time'].zfill(8) if len(x['Time']) > 5 else '00:' + x['Time'] for x in runs if x['Event'] == k]
    return (get_avg(l), min(l), max(l))


def year_summary(runs):
    def uniq_year(data, year):
        return len([x for x in data if x.startswith(str(year))])
        
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
    
    uniq_counter = Counter(
        x['Run Date'][-4:] + '-' + x['Event'] for x in runs
    )    
    
    d = get_event_years(runs)
    new_counter = Counter(
        [min(d[x]) for x in d]
    )
    
    different = 0
    data = [{'year': k,
             'count': v,
             'different_events': uniq_year(uniq_counter, k),
             'times': get_ystat_times(runs, k), 
             'new_events': new_counter[k],
             } for k, v in c.items()]

    return sorted(data, key=lambda x: x['year'], reverse=True)

def get_event_years(runs):
    d = {}
    for r in runs:
        if r['Event'] not in d.keys():
            d[r['Event']]=set()
        d[r['Event']].add(r['Run Date'][-4:])

    return d    

def event_summary(runs):
    c = Counter()
    d = get_event_years(runs)
    
    for r in runs: 
        c[r['Event']] += 1
        #if r['Event'] not in d.keys():
        #  d[r['Event']]=set()
        #d[r['Event']].add(r['Run Date'][-4:])
        
    data = [{'event': k,
             'count': v,
             'times': get_estat_times(runs, k), 
             'years': ', '.join(sorted(d[k])),
             'latest_year': max(d[k]), 
             'year_count': len(d),
             } for k, v in c.items()]

    return sorted(data, key=lambda x: x['count'], reverse=True)
    
