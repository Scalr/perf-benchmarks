
import os
import scp
import time
import json
import argparse
import paramiko
import telnetlib
import traceback

import subprocess as subps

import ec2
import gce

import util


def network_io_test(itype1, image1, region1, itype2, image2, region2, filesize=64, iteration=1, timeout=600): 
    
    ssh_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.ssh/')

    if itype1 in ec2.ec2_instance_types:
        inst1 = ec2.EC2Inst(itype1, image1, region1, 'ubuntu', '%s/perf-bench-%s.pem'\
                            % (ssh_path, region1), 'perf-bench-%s' % region1)
    if itype1 in gce.gce_instance_types:
        inst1 = gce.GCEInst(itype1, image1, region1, os.environ['USER'], '%s/google_compute_engine' % ssh_path)

    if itype2 in ec2.ec2_instance_types:
        inst2 = ec2.EC2Inst(itype2, image2, region2, 'ubuntu', '%s/perf-bench-%s.pem'\
                            % (ssh_path, region2), 'perf-bench-%s' % region2)
    if itype2 in gce.gce_instance_types:
        inst2 = gce.GCEInst(itype2, image2, region2, os.environ['USER'], '%s/google_compute_engine' % ssh_path)

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
            stdin, stdout, stderr = ssh_cli.exec_command('python2.7 /tmp/netcattest.py -i %s -u %s -k %s -s %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, filesize, timeout))
            time.sleep(10)
            for _ in range(timeout / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f netcat.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat netcat.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype, 'inst2':inst2.itype})
                    report.update({'region1':inst1.region, 'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud, 'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/netcat')
                    if not os.path.exists(report_path):
                        cmd = 'mkdir -p %s' % report_path
                        subps.call(cmd.split())
                        #os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['time']
                    break
                else:
                    time.sleep(5)
            print '[END] netcat'

            print '[START] scp'
            stdin, stdout, stderr = ssh_cli.exec_command('python2.7 /tmp/scptest.py -i %s -u %s -k %s -s %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, filesize, timeout))
            time.sleep(10)
            for _ in range(timeout / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f scp.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat scp.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype, 'inst2':inst2.itype})
                    report.update({'region1':inst1.region, 'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud, 'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/scp')
                    if not os.path.exists(report_path):
                        cmd = 'mkdir -p %s' % report_path
                        subps.call(cmd.split())
                        #os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['time']
                    break
                else:
                    time.sleep(5)
            print '[END] scp'

            print '[START] iperf'
            threads = [1, 4, 8] 
            work_time = 5
            stdin, stdout, stderr = ssh_cli.exec_command('python2.7 /tmp/iperftest.py -i %s -u %s -k %s -p %s -t %s'
                                 % (inst2.remote_ip, inst2.user, inst2.ssh_key, ' '.join(map(str, threads)), work_time))
            time.sleep(10)
            for _ in range(len(threads) * (work_time + 10) / 5 + 1):
                stdin, stdout, stderr = ssh_cli.exec_command('[ -f iperf.report ]; echo $?')
                out = stdout.read()
                if out.strip() == '0':
                    stdin, stdout, stderr = ssh_cli.exec_command('cat iperf.report')
                    out = stdout.read()
                    report = json.loads(out)
                    report.update({'inst1':inst1.itype, 'inst2':inst2.itype})
                    report.update({'region1':inst1.region, 'region2':inst2.region})
                    report.update({'cloud1':inst1.cloud, 'cloud2':inst2.cloud})
                    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/network-io/iperf')
                    if not os.path.exists(report_path):
                        cmd = 'mkdir -p %s' % report_path
                        subps.call(cmd.split())
                        #os.mkdir(report_path)
                    with open('%s/%s-%s__%s-%s' % (report_path, inst1.itype, inst1.region, inst2.itype, inst2.region), 'a+') as f:
                        f.write(json.dumps(report, indent=4, sort_keys=True))
                        f.write('\n')
                    print report['speed']
                    break
                else:
                    time.sleep(5)
            print '[END] iperf'

        ssh_cli.close()
    except Exception:

        print '[EXCEPTION] %s\n' % traceback.print_exc()

    finally:

        inst1.terminate()
        inst2.terminate()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--instance', default=None, help='instance type <m1.small|n1-standard-1|etc>')
    parser.add_argument('-m', '--mode', default=None, help='region mode <us-us|eu-us> for network-io test')
    parser.add_argument('-n', '--number', default=1, type=int, help='number of test iterations')
    parser.add_argument('-s', '--size', default=1, type=int, help='file size in MB')
    parser.add_argument('-t', '--timeout', default=360, type=int, help='timeout for netcat and scp test, seconds')

    args = parser.parse_args()

    start_time = time.time()

    regions = {
                'ec2':{
                    'us-us':{
                        'region1':'us-west-1',
                        'region2':'us-west-2'},
                    'eu-us':{
                        'region1':'us-east-1',
                        'region2':'eu-west-1'}},
                'gce':{
                    'us-us':{
                        'region1':'us-central1-a',
                        'region2':'us-central2-a'},
                    'eu-us':{
                        'region1':'us-central1-a',
                        'region2':'europe-west1-a'}}}
    
    if args.instance in ec2.ec2_instance_types:
    
        ec2_images = {'us-east-1':'ami-3fec7956', 'eu-west-1':'ami-f2191786',
                'us-west-1':'ami-883714cd', 'us-west-2':'ami-4ac9437a'}
    
        region1 = regions['ec2'][args.mode]['region1']
        region2 = regions['ec2'][args.mode]['region2']
    
        network_io_test(args.instance, ec2_images[region1], region1, args.instance,
                ec2_images[region2], region2, filesize=args.size, iteration=int(args.number), timeout=args.timeout) 
    
    if args.instance in gce.gce_instance_types:
    
        google_image='https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'
    
        zone1 = regions['gce'][args.mode]['region1']
        zone2 = regions['gce'][args.mode]['region2']
    
        network_io_test(args.instance, google_image, zone1, args.instance,
                google_image, zone2, filesize=args.size, iteration=int(args.number), timeout=args.timeout) 

    print 'Tests finish in %s seconds' % (time.time() - start_time)
