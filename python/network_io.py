
import os
import scp
import time
import json
import paramiko
import telnetlib
import traceback

import ec2
import gce

import util


def netrwork_io_test(itype1, image1, region1, itype2, image2, region2, filesize='64M', iteration=1, timeout=600): 
    
    if itype1 in ec2.ec2_instance_types:
        inst1 = ec2.EC2Inst(itype1, image1, region1, 'ubuntu', '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region1),
                            'perf-bench-%s' % region1)
    if itype1 in gce.gce_instance_types:
        inst1 = gce.GCEInst(itype1, image1, region1, os.environ['USER'], '%s/.ssh/google_compute_engine' % os.environ['HOME'])

    if itype2 in ec2.ec2_instance_types:
        inst2 = ec2.EC2Inst(itype2, image2, region2, 'ubuntu', '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region2),
                            'perf-bench-%s' % region2)
    if itype2 in gce.gce_instance_types:
        inst2 = gce.GCEInst(itype2, image2, region2, os.environ['USER'], '%s/.ssh/google_compute_engine' % os.environ['HOME'])

    inst1.launch()
    inst2.launch()

    try:

        print '[IP] waiting'
        for i in range(150):
            inst1.update()
            inst2.update()
            if inst1.remote_ip != None and inst2.remote_ip != None:
                print '[IP] ok'
                break
            time.sleep(2)
        
        print '[SSH] waiting'
        for i in range(120):
            try:
                telnetlib.Telnet(inst1.remote_ip, 22, 1)
                telnetlib.Telnet(inst2.remote_ip, 22, 1)
                print '[SSH] ok'
                break
            except:
                time.sleep(2)
        
        print '[UP] %s | %s | %s' % (inst1.itype, inst1.region, inst1.remote_ip)
        print '[UP] %s | %s | %s' % (inst2.itype, inst2.region, inst2.remote_ip)

        util.instances_prepare([inst1, inst2], ['iperf', 'screen'])

        ssh_cli = paramiko.SSHClient()
        ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_cli.connect(inst1.remote_ip, username=inst1.user, key_filename=inst1.ssh_key)
        scp_cli = scp.SCPClient(ssh_cli.get_transport())
        scp_cli.put('netcattest.py', '/tmp/netcattest.py')
        scp_cli.put('scptest.py', '/tmp/scptest.py')
        scp_cli.put('iperftest.py', '/tmp/iperftest.py')

        print '[START TESTS] %s %s <-----> %s %s'\
                % (inst1.itype, inst1.region, inst2.itype, inst2.region)

        for i in range(iteration):

            print '[START ITERATION %s]' % i

            print '[START] netcat'
            stdin, stdout, stderr = ssh_cli.exec_command('python /tmp/netcattest.py -i %s -u %s -k %s -s %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, filesize, timeout))
            for _ in range(timeout / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f netcat.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat netcat.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype})
                    report.update({'inst2':inst2.itype})
                    report.update({'region1':inst1.region})
                    report.update({'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud})
                    report.update({'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/netcat')
                    if not os.path.exists(report_path):
                        os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['time']
                    break
                else:
                    time.sleep(5)
            print '[END] netcat'

            print '[START] scp'
            stdin, stdout, stderr = ssh_cli.exec_command('python /tmp/scptest.py -i %s -u %s -k %s -s %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, filesize, timeout))
            for _ in range(timeout / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f scp.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat scp.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype})
                    report.update({'inst2':inst2.itype})
                    report.update({'region1':inst1.region})
                    report.update({'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud})
                    report.update({'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/scp')
                    if not os.path.exists(report_path):
                        os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['time']
                    break
                else:
                    time.sleep(5)
            print '[END] scp'

            print '[START] iperf'
            threads = [1, 4] 
            work_time = 5
            stdin, stdout, stderr = ssh_cli.exec_command('python /tmp/iperftest.py -i %s -u %s -k %s -p %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, ' '.join(map(str, threads)), work_time))
            for _ in range(len(threads) * (work_time + 10) / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f iperf.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat iperf.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype})
                    report.update({'inst2':inst2.itype})
                    report.update({'region1':inst1.region})
                    report.update({'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud})
                    report.update({'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/iperf')
                    if not os.path.exists(report_path):
                        os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['speed']
                    break
                else:
                    time.sleep(5)
            print '[END] iperf'

    except Exception:

        print '[EXCEPTION] %s\n' % traceback.print_exc()

    finally:

        ssh_cli.close()

        inst1.terminate()
        inst2.terminate()

