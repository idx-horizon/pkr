import app.utils

def get_cancellations():
    url ='https://www.parkrun.org.uk/cancellations'
    page = utils.get(url)
    
    soup = BeautifulSoup(c.text)
    ul = soup.find_all('ul')
    h2 = soup.find_all('h2')
​
    title = h2[0].text
​
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

​   return title, d
