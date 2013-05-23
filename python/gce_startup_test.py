
import time
import argparse
import datetime
import telnetlib

import subprocess as subps


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--number', type=int, default=1, help='number of instances for start')
    parser.add_argument('-i', '--interval', default=60, type=int, help='interval between starts')

    args = parser.parse_args()

    for i in range(args.number):
        start_time = time.time()
        utcnow = datetime.datetime.utcnow()
        time_str = utcnow.strftime('%d:%m:%Y;%H:%M:S') 

        p = subps.Popen(['gcutil',
                     '--project=scalr.com:scalr-labs',
                     'addinstance',
                     'launching-time-test',
                     '--machine_type=n1-standard-1',
                     '--zone=us-central1-a',
                     '--image=https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'],
                     stdout=subps.PIPE, stderr=subps.PIPE)

        print p.stderr.read()
        print p.stdout.read()

        p = subps.Popen(['gcutil',
                     '--project=scalr.com:scalr-labs',
                     'getinstance',
                     'launching-time-test'], stdout=subps.PIPE, stderr=subps.PIPE)

        out = p.stdout.read()

        ip = None

        for line in out.split('\n'):
            if 'external-ip' in line:
                ip = line.split('|')[2].strip()

        if ip:
            while True:
                try:
                    telnetlib.Telnet(ip, 22, 1)
                    break
                except Exception:
                    pass

            end_time = time.time()

            instance_time = end_time - start_time

            with open('gce.csv', 'a+') as f:
                f.write('%s;%s\n' % (time_str, instance_time))

            print '%s;%s' % (time_str, instance_time)

        else:
            print 'WARNING IP'

        p = subps.Popen(['gcutil',
                     '--project=scalr.com:scalr-labs',
                     'deleteinstance',
                     'launching-time-test'], stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)

        p.communicate(input='yes')
        print p.stderr.read()
        print p.stdout.read()

