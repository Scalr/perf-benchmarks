
import re
import random
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='file to parse')
    args = parser.parse_args()

    fo = open('%s.csv' % args.file, 'w+')
    fi = open(args.file, 'r')
    content = fi.read()
    fi.close()

    '''
    tests = {
        'name':{
                'date':date,
                'time':time,
                'rw':rw,
                'size':size,
                'bs':bs,
                'depth':depth
            },    
        }
    '''

    tests = {}
    
    for line in content.split('\n'):

        if line.startswith('#'):
            dt = line[1:].strip()
            continue

        p = re.compile(r'^\[global\]$')
        if p.match(line):
            continue

        p = re.compile(r'^\[.*\]$')
        if p.match(line):
            name = '%s-%s' % (line[1:-1], random.randint(100, 999))
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

        p = re.compile(r'.*[,]+[ ]iops[ ]*=[ ]*[1-9]+')
        if p.match(line):
            tests[name].update({'iops':int(line.split(':')[1].split(',')[2].split('=')[1].strip())})
            continue

        p = re.compile(r'[ ]*lat[ ]*\([a-z]sec\)[ ]*.*avg[ ]*=[ ]*[0-9]')
        if p.match(line):
            factors = {'usec':1000000.0, 'msec':1000.0}
            prefix = line.split(':')[0].split()[1].strip()[1:-1]
            prefix_factor = factors[prefix] / 1000.0

            value = line.split(':')[1].split(',')[0].split('=')[1].strip()
            if value.endswith('K'):
                value = value[0:-1]
                tests[name].update({'lat_min':float(value) / prefix_factor * 1000})
            tests[name].update({'lat_min':float(value) / prefix_factor})

            value = line.split(':')[1].split(',')[1].split('=')[1].strip()
            if value.endswith('K'):
                value = value[0:-1]
                tests[name].update({'lat_max':float(value) / prefix_factor * 1000})
            tests[name].update({'lat_max':float(value) / prefix_factor})

            value = line.split(':')[1].split(',')[2].split('=')[1].strip()
            if value.endswith('K'):
                value = value[0:-1]
                tests[name].update({'lat_avg':float(value) / prefix_factor * 1000})
            tests[name].update({'lat_avg':float(value) / prefix_factor})
            continue
        p = re.compile(r'.*[,]+[ ]*aggrb[ ]*=[ ]*[1-9]+')
        if p.match(line):
            tests[name].update({'aggrb':int(line.split(':')[1].split(',')[1].split('=')[1].strip()[:-4])})
            continue

    class Table(dict):

        def __init__(self, name):
            self.name = name

    iops_table = Table('iops')
    aggrb_table = Table('aggrb, KB/s')
    lat_avg_table = Table('lat average, msec')

    tables = [iops_table, aggrb_table, lat_avg_table]

    for test, data in tests.iteritems():

        iops_table.setdefault(data['rw'], {}).setdefault(data['bs'], {})[data['depth']] = data['iops']
        aggrb_table.setdefault(data['rw'], {}).setdefault(data['bs'], {})[data['depth']] = data['aggrb']
        lat_avg_table.setdefault(data['rw'], {}).setdefault(data['bs'], {})[data['depth']] = data['lat_avg']

    for table in tables:

        for rw, rw_table in table.iteritems():

            rows = []
            for v in rw_table.values():
                for k in v.keys():
                    if k not in rows:
                        rows.append(k)

            rows = sorted(rows)
            cols = sorted(rw_table.keys())

            fo.write('[%s %s]\n' % (rw, table.name))
            fo.write(';%s' % ';'.join(map(lambda el: 'Depth %s' % el, rows)))
            fo.write('\n')

            for bs in cols:
                row = []
                for depth in rows:
                    try:
                        row.append('%s' % str(rw_table[bs][depth]).replace('.', ','))
                    except KeyError:
                        row.append(' ')
                fo.write('%sk;%s\n' % (bs, ';'.join(row)))
            fo.flush()

    fo.close()

    print 'Done'
