
import re
import json
import argparse


def parse(data):

    tests = {}

    for test in data:

        for line in test['config'].split('\n'):

            p = re.compile(r'^\[global\]$')
            if p.match(line):
                continue

            p = re.compile(r'^\[.*\]$')
            if p.match(line):
                name = '%s' % line[1:-1]
                tests.update({name:{}})
                continue

            if line.startswith('rw='):
                tests[name].update({'rw':line.split('=')[1]})
                continue

            if line.startswith('bs='):
                if line.strip().endswith('k') or line.strip().endswith('K'):
                    tests[name].update({'bs':int(line.split('=')[1][0:-1])})
                if line.strip().endswith('m') or line.strip().endswith('M'):
                    tests[name].update({'bs':int(line.split('=')[1][0:-1]) * 1024})
                continue

            if line.startswith('iodepth='):
                tests[name].update({'depth':int(line.split('=')[1])})
                continue

        for line in test['data'].split('\n'):

            p = re.compile(r'^[ ]*read[ ]*:', re.IGNORECASE)
            if p.match(line):
                mode = 'read'
                tests[name].setdefault(mode, {})

            p = re.compile(r'^[ ]*write[ ]*:', re.IGNORECASE)
            if p.match(line):
                mode = 'write'
                tests[name].setdefault(mode, {})

            p = re.compile(r'.*[ ]*bw[ ]*=[ ]*[0-9\.]+KB/s')
            if p.match(line):
                tests[name][mode].update({'bw':float(line.split(':')[1].split(',')[1].split('=')[1].strip()[0:-4])})

            p = re.compile(r'.*[ ]*bw[ ]*=[ ]*[0-9\.]+MB/s')
            if p.match(line):
                tests[name][mode].update({'bw':float(line.split(':')[1].split(',')[1].split('=')[1].strip()[0:-4]) * 1024})

            p = re.compile(r'.*[ ]*iops[ ]*=[ ]*[0-9]+')
            if p.match(line):
                tests[name][mode].update({'iops':int(line.split(':')[1].split(',')[2].split('=')[1].strip())})

            for lat in ['clat', 'slat', 'lat']:
                for i, type_ in enumerate(['min', 'max', 'avg']):
                    p = re.compile(r'[ ]*%s[ ]*\([a-z]sec\)[ ]*.*%s[ ]*=[ ]*[0-9]' % (lat, type_))
                    if p.match(line):
                        tests[name][mode].setdefault('%s/%s' % (lat, type_), {})

                        factors = {'usec':1000000.0, 'msec':1000.0}
                        prefix = line.split(':')[0].split()[1].strip()[1:-1]
                        prefix_factor = factors[prefix] / 1000.0

                        value = line.split(':')[1].split(',')[i].split('=')[1].strip()
                        if value.endswith('K'):
                            value = value[0:-1]
                            tests[name][mode]['%s/%s' % (lat, type_)] = float(value) / prefix_factor * 10000
                        tests[name][mode]['%s/%s' % (lat, type_)] = float(value) / prefix_factor

            for i, type_ in enumerate(['aggrb', 'minb', 'maxb']):
                p = re.compile(r'[ ]*READ[ ]*:+.*%s[ ]*=[ ]*[0-9]+' % type_)
                if p.match(line):
                    tests[name]['read'].update({'%s' % type_:int(line.split(':')[1].split(',')[i+1].split('=')[1].strip()[:-4])})

                p = re.compile(r'[ ]*WRITE[ ]*:+.*%s[ ]*=[ ]*[0-9]+' % type_)
                if p.match(line):
                    tests[name]['write'].update({'%s' % type_:int(line.split(':')[1].split(',')[i+1].split('=')[1].strip()[:-4])})

    class Table(dict):

        def __init__(self, name):
            self.name = name

    tables = [Table('iops'), Table('bw'), Table('lat/avg'), Table('aggrb')]

    for test_name, test_data in tests.iteritems():
        for mode, mode_data in test_data.iteritems():
            if mode not in ['read', 'write']:
                continue
            for table in tables:
                if table.name in mode_data.keys():
                    table.setdefault(test_data['rw'], {}).setdefault(test_data['bs'], {})[test_data['depth']] = mode_data[table.name]
    
    out = ''

    for table in tables:
        for mode, mode_data in table.iteritems():

            rows = []
            for v in mode_data.values():
                for k in v.keys():
                    if k not in rows:
                        rows.append(k)

            rows = sorted(rows)
            cols = sorted(mode_data.keys())

            out += '[%s %s]\n' % (mode, table.name)
            out += ';%s\n' % ';'.join(map(lambda el: 'Depth %s' % el, rows))

            for bs in cols:
                row = []
                for depth in rows:
                    try:
                        row.append('%s' % str(mode_data[bs][depth]).replace('.', ','))
                    except KeyError:
                        row.append(' ')
                out += '%sk;%s\n' % (bs, ';'.join(row))

    return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('-f', '--file', help="file")

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        raw = f.read()
        data = json.loads(raw)
        print parse(data)

