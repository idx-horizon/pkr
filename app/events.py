import requests
import json

def g(url,saveto):
    session = requests.Session()
    d = session.get(url)
    