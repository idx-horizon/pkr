from operator import attrgetter
import app.newruns as nr
import app.utils as utils

def getmap(current_user, session):
   style="height:60%;width:90%;margin:5%"
   markers=get_map_markers(
            centre='bromley',
            current_user=current_user, 
            session=session)
                
   mymap = Map(
        identifier="mymap", 
        lat=51.386539, # currently set to Bromley
        lng=0.022874, 
        zoom=9, 
        style=style,
        region="UK",
        markers= markers
   )     
   return mymap


def make_infobox(d):
   info = f'<P><B>{d.evshortname}</B><P>Difficulty: <B>{d.sss_score}</B><P>Times run: <B>{d.occurrences}</B>'
   
   return info
   
def get_map_markers(filterby='', 
                     centre='bromley',
                     current_user=None,
                     session=None):
   max_events = 1000
   iconbase = "https://maps.google.com/mapfiles/ms/icons"

   all_events = nr.getevents_by_filter(filterby, centre_on=centre)
      
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
   
   for idx, d in enumerate(data):
      icon = 'green-dot.png' if d.hasrun else 'red-dot.png'
      if idx == 0:
         icon = 'blue-dot.png'
         
      markers.append({'lat': d.latitude,
                      'lng': d.longitude,
                      'icon': f'{iconbase}/{icon}',
                      'infobox': make_infobox(d)
                      })
   return markers
                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
