
import os
import time
import json
import argparse
import datetime

import subprocess as subps


class SCPError(Exception):
    pass


class SCPTimeout(Exception):
    pass

utcnow = datetime.datetime.utcnow()
time_str = utcnow.strftime('%d:%m:%Y %H:%M') 

def scp_test(ip, user, ssh_key, filesize='64M', timeout=300):

    report = {'datetime':time_str}

    try:

        scp_sh = '\
#!/bin/bash\n\
sudo killall -9 scp &>/dev/null\n\
find . -name "scp.*" -exec rm {} \;\n\
/usr/bin/time -f "%%e" -o scp.time head -c %s /dev/zero 2>>scp.err | ssh %s@%s "cat>/dev/null" 2>>scp.err\n'\
            % (filesize, user, ip)

        with open('/tmp/scp.sh', 'w') as fo:
            fo.write(scp_sh)

        cmd = "screen -m -d /bin/bash /tmp/scp.sh"
        if subps.call(cmd.split(), stderr=file('scp.err', 'w')):
            raise SCPError()

        time.sleep(1)

        for _ in range(timeout / 2):
            if os.path.exists("scp.time") and os.path.getsize("scp.time") > 0:
                with open("scp.time", 'r') as f:
                    data = float(f.read().strip())
                    report.update({'size':filesize})
                    report.update({'time':data})
                break
            time.sleep(2)
        else:
            raise SCPTimeout('timeout %s' % timeout)

        if os.path.exists("scp.err") and os.path.getsize("scp.err") > 0:
            raise SCPError()

    except Exception, e:
        with open("iperf.err", 'r') as f:
            report.update({'error':'%s;%s;%s' % (e.__class__.__name__, e, f.read())})

    finally:
        with open('scp.report', 'w') as f:
            f.write(json.dumps(report))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--ip', default=None, help='ip address')
    parser.add_argument('-u', '--user', default=None, help='user')
    parser.add_argument('-k', '--key', default=None, help='ssh key')
    parser.add_argument('-s', '--size', default=None, help='file size')
    parser.add_argument('-t', '--timeout', default=60, type=int, help='timeout')

    args = parser.parse_args()

    scp_test(args.ip, args.user, args.key, args.size, args.timeout)
        
