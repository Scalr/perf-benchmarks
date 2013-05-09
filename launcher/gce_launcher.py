
import time
import telnetlib

import subprocess as subps

number_of_inst = 100 

f = open('gce1', 'a+')


def run_inst(name):
    
    start_time = time.time()

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'addinstance',
                 '%s' % name,
                 '--machine_type=n1-standard-1',
                 '--zone=us-central1-a',
                 '--image=https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'], stdout=subps.PIPE, stderr=subps.PIPE)

    print p.stderr.read()
    #print p.stdout.read()

    #p.terminate()

    print (time.time() - start_time)

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'getinstance',
                 '%s' % name], stdout=subps.PIPE, stderr=subps.PIPE)

    out = p.stdout.read()

    #p.terminate()

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
            except:
                pass

        end_time = time.time()

        inst_time = end_time - start_time

        print '%s\t%s' % (i, inst_time)

        f.write('%i\t%s\n' % (start_time, inst_time))
        f.flush()
    else:
        print 'WARNING IP'

    p = subps.Popen(['gcutil-1.7.2/gcutil',
                 '--project=scalr.com:scalr-labs',
                 'deleteinstance',
                 '%s' % name], stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)

    p.communicate(input='yes')

    #p.terminate()

    #print ppp.stderr.read()
    #print ppp.stdout.read()


for i in range(number_of_inst):

    run_inst('roma-test-%sa' % i)

