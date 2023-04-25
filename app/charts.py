import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import pandas as pd
from collections import Counter
import string

np.random.seed(1)



opts = {
    'Year': {
        'key': 'Run Date', 
        'start': -4, 'end': None, 
        'title': 'By Year', 'xlabel': 'Years',
        'bubble_factor': 2
    },
    'Month': {
        'key': 'Run Date', 
        'start': 3, 'end': 5, 
        'title': 'By Month', 'xlabel': 'Month',
        'include_vals': ['01','02','03','04','05','06','07','08','09','10','11','12'],
        'bubble_factor': 2
    },
    'Time': {
        'key': 'Time', 
        'start': -5, 'end': -3, 
        'title': 'Run time (minutes)', 'xlabel': 'Minutes (m)',
        'include_vals': range(25,40),
        'bubble_factor': 2
    },
    'AgeGrade': { 
        'key': 'AgeGrade' ,
        'start': 0, 'end': 2, 
        'title': 'Age Grading (%)', 'xlabel': '%',
        'include_vals': range(45,50),
        'bubble_factor': 2
    },
    'Event-Initial': {
        'key': 'Event', 
        'start': 0, 'end': 1, 
        'title': 'Event Letters', 'xlabel': 'Letter',
        'include_vals': list(string.ascii_uppercase),
        'bubble_factor': 1.5
    },
    'Event': {
        'key': 'Event', 
        'start': 0, 'end': None, 
        'title': 'Events', 'xlabel': 'Events',
        'bubble_factor': 1
    }
}

def getdata(fn):
    with open(fn,'r',encoding='utf-8') as f:
        return json.loads(f.read())[1]['runs']


def produce_graph(graph_name, data):
    g = opts[graph_name]
    t = sorted([x[g['key']][g['start'] : g['end']] for x in data])

    c=Counter(t)
    #c.update(t)
    if g.get('include_vals', None):
        for i in [str(x) for x in g['include_vals']]:
            if i not in c.keys():
                c[i]=0
    N = len(c)

    counts = [c[v] for v in sorted(c)]
    values = [v for v in c]

    colors = np.random.rand(N)

    area = [c[_]**g.get('bubble_factor',1) for _ in c]

    df = pd.DataFrame({
        'X': values,
        'Y': counts,
        'bubble_size': area})

    #xlimits = [int(min(c)),int(max(c))]
    plt.figure(figsize=(10,6))
    plt.scatter('X', 'Y', 
                 s='bubble_size',
                 alpha=0.6, 
                 c=None, 
                 marker='o',
                 edgecolors="grey", 
                 linewidth=3,
                 data=df)

    plt.xlabel(g['xlabel'], size=16)
    plt.ylabel("# runs", size=16)
    plt.ylim(ymin=0, ymax=max([c[_] for _ in c])+10)
    #plt.xlim([int(min(c)),int(max(c))])

    df2=pd.DataFrame([[c[lbl] for lbl in c]],columns=[lbl for lbl in values])

    cellcolors=[['xkcd:sky blue']*N]
    
    cellcolors=[['xkcd:sky blue']*N]
    for idx, v in enumerate([c[lbl] for lbl in c]):
        if v == 0:
            cellcolors[0][idx] = 'lightcoral'
    
    plt.table(cellText=df2.values, colLabels=df2.columns, 
              loc='center',
              rowLabels=['# runs'],
              cellLoc='center',
              cellColours=cellcolors,
              bbox=[0.0, -0.4, 1.0, 0.2])
    
            
    plt.title(g['title'], size=18)
    #plt.grid()
    plt.grid(color = 'green', linestyle = ':', linewidth = 0.8)

    plt.tight_layout()
#    plt.savefig("timebubbles.jpg", bbox_inches="tight")
    print('** returning from produce_graph')
    return get_chart_data(plt)
    #return plt

def get_chart_data(plt):
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

def make_chart(who):
    print('** in make_chart**')
    return produce_graph('Event-Initial',who.runs)
    
    