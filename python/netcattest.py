
import os
import time
import json
import argparse
import datetime

import subprocess as subps


class NetCatTimeout(Exception):
    pass


class NetCatError(Exception):
    pass

utcnow = datetime.datetime.utcnow()
time_str = utcnow.strftime('%d:%m:%Y %H:%M') 

def netcat_test(ip, user, ssh_key, filesize='64M', timeout=300):
    
    report = {'datetime':time_str}

    try:

        netcat_sh = '\
#!/bin/bash\n\
sudo killall -9 nc &>/dev/null\n\
find . -name "netcat.*" -exec rm {} \;\n\
nc -l 7777 >/dev/null 2>>netcat.err\n'

        cmd = ["ssh", "%s@%s" % (user, ip), "echo '%s' >/tmp/netcat.sh" % netcat_sh] 
        if subps.call(cmd, stderr=file('netcat.err', 'w')):
            raise NetCatError()

        cmd = ["ssh", "%s@%s" % (user, ip), "screen -m -d bash /tmp/netcat.sh"] 
        if subps.call(cmd, stderr=file('netcat.err', 'w')):
            raise NetCatError()

        for i in range(3):
            cmd = ["ssh", "%s@%s" % (user, ip), "ps aux | grep -v grep | grep 'nc -l 7777'"] 
            try:
                out = subps.check_output(cmd, stderr=file('netcat.err', 'w'))
            except subps.CalledProcessError:
                continue
            if out:
                break
            else:
                time.sleep(2)
        else:
            cmd = ["ssh", "%s@%s" % (user, ip), "cat netcat.err'"] 
            error = subps.check_output(cmd, stderr=file('netcat.err', 'w'))
            raise NetCatError(error)

        netcat_sh = '\
#!/bin/bash\n\
sudo killall -9 nc &>/dev/null\n\
find . -name "netcat.*" -exec rm {} \;\n\
/usr/bin/time -f "%%e" -o netcat.time head -c %sM /dev/zero 2>>netcat.err | nc %s 7777 2>>netcat.err\n' % (filesize, ip)

        with open('/tmp/netcat.sh', 'w') as fo:
            fo.write(netcat_sh)

        cmd = "screen -m -d /bin/bash /tmp/netcat.sh"
        if subps.call(cmd.split(), stderr=file('netcat.err', 'w')):
            raise NetCatError()

        time.sleep(1)

        for _ in range(timeout / 2):
            if os.path.exists("netcat.time") and os.path.getsize("netcat.time") > 0:
                with open("netcat.time", 'r') as f:
                    data = float(f.read().strip())
                    report.update({'size':filesize})
                    report.update({'time':data})
                break
            time.sleep(2)
        else:
            raise NetCatTimeout('timeout %s' % timeout)

        if os.path.exists("netcat.err") and os.path.getsize("netcat.err") > 0:
            raise NetCatError()

    except Exception, e:
        with open("iperf.err", 'r') as f:
            report.update({'error':'%s;%s;%s' % (e.__class__.__name__, e, f.read())})

    finally:
        with open('netcat.report', 'w') as f:
            f.write(json.dumps(report))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--ip', default=None, help='ip address')
    parser.add_argument('-u', '--user', default=None, help='user')
    parser.add_argument('-k', '--key', default=None, help='ssh key')
    parser.add_argument('-s', '--size', type=int, default=64, help='file size in MB')
    parser.add_argument('-t', '--timeout', default=None, type=int, help='timeout')

    args = parser.parse_args()

    netcat_test(args.ip, args.user, args.key, args.size, args.timeout)
        
