from operator import attrgetter
import app.newruns as nr
import app.utils as utils
from flask_googlemaps import Map


def make_infobox(d):
   if d.occurrences:
      badge = f'<span  class="badge badge-pill badge-success">{d.occurrences}</span>'
   else:
      badge = '<span  class="badge badge-pill badge-danger">never</span>'
   
    
   style = '<style>.infobox { background-color: white; color:black; font-size: 12px} .tdr {text-align: right;} .thl {text-align:left; }</style>'
   
   info = f'<b>{d.evshortname}</b><P>Difficulty: <B>{d.sss_score}</B><P>Times run: <B>{d.occurrences}</B></div>'
   
   table = f'<div class="infobox"><table>' + \
      f'<tr><th class="thl"><B><U>{d.evshortname}</U></B></th><th></th></tr>' + \
      f'<tr><td>Difficulty</td><td class="tdr">{d.sss_score}</td></tr>' + \
      f'<tr><td>Times run</td><td class="tdr">' + badge + '</td></tr>' + \
      f'</table></div>'
      
   return style + table
   
def get_map_markers(data): 
   iconbase = "https://maps.google.com/mapfiles/ms/icons"
   iconbase = url_for('static')
   markers = []
   
   for idx, d in enumerate(data):
      icon = 'green1.png' if d.hasrun else 'red1.png'
      if idx == 0:
         icon = 'green0.png'
         
      markers.append({'lat': d.latitude,
                      'lng': d.longitude,
                      'icon': f'{iconbase}/{icon}',
                      'infobox': make_infobox(d)
                      })
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
        fullscreen_control=True,
        markers= markers
   )     
   return mymap


                      
#{evid': 2352, 'evname': 'bethlemroyalhospital', 'evshortname': 'Bethlem Royal Hospital', 'evlongname': 'Bethlem Royal Hospital parkrun', 'first_run': '2019-05-25', 'sss_score': 4.2, 'latitude': 51.385332, 'longitude': -0.029969, 'domain': 'https://parkrun.org.uk/', 'url_latestresults': 'https://parkrun.org.uk/bethlemroyalhospital/results/latestresults/', 'url_course': 'https://parkrun.org.uk/bethlemroyalhospital/course/', 'distance': 2.29, 'hasrun': None, 'occurrences': None}
