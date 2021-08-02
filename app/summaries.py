from counters import Counter

def year_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
    return [{'year': k,'count': v} for k,v in c.items()]        
    
def event_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Event']] += 1
        
    return [{'event': k,'count': v} for k,v in c.items()]        
