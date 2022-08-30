from operator import attrgetter
import app.newruns as nr

def make_infobox(d):
   info = f'<P>{d["evshortname"]}<P>Difficulty: {d["sss_score"]}'
   
   return info
   
def get_map_markers(filterby=''):
   max_events = 10
   icon = "https://maps.google.com/mapfiles/ms/icons/green-dot.png"

   all_events = nr.getevents_by_filter(filterby)
      
   data = sorted(all_events, key=attrgetter('distance'))[0:max_events]
   
   markers = []
   
   for d in data:
      markers.append({'lat': d['latitude'],
                      'lng': d['longitude'],
                      'icon': icon,
                      'infobox': make_infobox(d)
                      })
   return markers
                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
