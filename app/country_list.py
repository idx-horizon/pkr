country_dict = {
    'au': {'id': 3,  'name': 'Australia','base': 'parkrun.com.au'},
    'ca': {'id': 14, 'name': 'Canada', 'base': 'parkrun.ca'},
    'dk': {'id': 23, 'name': 'Denmark', 'base': 'parkrun.dk'},
    'fi': {'id': 30, 'name': 'Finland', 'base': 'parkrun.fi'},
    'fr': {'id': 31, 'name': 'France', 'base': 'parkrun.fr'},
    'de': {'id': 32, 'name': 'Germany','base': 'parkrun.com.de'},
    'ie': {'id': 42, 'name': 'Ireland', 'base': 'parkrun.ie'},
    'it': {'id': 44, 'name': 'Italy', 'base': 'parkrun.it'},
    'jp': {'id': 46, 'name': 'Japan', 'base': 'parkrun.jp'},
    'my': {'id': 57, 'name': 'Malaysia', 'base': 'parkrun.my'},
    'nl': {'id': 64, 'name': 'Netherlands','base': 'parkrun.co.nl'},
    'nz': {'id': 65, 'name': 'New Zealand', 'base': 'parkrun.co.nz'},
    'no': {'id': 67, 'name': 'Norway', 'base': 'parkrun.no'},
    'pl': {'id': 74, 'name': 'Poland', 'base': 'parkrun.pl'},
    'ru': {'id': 79, 'name': 'Russia', 'base': 'parkrun.ru'},
    'sg': {'id': 82, 'name': 'Singapore', 'base': 'parkrun.sg'},
    'za': {'id': 85, 'name': 'South Africa', 'base': 'parkrun.za'},
    'se': {'id': 88, 'name': 'Sweden', 'base': 'parkrun.se'},
    'uk': {'id': 97, 'name': 'UK', 'base': 'parkrun.org.uk'},
    'us': {'id': 98, 'name': 'USA', 'base': 'parkrun.us'}
}


from app.models import Location
def get_centres():
    locations = Location.query.all()
    d={}
    for c in locations:
       d[c.ln_name] = (c.ln_lat, c.ln_long)
    return d

centres = get_centres()


#centres = {
#        'bromley': (51.386539,0.022874),
#        'bushy': (51.410992,-0.335791),
#		'banstead': (51.307648, -0.184225),
#		'lloyd':    (51.364807,-0.079973),
#		'wepre': (53.205552,-3.056846),
#		'woking': (51.311708,-0.556204),
#		'southnorwood' : (51.396111, -0.059908)
#        }

    
    
