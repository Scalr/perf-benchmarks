
import os
import sys
import time
import boto.ec2
import telnetlib
import logging
import scp
import paramiko
import datetime
import argparse

import subprocess as subps
import multiprocessing as mp

ssh_key = '%s/.ssh/id_rsa' % os.environ['HOME']

USER = 'ubuntu'


def ec2_network_io_test(
        inst_type='m1.small',
        ami1='ami-883714cd', ami2='ami-4ac9437a',
        region1='us-west-1', region2='us-west-2',
        filesize='5G'):

    conn1 = boto.ec2.connect_to_region(region1)
    conn2 = boto.ec2.connect_to_region(region2)

    reservation1 = conn1.run_instances(
            ami1,
            key_name='perf-bench-%s' % region1,
            instance_type=inst_type,
            security_groups=['perf-bench-%s' % region1])

    inst1=reservation1.instances[0]

    reservation2 = conn2.run_instances(
            ami2,
            key_name='perf-bench-%s' % region2,
            instance_type=inst_type,
            security_groups=['perf-bench-%s' % region2])

    inst2=reservation2.instances[0]

    try:

        for i in range(150):
            inst1.update()
            inst2.update()
            if inst1.ip_address != None and inst2.ip_address != None:
                break
            time.sleep(2)

        for i in range(120):
            try:
                telnetlib.Telnet(inst1.ip_address, 22, 1)
                telnetlib.Telnet(inst2.ip_address, 22, 1)
                break
            except:
                time.sleep(1)

        print '%s:%s:%s up' %(inst_type, region1, inst1.ip_address)
        print '%s:%s:%s up' %(inst_type, region2, inst2.ip_address)

        key1 = '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region1)
        key2 = '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region2)
        instances_prepare(inst1.ip_address, key1, inst2.ip_address, key2)

        today = datetime.datetime.utcnow()

        netcat_start_time = time.time()
        netcat_time = netcat_test(inst1.ip_address, inst2.ip_address, filesize)
        print inst_type, 'netcat;%s;' % netcat_time

        scp_start_time = time.time()
        scp_time = scp_test(inst1.ip_address, inst2.ip_address, filesize)
        print inst_type, 'scp;%s;' % scp_time

        speed1, speed4, speed8, speed12, speed16 = iperf_test(inst1.ip_address, inst2.ip_address)

        f = open('%s-%s-%s.csv' % (inst_type, region1, region2), 'a+')
        f.write('%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (
                today.date(), today.strftime('%H:%M:%S'), netcat_time, scp_time,
                speed1, speed4, speed8, speed12, speed16))
        f.flush()
        f.close()

        print inst_type, 'ok'
        time.sleep(5)

    except:

        print inst_type, sys.exc_info()

    finally:

        print 'terminating instances %s:%s:%s ...' %(inst_type, region1, inst1.ip_address)
        print 'terminating instances %s:%s:%s ...' %(inst_type, region2, inst2.ip_address)
        conn1.terminate_instances(instance_ids=[inst1.id])
        conn2.terminate_instances(instance_ids=[inst2.id])


def instances_prepare(ip1, key1, ip2, key2):

        ssh_cli1 = paramiko.SSHClient()
        ssh_cli1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_cli2 = paramiko.SSHClient()
        ssh_cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_cli1.connect(ip1, username=USER, key_filename=key1)
        ssh_cli2.connect(ip2, username=USER, key_filename=key2)

        scp_cli1 = scp.SCPClient(ssh_cli1.get_transport())
        scp_cli1.put('%s/.ssh/id_rsa' % os.environ['HOME'], '/tmp/id_rsa')
        scp_cli1.put('%s/.ssh/id_rsa.pub' % os.environ['HOME'], '/tmp/id_rsa.pub')

        scp_cli2 = scp.SCPClient(ssh_cli2.get_transport())
        scp_cli2.put('%s/.ssh/id_rsa' % os.environ['HOME'], '/tmp/id_rsa')
        scp_cli2.put('%s/.ssh/id_rsa.pub' % os.environ['HOME'], '/tmp/id_rsa.pub')

        stdin, stdout, stderr = ssh_cli1.exec_command('cat /tmp/id_rsa.pub >> $HOME/.ssh/authorized_keys')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('mv /tmp/id_rsa $HOME/.ssh/')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('mv /tmp/id_rsa.pub $HOME/.ssh/')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('chmod 400 $HOME/.ssh/id_rsa*')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('cat /tmp/id_rsa.pub >> $HOME/.ssh/authorized_keys')
        stderr.read()
        #print inst_type, stderr.read()
        
        stdin, stdout, stderr = ssh_cli2.exec_command('mv /tmp/id_rsa $HOME/.ssh/')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('mv /tmp/id_rsa.pub $HOME/.ssh/')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('chmod 400 $HOME/.ssh/id_rsa*')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan github.com >> $HOME/.ssh/known_hosts')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % ip2)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % ip2)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan github.com >> $HOME/.ssh/known_hosts')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % ip1)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % ip1)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('export DEBIAN_FRONTEND=noninteractive;sudo apt-get install -y iperf fio')
        stdout.channel.recv_exit_status()
        #stdin, stdout, stderr = ssh_cli1.exec_command('git clone git@github.com:Scalr/perf-benchmarks.git $HOME/perf-benchmarks')

        stdin, stdout, stderr = ssh_cli2.exec_command('export DEBIAN_FRONTEND=noninteractive;sudo apt-get install -y iperf fio')
        stdout.channel.recv_exit_status()
        #stdin, stdout, stderr = ssh_cli2.exec_command('git clone git@github.com:Scalr/perf-benchmarks.git $HOME/perf-benchmarks')

        ssh_cli1.close()
        ssh_cli2.close()


def scp_test(ip_from, ip_to, filesize):

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username=USER, key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /$HOME/scp.file' % filesize)
    print stderr.read()

    print 'scp send %s to %s' % (filesize, ip_to)

    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('scp /$HOME/scp.file %s@%s:/dev/null' % (USER, ip_to))
    stdout.channel.recv_exit_status()
    end_time = time.time()
    print stderr.read()
    ssh_cli.close()

    #ssh_cli = paramiko.SSHClient()
    #ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh_cli.connect(ip_to, username='ubuntu', key_filename=ssh_key)
    #stdin, stdout, stderr = ssh_cli.exec_command('ls -lah /tmp')
    #print stdout.read()
    #print stderr.read()
    #ssh_cli.close()

    return end_time - start_time


def netcat_test(ip_from, ip_to, filesize):

    p = subps.Popen([
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-l", USER,
            ip_to,
            'sudo killall -9 nc;nc -l 7777 > /dev/null'],
            stdout=subps.PIPE, stderr=subps.PIPE, close_fds=True)
    print 'run netcat listener on %s' % ip_to

    time.sleep(1)

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username=USER, key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /$HOME/netcat.file' % filesize)
    print stderr.read()

    stdin, stdout, stderr = ssh_cli.exec_command('sudo killall -9 nc')
    stdout.channel.recv_exit_status()

    print 'netcat send %s to %s' % (filesize, ip_to)

    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('cat /$HOME/netcat.file | nc %s 7777 -q 0' % ip_to)
    stdout.channel.recv_exit_status()
    end_time = time.time()
    print stderr.read()
    ssh_cli.close()

    #ssh_cli = paramiko.SSHClient()
    #ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh_cli.connect(ip_to, username='ubuntu', key_filename=ssh_key)
    #stdin, stdout, stderr = ssh_cli.exec_command('ls -lah /tmp')
    #print stdout.read()
    #print stderr.read()
    #ssh_cli.close()

    return end_time - start_time


def iperf_test(ip_serv, ip_cli):

    ssh_serv = paramiko.SSHClient()
    ssh_serv.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_serv.connect(ip_serv, username=USER, key_filename=ssh_key)
    stdin, stdout, stderr = ssh_serv.exec_command('sudo killall -9 iperf')
    stdout.channel.recv_exit_status()
    stdin, stdout, stderr = ssh_serv.exec_command('iperf -s -p 1234 &>/dev/null')

    print 'iperf server start'

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_cli, username=USER, key_filename=ssh_key)
    stdin, stdout, stderr = ssh_cli.exec_command('sudo killall -9 iperf')
    stdout.channel.recv_exit_status()

    speed = []

    stdin, stdout, stderr = ssh_cli.exec_command(
            "iperf -c %s -p 1234 -t 30 -f m | grep '/sec' > /tmp/iperf.log" % ip_serv)
    stdout.channel.recv_exit_status()
    print stderr.read()
    stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/iperf.log')
    stdout.channel.recv_exit_status()
    print stderr.read()
    out = stdout.read()

    for line in out.split('\n'):
        if line.endswith('/sec'):
            print line
            speed.append(line.split()[-2])


    for p in [4, 8, 12, 16]:
        stdin, stdout, stderr = ssh_cli.exec_command(
                "iperf -c %s -p 1234 -t 30 -P %s -f m | grep '/sec' > /tmp/iperf.log" % (ip_serv, p))
        stdout.channel.recv_exit_status()
        print stderr.read()
        stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/iperf.log')
        stdout.channel.recv_exit_status()
        print stderr.read()
        out = stdout.read()

        for line in out.split('\n'):
            if '[SUM]' in line:
                print line
                speed.append(line.split()[-2])


    stdin, stdout, stderr = ssh_serv.exec_command('sudo killall -9 iperf')
    stdout.channel.recv_exit_status()

    ssh_cli.close()
    ssh_serv.close()

    return speed



def gce_network_io_test(
       inst_type='n1-standard-1',
       zone1='us-central1-a', zone2='us-central2-a',
       image='https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325',
       filesize='5G'):

    name1 = 'pb-%s-%s' % (inst_type, zone1)
    name2 = 'pb-%s-%s' % (inst_type, zone2)

    p1 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'addinstance',
                 name1,
                 '--machine_type=%s' % inst_type,
                 '--zone=%s' % zone1,
                 '--image=%s' % image], stdout=subps.PIPE, stderr=subps.PIPE)
    print p1.stderr.read()

    p2 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'addinstance',
                 name2,
                 '--machine_type=%s' % inst_type,
                 '--zone=%s' % zone2,
                 '--image=%s' % image], stdout=subps.PIPE, stderr=subps.PIPE)
    print p2.stderr.read()

    p1 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'getinstance',
                 name1], stdout=subps.PIPE, stderr=subps.PIPE)
    out1 = p1.stdout.read()

    p2 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'getinstance',
                 name2], stdout=subps.PIPE, stderr=subps.PIPE)
    out2 = p2.stdout.read()

    ip1 = None
    ip2 = None

    for line in out1.split('\n'):
        if 'external-ip' in line:
            ip1 = line.split('|')[2].strip()

    for line in out2.split('\n'):
        if 'external-ip' in line:
            ip2 = line.split('|')[2].strip()

    if ip1 == None or ip2 == None:
        print "Couldn't detect IP. Exit"
        return

    for i in range(300):
        try:
            telnetlib.Telnet(ip1, 22, 1)
            telnetlib.Telnet(ip2, 22, 1)
            break
        except:
            time.sleep(1)

    print '%s:%s:%s up' % (inst_type, zone1, ip1)
    print '%s:%s:%s up' % (inst_type, zone2, ip2)

    key1 = '%s/.ssh/google_compute_engine' % os.environ['HOME']
    key2 = '%s/.ssh/google_compute_engine' % os.environ['HOME']
    instances_prepare(ip1, key1, ip2, key2)

    today = datetime.datetime.utcnow()

    netcat_start_time = time.time()
    netcat_time = netcat_test(ip1, ip2, filesize)
    print inst_type, 'netcat;%s;' % netcat_time

    scp_start_time = time.time()
    scp_time = scp_test(ip1, ip2, filesize)
    print inst_type, 'scp;%s;' % scp_time

    speed1, speed4, speed8, speed12, speed16 = iperf_test(ip1, ip2)

    f = open('%s-%s-%s.csv' % (inst_type, zone1, zone2), 'a+')
    f.write('%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (
            today.date(), today.strftime('%H:%M:%S'), netcat_time, scp_time,
            speed1, speed4, speed8, speed12, speed16))
    f.flush()
    f.close()

    print inst_type, 'ok'
    time.sleep(5)

    print 'terminating %s' % name1
    p1 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'deleteinstance',
                 name1],
                 stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)
    p1.communicate(input='yes')
    print '%s terminated' % name1

    print 'terminating %s' % name2
    p2 = subps.Popen(['gcutil',
                 '--project=scalr.com:scalr-labs',
                 'deleteinstance',
                 name2],
                 stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)
    p2.communicate(input='yes')
    print '%s terminated' % name2



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--cloud', default='ec2', help='cloud for test <ec2|gce>')

    args = parser.parse_args()

    print args.cloud

    ps = []


    if args.cloud == 'ec2':
        global USER
        USER = 'ubuntu'
        print USER
        for itype in ['m1.small', 'm1.xlarge', 'c1.medium']:
        #for itype in ['m1.small']:

            ps.append(mp.Process(target=ec2_network_io_test,
                            kwargs={'inst_type':itype, 'region1':'us-east-1', 'ami1':'ami-3fec7956',
                            'region2':'eu-west-1', 'ami2':'ami-f2191786', 'filesize':'5G'}))

    if args.cloud == 'gce':
        USER = os.environ['USER']
        print USER
        for itype in ['n1-standard-1', 'n1-standard-8', 'n1-highcpu-4']:
        #for itype in ['n1-standard-1']:

            ps.append(mp.Process(target=gce_network_io_test,
                            kwargs={'inst_type':itype,
                            'zone2':'europe-west1-a', 'filesize':'5G'}))

    for p in ps:
        p.start()

    for p in ps:
        try:
            p.join()
        except KeyboardInterrupt:
            pass
