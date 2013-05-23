
import telnetlib

from time import time

import subprocess as subps

number_of_instances = 300 

f = open('gce.csv', 'a+')

for i in range(number_of_instances):
    
    start_time = time.time()

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'addinstance',
                 'launching-time-test',
                 '--machine_type=n1-standard-1',
                 '--zone=us-central1-a',
                 '--image=https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'],
                 stdout=subps.PIPE, stderr=subps.PIPE)

    print p.stderr.read()
    print p.stdout.read()

    print (time() - start_time)

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'getinstance',
                 'launching-time-test'], stdout=subps.PIPE, stderr=subps.PIPE)

    out = p.stdout.read()

    ip = None

    for line in out.split('\n'):
        if 'external-ip' in line:
            ip = line.split('|')[2].strip()

    if ip:
        print 'try ssh %s' % ip
        while True:
            try:
                telnetlib.Telnet(ip, 22, 1)
                print 'ssh ok'
                break
            except Exception:
                pass

        end_time = time()

        instance_time = end_time - start_time

        print '%s\t%s' % (i, instance_time)

        f.write('%i;%s\n' % (start_time, instance_time))
        f.flush()
    else:
        print 'WARNING IP'

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'deleteinstance',
                 'launching-time-test'], stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)

    p.communicate(input='yes')
    print p.stderr.read()
    print p.stdout.read()

