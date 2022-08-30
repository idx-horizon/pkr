from operator import attrgetter
import app.newruns as nr
import app.utils as utils

def make_infobox(d):
   info = f'<P><B>{d.evshortname}</B><P>Difficulty: <B>{d.sss_score}</B>'
   
   return info
   
def get_map_markers(filterby='',current_user=None):
   max_events = 50
   iconbase = "https://maps.google.com/mapfiles/ms/icons"

   all_events = nr.getevents_by_filter(filterby)
      
   data = sorted(all_events, key=attrgetter('distance'))[0:max_events]

   if not current_user.is_anonymous:
        SELECTEDRUNNER = session['SELECTEDRUNNER']
        base_runner = SELECTEDRUNNER['rid'] or current_user.rid
        rid = utils.Runner(str(base_runner).lower())
        rid.get_runs(filterby, False)

        for d in data:
            occ = len([x for x in rid.runs if x['Event'] == d.evshortname])
            d.set_occurrences(occ)
            if occ != 0:
                d.set_hasrun('Yes')

   
   markers = []
   
   for d in data:
      colour = 'green' if d.hasrun else 'red'
      
      markers.append({'lat': d.latitude,
                      'lng': d.longitude,
                      'icon': f'{iconbase}/{colour}-dot.png',
                      'infobox': make_infobox(d)
                      })
   return markers
                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
