import json
from datetime import datetime, timedelta

def getdata(fn):
    with open(fn, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def get_all_days():
    base_year = 2020 # this is a leap year so 29 Feb is included
    start_date=datetime(base_year-1, 12, 31)
    end_date=datetime(base_year, 12, 31)
    d=start_date
    dates=[]
    while d < end_date:
        d += timedelta(days=1)
        dates.append( f'{d.month:02}/{d.day:02}' )

    return set(dates)

def calculate_next_saturday_for_date(dd, mm, start_year):
    yr = start_year
    today = datetime.today()
    
    while True:
        try:
            d = datetime(yr, mm, dd)
            if d.weekday() == 5 and d > today:     # 5 is Saturday
                return d
        except ValueError:
            #raise ValueError(f'Invalid date {dd}/{mm}/{yr}')
            pass
            
        yr += 1

def get_next_saturday_list(runs, initial_year=None):
    # this gets all possible days in a year (including 29-Feb) in 'mm/dd' format
    all_days = get_all_days()

    # dates in runs are formatted as 'dd/mm/yyyy', so pull out 'mm/dd'
    run_days = set(sorted([x['Run Date'][3:5] + '/' + x['Run Date'][0:2] for x in runs]))    

    missing_days = sorted(all_days - run_days)
    from_year = initial_year if initial_year else max([int(y['Run Date'][6:10]) for y in runs])
    
    all = sorted([calculate_next_saturday_for_date(
                            int(day[3:5]), 
                            int(day[0:2]), 
                            from_year) for day in missing_days])

    return {'next': all[0].strftime('%d-%b-%Y'),
            'last': all[-1].strftime('%d-%b-%Y'),
            'count': len(all),
            'all': all,}

if __name__ == "__main__":
    d = getdata('data/184594.pkr')
    runs = d[1]['runs']

    x = get_next_saturday_list(runs)
    print(f'{x["next"]} - {x["last"]}')

