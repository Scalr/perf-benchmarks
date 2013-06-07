
import json
import argparse
import datetime

import subprocess as subps


class FIOError(Exception):
    pass


class FIOTimeout(Exception):
    pass

def fio_test(filename, filesize, mode, bs, depth, runtime):

    try:

        report = []

        for m in mode:
            for b in bs:
                for d in depth:

                    cmd = 'python2.7 /tmp/fio_conf_generator.py -n %s-%s-%s -f %s -s %sM -m %s -b %sK -d %s -t %s -o /tmp/fio.conf'\
                            % (m, b, d, filename, filesize, m, b, d, runtime)
                    if subps.call(cmd.split(), stderr=file('fio.err', 'w')):
                        raise FIOError()

                    utcnow = datetime.datetime.utcnow()
                    time_str = utcnow.strftime('%d:%m:%Y %H:%M:%S') 

                    with open('/tmp/fio.conf', 'r') as f:
                        config = f.read()
                    cmd = 'sudo fio --timeout=%s /tmp/fio.conf' % (runtime + 20)
                    try:
                        out = subps.check_output(cmd, stderr=file('fio.err', 'w'), shell=True)
                        report.append({'datetime':time_str, 'config':config, 'data':out})
                    except Exception, e:
                        with open('fio.err', 'r') as f:
                            report.append({'datetime':time_str, 'config':config, 'error':'%s;%s' % (str(e), f.read())})

    except Exception, e:
        with open('fio.err', 'r') as f:
            report.append({'error':'%s;%s;%s' % (e.__class__.__name__, e, f.read())})

    finally:
        with open('fio.report', 'w') as f:
            f.write(json.dumps(report, indent=4, sort_keys=True))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', default='/tmp/fio.file', help='file or device')
    parser.add_argument('-s', '--size', default=128, type=int, help='filesize in MB')
    parser.add_argument('-m', '--mode', nargs='+', type=str, default=['randrw'], help='mode <read|write|randread|randwrite|randrw>')
    parser.add_argument('-b', '--bs', nargs='+', type=int, default=1, help='block size in KB')
    parser.add_argument('-d', '--depth', nargs='+', type=int, default=1, help='iodepth')
    parser.add_argument('-t', '--runtime', type=int, default=None, help='runtime')

    args = parser.parse_args()

    fio_test(args.file, args.size, args.mode, args.bs, args.depth, args.runtime)
        
