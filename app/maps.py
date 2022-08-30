from operator import attrgetter
import app.newruns as nr
import app.utils as utils
from flask_googlemaps import Map


def make_infobox(d):
   info = f'<style>.infobox { background-color: lightgreen; }</style><div class="infobox"><h3 style="background-color:green;">Summary</h3>:<P><P><B>{d.evshortname}</B><P>Difficulty: <B>{d.sss_score}</B><P>Times run: <B>{d.occurrences}</B></div>'
   
   return info
   
def get_map_markers(data): 
   iconbase = "https://maps.google.com/mapfiles/ms/icons"

   markers = []
   
   for idx, d in enumerate(data):
      icon = 'green-dot.png' if d.hasrun else 'red-dot.png'
      if idx == 0:
         icon = 'blue-dot.png'
#         print('** Centre: ', type(d), d, '\n', make_infobox(d))
         
      markers.append({'lat': d.latitude,
                      'lng': d.longitude,
                      'icon': f'{iconbase}/{icon}',
                      'infobox': make_infobox(d)
                      })
   print(markers[0])
   print(markers[1])   
   return markers

def getmap(data, centres, centre_on, current_user, session):
   style="height:45%;width:100%;margin:0%"
   markers=get_map_markers(data)

   centre_lat, centre_lng = centres[centre_on]

   mymap = Map(
        identifier="mymap", 
        lat=centre_lat, # 51.386539, # currently set to Bromley
        lng=centre_lng, # 0.022874, 
        zoom=10, 
        style=style,
        region="UK",
        markers= markers
   )     
   return mymap


                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
