from collections import Counter

def year_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
        
    data = [{'year': k,'count': v} for k,v in c.items()]

    return sorted(data,key=lambda x: x['year'], reverse=True)     
    
def event_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Event']] += 1

    data = [{'event': k,'count': v} for k,v in c.items()]

    return sorted(data,key=lambda x: x['count'], reverse=True)     
