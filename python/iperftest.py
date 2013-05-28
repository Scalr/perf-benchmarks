
import os
import time
import json
import argparse
import datetime

import subprocess as subps


class IPerfTimeout(Exception):
    pass


class IPerfError(Exception):
    pass

utcnow = datetime.datetime.utcnow()
time_str = utcnow.strftime('%d:%m:%Y %H:%M') 

def iperf_test(ip, user, ssh_key, threads, work_time=10):

    report = {'datetime':time_str}

    try:

        iperf_sh = '\
#!/bin/bash\n\
sudo killall -9 iperf &>/dev/null\n\
find . -name "iperf.*" -exec rm {} \;\n\
iperf -s -p 1234 1>/dev/null 2>iperf.err\n'

        cmd = ["ssh", "%s@%s" % (user, ip), "echo '%s' >/tmp/iperf.sh" % iperf_sh] 
        if subps.call(cmd, stderr=file('iperf.err', 'w')):
            raise IPerfError()

        cmd = ["ssh", "%s@%s" % (user, ip), "screen -m -d bash /tmp/iperf.sh"] 
        if subps.call(cmd, stderr=file('iperf.err', 'w')):
            raise IPerfError()

        for i in range(3):
            cmd = ["ssh", "%s@%s" % (user, ip), "ps aux | grep -v grep | grep 'iperf -s -p 1234'"] 
            try:
                out = subps.check_output(cmd, stderr=file('iperf.err', 'w'))
            except subps.CalledProcessError:
                continue
            if out:
                break
            else:
                time.sleep(2)
        else:
            cmd = ["ssh", "%s@%s" % (user, ip), "'cat iperf.err'"] 
            error = subps.check_output(cmd, stderr=file('iperf.err', 'w'))
            raise IPerfError(error)

        iperf_sh = '\
#!/bin/bash\n\
IP=$1\n\
P=$2\n\
T=$3\n\
sudo killall -9 iperf &>/dev/null\n\
find . -name "iperf.*" -exec rm {} \;\n\
iperf -c $IP -p 1234 -P $P -t $T -f m 2>iperf.err | grep "Mbits/sec" &>iperf.data\n'

        with open('/tmp/iperf.sh', 'w') as f:
            f.write(iperf_sh)

        speed = {}

        print threads
        for p in threads:
            cmd = "screen -m -d /bin/bash /tmp/iperf.sh %s %s %s" % (ip, p, work_time)
            if subps.call(cmd.split(), stderr=file('iperf.err', 'w')):
                raise IPerfError()

            time.sleep(work_time + 1)

            for _ in range(5):
                if os.path.exists("iperf.data") and os.path.getsize("iperf.data") > 0:
                    with open("iperf.data", 'r') as f:
                        data = f.read()

                    print data
                    if '[SUM]' not in data:
                        for line in data.split('\n'):
                            if 'Mbits/sec' in line:
                                speed[p] = line.split()[-2]
                    else:
                        for line in data.split('\n'):
                            if '[SUM]' in line:
                                speed[p] = line.split()[-2]
                    report.setdefault('speed', {})[p] = speed[p] 
                    break
                time.sleep(2)
            else:
                raise IPerfTimeout('timeout')

        if os.path.exists("iperf.err") and os.path.getsize("iperf.err") > 0:
            raise IPerfError()

    except Exception, e:
        with open("iperf.err", 'r') as f:
            report.update({'error':'%s;%s;%s' % (e.__class__.__name__, e, f.read())})

    finally:
        with open('iperf.report', 'w') as f:
            f.write(json.dumps(report))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--ip', default=None, help='ip address')
    parser.add_argument('-u', '--user', default=None, help='user')
    parser.add_argument('-k', '--key', default=None, help='ssh key')
    parser.add_argument('-p', '--threads', nargs='+', type=int, default=1, help='threads list')
    parser.add_argument('-t', '--worktime', default=10, type=int, help='working time')

    args = parser.parse_args()

    iperf_test(args.ip, args.user, args.key, args.threads, args.worktime)
        
