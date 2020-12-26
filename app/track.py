import datetime

class Tracker:
    meta = {'name': 'PKR API',
            'version': '1.0',
            'last_visit': datetime.datetime.now(),
            'total_visits': 0,
            'POST': 0,
            'GET': 0,
            'ip_addresses': []}
                
    def __init__(self):
        pass
        
    def update(self, request):
        Tracker.meta['total_visits'] += 1
        Tracker.meta['last_visit'] = datetime.datetime.now()
        Tracker.meta[request.method.upper()] += 1
        Tracker.meta['last_ip'] = str(request.headers.get('X-Forwarded-For', 'Unknown'))
