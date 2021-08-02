from collections import Counter
from operator import attrgetter

def year_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Run Date'][-4:]] += 1
        
    data = [{'year': k,'count': v} for k,v in c.items()]

    return sorted(data,key=lambda x: x['year'], reverse=True)     
#    return sorted(data,key=attrgetter('year'))        

    
def event_summary(runs):
    c = Counter()
    for r in runs: 
        c[r['Event']] += 1

    data = [{'year': k,'count': v} for k,v in c.items()]

    return sorted(data,key=lambda x: x['count'], reverse=True)     
#    return sorted(data,reverse=True, key=attrgetter('count'))        
        
#    return [{'event': k,'count': v} for k,v in c.items()]        

#    return sorted([{'year': k,'count': v} for k,v in c.items()],reverse=True, key=attrgetter('count'))        
