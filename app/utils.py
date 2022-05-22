# import datetime
import requests
import os
import json
from collections import Counter
import string
import statistics
import re
import datetime
import math

try:
    import app.extract as extract
except Exception as e:
    import extract

ANNIVERSARY_URL = 'https://wiki.parkrun.com/index.php/Anniversaries'
EVENT_URL = 'https://images.parkrun.com/events.json'


def last_saturday(dt=datetime.datetime.now().date()):
    return dt - datetime.timedelta(days=((dt.isoweekday() + 1) % 7))


def time_to_secs(runtime):
    if runtime.count(':') == 2:
        weights = [3600, 60, 1]
    else:
        weights = [60, 1]

    return sum(x * int(t) for x, t in zip(weights, runtime.split(":")))


def find_in_list_dict(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None


class Runner:
    base = 'https://www.parkrun.org.uk/parkrunner/{}/all/'

    def run(self):
        pass

    def __init__(self, rid):
        self.rid = rid
        self.url = Runner.base.format(self.rid)
        self.runs = None
        self.cached = None
        self.updated_dt = None
        self.fullname = None
        self.name = None
        self.countries = None
        self.stats = None
        self.challenges = None
        self.caption = None
        self.run_count = 0

    def get_runs(self, filter_by=None, refresh=True, sort_by='Date'):
        local_filename = '{}.pkr'.format(self.rid)

        def save_local(payload):
            with open(local_filename, 'w', encoding='utf-8') as fh:
                fh.write(payload)

        def get_local():
            with open(local_filename, 'r', encoding='utf-8') as fh:
                return json.loads(fh.read())

        print('** Filter: {} Refresh: {} - File {} in {} **'.format(
            filter_by, refresh,
            local_filename,
            os.getcwd()
        )
        )

        if refresh or not os.path.exists(local_filename):
            page = get(self.url).text
            print(self.url)
            data = extract.extract_tables(page)[3]
            countries = extract.get_run_links(page)
            self.cached = 'new'
            save_local(json.dumps((countries, data)))

        else:
            countries, data = get_local()
            self.cached = 'cached'

        self.updated_dt = get_file_details(local_filename)
        self.run_count = len(data['runs'])
        print(data['title'])
        self.fullname = data['title']
        self.name = self.fullname[:self.fullname.index(' ')]

        # add number of occurrences event has been run and
        # add timeSecs to represent Time in seconds
        ev_counter = Counter([ev['Event'] for ev in data['runs']])
        for ev in data['runs']:
            ev['occurrences'] = ev_counter[ev['Event']]
            ev['TimeSecs'] = time_to_secs(ev['Time'])

        if filter_by:
            if filter_by.lower().startswith('year='):
                self.runs = [x for x in data['runs'] if filter_by.lower().replace('year=', '') in x['Run Date']]
            else:
                self.runs = [x for x in data['runs'] if filter_by.lower() in x['Event'].lower()]
        else:
            self.runs = data['runs']

        if sort_by == 'run_pos':  # ascending position
            self.runs = sorted(self.runs, key=lambda d: int(d['Pos']))
        elif sort_by == 'age_grading':  # descending age
            self.runs = sorted(self.runs, key=lambda d: float(d['AgeGrade'].replace('%', '')), reverse=True)
        elif sort_by == 'event_no':  # ascending event/run number
            self.runs = sorted(self.runs, key=lambda d: int(d['Run Number']))
        elif sort_by == 'time':  # ascending Time
            self.runs = sorted(self.runs, key=lambda d: int(d['TimeSecs']))
        elif sort_by == 'date':  # already in reverse "Run Date" order
            pass

        self.caption = data['caption']
        self.countries = countries

        self.stats = self.get_stats()
        self.challenges = self.get_challenges()

    def holiday_runs(self, month, day):
        dts = [datetime.datetime.strptime(x['Run Date'], '%d/%m/%Y') for x in self.runs]

        yrs = []
        for i in range(min(dts).year, max(dts).year + 1):
            if datetime.datetime(i, month, day, 0, 0) in dts:
                runs = [x['Event'] for x in self.runs if x['Run Date'] == '{:02d}/{:02d}/{}'.format(day, month, i)]
                yrs.append('{}: {}'.format(i, ', '.join(runs)))

        if len(yrs) == 0:
            return '-'
        else:
            return '{}~{}'.format(len(yrs), '~'.join(yrs))

    def get_card_summary(self):
        pb = min([t['TimeSecs'] for t in self.runs])
        return 'PB: {}~{} runs @ {} events~Latest: {} at {} on {}'.format(
            str(datetime.timedelta(seconds=pb)),
            self.run_count,
            len([x for x in self.stats if x.startswith('_EVENT_')]),
            self.runs[0]['Time'],
            self.runs[0]['Event'],
            fdate(self.runs[0]['Run Date'])
        )

    def get_challenges(self):
        challenges = {}
        if len(self.runs) == 0:
            return challenges

        challenges['Last run'] = '{} at {}'.format(fdate(self.runs[0]['Run Date']), self.runs[0]['Event'])
        challenges['Current series'] = self.current_series()
        challenges['Parkruns this year'] = self.stats['_YR_' + str(datetime.datetime.now().year)]
        pb = min([t['TimeSecs'] for t in self.runs])
        challenges['Best ever PB'] = str(datetime.timedelta(seconds=pb))
        challenges['Number of PBs'] = self.stats['_PB']

        last_pb_ix = find_in_list_dict(self.runs, 'PB?', 'PB') or 0
        challenges['Last PB'] = '{} at {} ({} runs ago)'.format(
            fdate(self.runs[last_pb_ix]['Run Date']),
            self.runs[last_pb_ix]['Event'],
            last_pb_ix)

        challenges['✳️ Total number of runs'] = self.run_count
        challenges['✳️ Events run'] = len([x for x in self.stats if x.startswith('_EVENT_')])
        challenges['🚩 Milestones'] = self.milestones()
        challenges['📅 Calendar Bingo'] = self.bingo()
        challenges['🔤 Alphabet A-Z'] = self.alphabet()
        challenges['⏱ Stopwatch 00-59'] = self.stopwatch()
        challenges['💯 Position 00-99'] = self.position()
        challenges['💹 Fibonacci series'] = self.num_series('Fibonacci')
        challenges['💹 Primes series'] = self.num_series('Prime')
        challenges['🐮 Cowell Club'] = self.cowell()
        challenges['🔒 Lockdown'] = self.lockdown()
        challenges['✳️ Total distance'] = '{:0,}km'.format(self.run_count * 5)

        key = max({x for x in self.stats if x.startswith('_YR_')}, key=lambda ky: self.stats[ky])

        challenges['✳️ Most parkruns in a year'] = '{} in {}'.format(
            self.stats[key], key.replace('_YR_', ''))
        challenges['🏆 Trophy years'] = self.medal_years()

        times = Counter(x['Time'] for x in self.runs)
        max_freq = max(times.values())
        times_done_max_freq = sorted([x for x in times if times[x] == max_freq])
        challenges['⏱ Most frequent time'] = '{} - {} times'.format(
            ', '.join(times_done_max_freq),
            max_freq
        )
        pos = Counter(x['Pos'] for x in self.runs)
        max_freq = max(pos.values())
        times_done_max_freq = sorted([x for x in pos if pos[x] == max_freq])
        challenges['🔢 Most frequent position'] = '{} - {} times'.format(
            ', '.join(times_done_max_freq),
            max_freq
        )

        key = max({x for x in self.stats if x.startswith('_EVENT_')}, key=lambda ky: self.stats[ky])

        challenges['Most common event'] = '{} at {}'.format(self.stats[key], key.replace('_EVENT_', ''))
        challenges['1️⃣ Singleton events'] = '{}'.format(
            len([x for x in self.stats if x.startswith('_EVENT_') and self.stats[x] == 1])
        )
        challenges['2️⃣ Double events'] = '{}'.format(
            len([x for x in self.stats if x.startswith('_EVENT_') and self.stats[x] == 2])
        )

        pix = 0
        ev = sorted([self.stats[x] for x in self.stats if x.startswith('_EVENT_')], reverse=True)
        for ix, element in enumerate(ev):
            if element > ix:
                pix = ix + 1
            else:
                break
        challenges['ℹ️ p-index'] = pix

        rn = sorted(set([int(x['Run Number']) for x in self.runs]))
        wix = sorted(list(
            set(range(1, max(rn)))
            - set(rn)))[0] - 1
        challenges['ℹ️ Wilson-index'] = wix

        challenges['🎉 Parkrun birthday'] = '{} at {}'.format(
            fdate(self.runs[-1]['Run Date']),
            self.runs[-1]['Event']
        )

        yr = sorted([x.replace('_YR_', '') for x in self.stats if x.startswith('_YR_')])
        challenges['🕯 Years running'] = '{} ({} to {})'.format(len(yr), yr[0], yr[-1])

        challenges['Tourist Quotient'] = '{:0.0%}'.format(
            len([x for x in self.stats if x.startswith('_EVENT_')]) / self.run_count
        )
        streak = 0
        seen = []
        for ele in [x['Event'] for x in self.runs]:
            if ele in seen:
                break
            else:
                streak += 1
                seen.append(ele)

        challenges['Current tourism streak'] = streak
        challenges['Longest tourism streak'] = 'tbc'
        challenges['Total distance travelled'] = 'tbc'

        challenges['🌍 Countries visited'] = '{} ({})'.format(len(self.countries), ', '.join(self.countries))

        for k, v in [('Time', '⏱ Time'), ('AgeGrade', '🎂 Age grading'), ('Pos', '🏅 Position')]:
            element = ['{:>8}'.format(t[k]) for t in self.runs]
            challenges[v + ' (range)'] = '{} --> {}'.format(min(element).strip(), max(element).strip())

        times = [sum(x * int(t) for x, t in zip([60, 1], ele['Time'].split(":"))) for ele in self.runs]
        challenges['⏱ Average run time'] = '{}'.format(datetime.timedelta(seconds=round(statistics.mean(times))))
        challenges['⏱ Total run time'] = '{}'.format(str(datetime.timedelta(seconds=sum(times))))

        challenges['🎄 Christmas Day'] = self.holiday_runs(12, 25)
        challenges['🎊 New Year Day'] = self.holiday_runs(1, 1)

        challenges['🌳 Bushy Pilgrimage'] = fdate(self.regex_test('bushy', 'Run Date', 'single'))

        challenges['🐍 Snake'] = self.ev_pattern_challenge({'^S': 10}, '(Ssssslither around)')
        challenges['🎵 Bee Gees'] = self.ev_pattern_challenge({'^B': 3, '^G': 3}, '(3B & 3G)')
        challenges['🏴‍☠️ Pirates'] = self.ev_pattern_challenge({'^C': 7, '^R': 1}, '(7C & 1R)')
        challenges['🧭 Compass'] = self.ev_pattern_challenge(
            {'north': 1, 'west': 1, 'south': 1, 'east': 1},
            '(Go North, South, East & West)')
        challenges['👤 Full Ponty'] = self.ev_pattern_challenge({'ponty': 4}, '(All the Ponty\'s)')

        return challenges

    def ev_pattern_challenge(self, d, reqt):
        result = {}
        for ele in d:
            result[ele] = self.regex_test(ele, 'Event', 'list').split('~')[0:d[ele]]

        total_met = sum([len(result[x]) for x in result if result[x] != ['-']])
        total_required = sum(d.values())
        events = ', '.join([', '.join(result[x]) for x in result if result[x] != ['-']])
        return '{:0.0%} - {} out of {} {}~{}'.format(
            total_met / total_required,
            total_met,
            total_required,
            reqt,
            events)

    def medal_years(self):
        def get_selected(yrs, label, lower, upper):
            s = sorted(['{} ({})'.format(x[0], x[1]) for x in yrs if (x[1] > lower) and (x[1] < upper)])
            if len(s) > 0:
                s = [label] + s + ['~']

            return s

        years = [(x.replace('_YR_', ''), self.stats[x]) for x in self.stats if x.startswith('_YR_')]
        gold = get_selected(years, '🥇 (50+): ', 49, 99)
        silver = get_selected(years, '🥈 (40+): ', 39, 50)
        bronze = get_selected(years, '🥉 (30+): ', 29, 40)

        if len(gold + silver + bronze) == 0:
            gold = ['No years where 30+ events run']

        return '{}'.format(' '.join(gold + silver + bronze))

    def bingo(self):
        resp = Counter([datetime.datetime.strptime(x['Run Date'], '%d/%m/%Y').strftime('%d-%b') for x in self.runs])
        return '{:0.0%} - {} out of 365 - most common {} ({} times)'.format(
            len(resp) / 365,
            len(resp),
            resp.most_common(1)[0][0],
            resp.most_common(1)[0][1])

    def atoz(self):
      x = {}
      for i in range(65,91):
        x[chr(i)] = []
      for i in self.runs:
        if i['Event'] not in x[i['Event'][0]]: x[i['Event'][0]].append(i['Event'])
        
      return x
    

    def milestones(self):
        resp = ''
        for ms in [10, 25, 50, 100, 250, 300, 350, 400, 450, 500]:
            if ms <= len(self.runs):
                txt = '{} Club on {} at {}~'. \
                    format(ms,
                           fdate(self.runs[-ms]['Run Date']),
                           self.runs[-ms]['Event']
                           )
                resp += txt

        return resp

    def lockdown(self):
        evs = [x['Run Date'] for x in self.runs if x['Run Date'] in ('14/03/2020', '24/07/2021')]
        if len(evs) == 2:
            return 'Last & First'
        elif len(evs) == 1 and evs[0].endswith('2020'):
            return 'Last before lockdown'
        elif len(evs) == 1 and evs[0].endswith('2021'):
            return 'First after lockdown'
        else:
            return '-'

    def num_series(self, name):
        series_dict = {
            'Fibonacci': [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610],
            'Prime': [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
        }
        series = series_dict[name]

        matching = set([int(x['Run Number']) for x in self.runs if int(x['Run Number']) in series])
        missing = set(series) - set(matching)

        if len(series) == len(matching):
            return '100% - (first {} numbers of {} series)'.format(len(series), name)
        else:
            return '{:0.0%} - missing {} out of {}~Missing: {}'.format(
                len(matching) / len(series),
                len(missing),
                len(series),
                ', '.join([str(x) for x in sorted(missing)])
            )

    def alphabet(self):
        # alphabet (discounts X, so only 25 letters)
        event_counter = self.count_by()
        missing = {x.upper() for x in event_counter if event_counter[x] == 0 and x != 'x'}
        if len(missing) == 0:
            return '100% - All letters (except X)'
        else:
            return '{:0.0%} - {} letters (missing {})'.format(
                (25 - len(missing)) / 25,
                25 - len(missing),
                ', '.join(sorted(missing))
            )

    def stopwatch(self):
        k = len({x for x in self.stats if self.stats[x] != 0 and x.startswith('_SEC_')})
        if k == 60:
            return '100% - All seconds ticked off'
        else:
            return '{:0.0%} - {} out of 60~Missing: {}'.format(
                k / 60,
                k,
                ', '.join(sorted(
                    {x.replace('_SEC_', '') for x in self.stats if self.stats[x] == 0 and x.startswith('_SEC_')}))
            )

    def position(self):
        k = len({x for x in self.stats if self.stats[x] != 0 and x.startswith('_POS_')})
        if k == 100:
            return '100% - All positions 00 to 99 completed'
        else:
            return '{:0.0%} - {} out of 100~Missing: {}'.format(
                k / 100,
                k,
                ', '.join(sorted(
                    {x.replace('_POS_', '') for x in self.stats if self.stats[x] == 0 and x.startswith('_POS_')}))
            )

    def cowell(self):
        levels = {0: '-', 1: 'Quarter', 2: 'Half', 3: 'Three quarter'}

        evs = len([x for x in self.stats if x.startswith('_EVENT_')])

        if evs > 99:
            return 'Full'
        else:
            return levels[math.floor(evs / 25)]

    def regex_test(self, pattern, attribute, return_type):
        lst = sorted(set([x[attribute] for x in self.runs if re.search(pattern, x['Event'], re.IGNORECASE)]))
        if return_type == 'single':
            return lst[0] if len(lst) > 0 else '-'
        else:
            return '~'.join(lst) if len(lst) > 0 else '-'

    def run_gen(self):
        ix = -1

        while True:
            ix += 1
            yield self.runs[ix]

    def convert_date(self, date_string, to_format='%d/%m/%Y'):
        return datetime.datetime.strptime(date_string, to_format)

    def current_series(self):
        try:
            diff = 0
            num_runs = 0
            seq = self.run_gen()
            first_run = next(seq)
            current_run = first_run
            current_dt = self.convert_date(current_run['Run Date'])
            prev_dt = current_dt

            while diff < 8:
                num_runs += 1
                prev_run = next(seq)
                prev_dt = self.convert_date(prev_run['Run Date'])
                diff = (current_dt - prev_dt).days
                if diff < 8:
                    current_run = prev_run
                    current_dt = prev_dt

            if num_runs == 1:
                return '{} - {} at {}'.format(
                    num_runs,
                    datetime.datetime.strftime(prev_dt + datetime.timedelta(days=diff), '%d-%b-%Y'),
                    first_run['Event']
                )
            else:
                return '{}~From: {} at {} to {} at {}'.format(
                    num_runs,
                    datetime.datetime.strftime(prev_dt + datetime.timedelta(days=diff), '%d-%b-%Y'),
                    current_run['Event'],
                    fdate(self.runs[0]['Run Date']),
                    self.runs[0]['Event']
                )
        except Exception:
            return 'Unavailable'

    def __str__(self):
        return 'Runner: {} | {} | {} | {} | {}'.format(
            self.rid,
            self.name,
            len(self.runs),
            self.cached or '-',
            self.updated_dt
        )

    def __repr__(self):
        return self.__str__()

    def get_stats(self):
        stats = Counter({'_SEC_{:02}'.format(s): 0 for s in range(60)})
        stats.update({'_POS_{:02}'.format(s): 0 for s in range(100)})
        stats.update('_SEC_' + t['Time'][-2:] for t in self.runs)
        stats.update('_PB' for t in self.runs if t['PB?'] != '')
        stats.update('_YR_' + t['Run Date'][-4:] for t in self.runs)
        stats.update('_EVENT_' + t['Event'] for t in self.runs)
        stats.update('_POS_' + t['Pos'][-2:].zfill(2) for t in self.runs)
        return stats

    def count_by(self):
        counter = Counter({letter: 0 for letter in string.ascii_lowercase})
        counter.update(t['Event'][0].lower() for t in self.runs)
        return counter


# -----------
# helpers
# -----------
def get(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"
    }

    session = requests.Session()
    session.headers.update(headers)
    return session.get(url)


def get_file_details(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def fdate(src, src_format='%d/%m/%Y', target_format='%d-%b-%Y'):
    try:
        return datetime.datetime.strptime(src, src_format).strftime(target_format)
    except Exception:
        return src


def load_runners():
    runners_lst = [184594, 4327482, 2564629, 541276, 33202, 3158074, 185368, 23656, 40489, 5404801, 69260]
    runners = []
    for r in runners_lst:
        o = Runner(r)
        o.get_runs(refresh=True)
        runners.append(o)
        print(o)


# -----------
# MAIN
# -----------
if __name__ == '__main__':
    load_runners()
