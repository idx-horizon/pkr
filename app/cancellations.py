from bs4 import BeautifulSoup
import datetime

import app.utils

def get_cancellations():
    url ='https://www.parkrun.org.uk/cancellations'
    page = app.utils.get(url)

    as_at_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1)))
    
    dt_update = as_at_dt.strftime('%a %d-%b-%Y at %-I:%M%p')

    soup = BeautifulSoup(page.text)
    ul = soup.find_all('ul')
    h2 = soup.find_all('h2')

    title = h2[0].text

    d = {}
    for idx, header in enumerate(h2):
        dt = header.text
        if 'Saturday' in dt:
            d[dt] = []
            li = ul[idx+4].find_all('li')
            for e in li:
                ev, reason =  e.text.split(':')
                d[dt].append({'event': ev, 
                              'reason': reason, 
                              'link': e.find('a').get('href')
                             })
                                
    return title, d, dt_update
