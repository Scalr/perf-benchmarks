
import os
import scp
import json
import time
import argparse
import datetime
import paramiko
import telnetlib
import traceback

import subprocess as subps

import ec2
import gce

import util


def disk_io_test(itype, image, region, filesize=1, mode=['randrw'], bs=[1], depth=[1], runtime=60): 

    ssh_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.ssh/')

    if itype in ec2.ec2_instance_types:
        inst = ec2.EC2Inst(itype, image, region, 'ec2-user', '%s/perf-bench-%s.pem'\
                            % (ssh_path, region), 'perf-bench-%s' % region)

    if itype in gce.gce_instance_types:
        inst = gce.GCEInst(itype, image, region, os.environ['USER'], '%s/google_compute_engine' % ssh_path)

    report = []
    utcnow = datetime.datetime.utcnow()
    time_str = utcnow.strftime('%d:%m:%Y-%H:%M:%S') 

    inst.launch(disk_size=(filesize + 5))

    try:

        print '[IP] waiting'
        for i in range(150):
            inst.update()
            if inst.remote_ip != None:
                print '[IP] ok'
                break
            time.sleep(2)
        
        print '[SSH] waiting'
        for i in range(120):
            try:
                telnetlib.Telnet(inst.remote_ip, 22, 1)
                print '[SSH] ok'
                break
            except:
                time.sleep(2)
        
        print '[UP] %s | %s | %s' % (inst.itype, inst.region, inst.remote_ip)

        if inst.distr == 'centos':
            util.instances_prepare([inst], ['python27', 'fio', 'screen'])
        else:
            util.instances_prepare([inst], ['fio', 'screen'])

        ssh_cli = paramiko.SSHClient()
        ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_cli.connect(inst.remote_ip, username=inst.user, key_filename=inst.ssh_key)
        scp_cli = scp.SCPClient(ssh_cli.get_transport())
        scp_cli.put('fio_conf_generator.py', '/tmp/fio_conf_generator.py')
        scp_cli.put('fiotest.py', '/tmp/fiotest.py')

        mode_str = ' '.join(mode)
        bs_str = ' '.join(map(str, bs))
        depth_str = ' '.join(map(str, depth))

        print '[START] fio'

        stdin, stdout, stderr = ssh_cli.exec_command('python2.7 /tmp/fiotest.py -f %s -s %s -m %s -b %s -d %s -t %s'
                % ('/dev/sdb', filesize * 1024, mode_str, bs_str, depth_str, runtime))

        for _ in range((120 * len(mode) * len(bs) * len(depth) + 60) / 5):
            stdin, stdout, stderr = ssh_cli.exec_command('[ -s fio.report ]; echo $?')
            out = stdout.read()
            if out.strip() == '0':
                stdin, stdout, stderr = ssh_cli.exec_command('cat fio.report')
                report = json.loads(stdout.read())
                for test in report:
                    test.update({'instance':itype})
                    test.update({'region':region})
                    if itype in ec2.ec2_instance_types:
                        test.update({'cloud':'ec2'})
                    if itype in gce.gce_instance_types:
                        test.update({'cloud':'gce'})
                break
            else:
                time.sleep(5)

        print '[END] fio'

    except Exception, e:

        report.append({'error':str(e)}) 
        print '[EXCEPTION] %s\n' % traceback.print_exc()

    finally:

        try:
            report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results/disk-io/%s/%s'\
                                               % (inst.cloud, inst.itype))
            if not os.path.exists(report_path):
                print report_path
                subps.call('mkdir -p %s'.split() % report_path)
                #os.mkdir(report_path)
            with open('%s/%s-%s.fiores' % (report_path, time_str, inst.itype), 'a+') as f:
                f.write(json.dumps(report, indent=4, sort_keys=True))
                f.write('\n')
        finally:
            ssh_cli.close()
            inst.terminate()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--instance', default=None, help='instance type <m1.small|n1-standard-1|etc>')
    parser.add_argument('-r', '--region', default=None, help='region')
    parser.add_argument('-s', '--size', default=1, type=int, help='filesize in GB')
    parser.add_argument('-m', '--mode', nargs='+', type=str, default=['randrw'], help='mode <read|write|randread|randwrite|randrw>')
    parser.add_argument('-b', '--bs', nargs='+', type=int, default=1, help='block size in KB')
    parser.add_argument('-d', '--depth', nargs='+', type=int, default=1, help='iodepth')
    parser.add_argument('-t', '--runtime', type=int, default=120, help='runtime')

    args = parser.parse_args()

    start_time = time.time()

    if args.instance in ec2.ec2_instance_types:
    
        # ubuntu 
        #ec2_images = {
        #    'us-east-1':'ami-3fec7956',
        #    'eu-west-1':'ami-f2191786',
        #    'us-west-1':'ami-883714cd',
        #    'us-west-2':'ami-4ac9437a'}

        # amazon linux
        ec2_images = {
            'us-east-1':'ami-05355a6c',
            'us-west-1':'ami-3ffed17a',
            'us-west-2':'ami-0358ce33',
            'eu-wets-1':'ami-c7c0d6b3'}
    
        disk_io_test(args.instance, ec2_images[args.region], args.region, args.size, args.mode, args.bs, args.depth, args.runtime) 
    
    if args.instance in gce.gce_instance_types:
    
        google_image='https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'
    
        disk_io_test(args.instance, google_image, args.region, args.size, args.mode, args.bs, args.depth, args.runtime) 

    print 'Tests finish in %s seconds' % (time.time() - start_time)

