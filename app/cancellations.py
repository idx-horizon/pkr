from bs4 import BeautifulSoup
import datetime

import app.utils

def get_cancellations():
    url ='https://www.parkrun.org.uk/cancellations'
    page = app.utils.get(url)

    as_at_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1)))
    
    dt_update = as_at_dt.strftime('%a %d-%b-%Y at %-I:%M%p')

    pg = BeautifulSoup(page.text)
    soup = pg.find('div', attrs={'id': 'primary'})
    ul = soup.find_all('ul')
    h2 = soup.find_all('h2')

    title = h2[0].text

    d = {}
    for idx, header in enumerate(h2[1:]):
        dt = header.text
        if 'Saturday' in dt:
            d[dt] = []
            li = ul[idx].find_all('li')
            for e in li:
                try:
                    ev, reason =  e.text.split(':',1)
                except:
                    ev = e.text
                    reason = '' 
                d[dt].append({'event': ev, 
                              'reason': reason, 
                              'link': e.find('a').get('href')
                             })
                                
    return title, d, dt_update
