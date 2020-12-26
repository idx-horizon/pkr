import datetime

class Tracker:
    meta = {'name': 'PKR API',
            'version': '1.0',
            'last_visit': datetime.datetime.now(),
            'last_ip': request.headers.get('X-Forwarded-For', 'Unknown'),
            'total_visits': 0,
            'POST': 0,
            'GET': 0,
            'ip_addresses': []}
                
    def __init__(self):
        pass
        
    def update(self, method):
        Tracker.meta['total_visits'] += 1
        Tracker.meta['last_visit'] = datetime.datetime.now()
        Tracker.meta[method] += 1