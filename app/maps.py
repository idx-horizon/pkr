from operator import attrgetter
import app.newruns as nr
import app.utils as utils
from flask_googlemaps import Map


def make_infobox(d):
   info = f'<P><B>{d.evshortname}</B><P>Difficulty: <B>{d.sss_score}</B><P>Times run: <B>{d.occurrences}</B>'
   
   return info
   
def get_map_markers(data): 
                     #filterby='', 
                     #centre='bromley',
                     #current_user=None,
                     #session=None):
   iconbase = "https://maps.google.com/mapfiles/ms/icons"

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

def getmap(data, centre, current_user, session):
   style="height:45%;width:100%;margin:0%"
   markers=get_map_markers(data)
#            data=data,
#            centre=centre,
#            current_user=current_user, 
#            session=session)
                
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


                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
