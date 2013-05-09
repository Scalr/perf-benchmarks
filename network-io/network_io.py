
import os
import sys
import time
import boto.ec2
import telnetlib
import logging
import scp
import paramiko
import datetime

import subprocess as subps
import multiprocessing as mp

ssh_key = '%s/.ssh/id_rsa' % os.environ['HOME']


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

    print inst_type, inst1

    reservation2 = conn2.run_instances(
            ami2,
            key_name='perf-bench-%s' % region2,
            instance_type=inst_type,
            security_groups=['perf-bench-%s' % region2])

    inst2=reservation2.instances[0]

    print inst_type, inst2

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

        print inst_type, inst1.ip_address
        print inst_type, inst2.ip_address

        ssh_cli1 = paramiko.SSHClient()
        ssh_cli1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_cli2 = paramiko.SSHClient()
        ssh_cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key1 = '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region1)
        ssh_cli1.connect(inst1.ip_address, username='ubuntu', key_filename=key1)

        key2 = '%s/.ssh/perf-bench-%s.pem' % (os.environ['HOME'], region2)
        ssh_cli2.connect(inst2.ip_address, username='ubuntu', key_filename=key2)

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

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % inst2.ip_address)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % inst2.ip_address)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan github.com >> $HOME/.ssh/known_hosts')
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % inst1.ip_address)
        stderr.read()
        #print inst_type, stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % inst1.ip_address)
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

        today = datetime.datetime.today()

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

        print inst_type, 'terminating instances ...'
        conn1.terminate_instances(instance_ids=[inst1.id])
        conn2.terminate_instances(instance_ids=[inst2.id])


def scp_test(ip_from, ip_to, filesize):

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username='ubuntu', key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /tmp/out.file' % filesize)
    print stderr.read()

    print 'scp send %s to %s' % (filesize, ip_to)

    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('scp /tmp/out.file ubuntu@%s:/dev/null' % ip_to)
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
            "-l", "ubuntu",
            ip_to,
            'nc -l 7777 > /dev/null'],
            stdout=subps.PIPE, stderr=subps.PIPE, close_fds=True)
    print 'run netcat listener on %s' % ip_to

    time.sleep(1)

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username='ubuntu', key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /tmp/out.file' % filesize)
    print stderr.read()

    stdin, stdout, stderr = ssh_cli.exec_command('sudo killall -9 nc')
    stdout.channel.recv_exit_status()

    print 'netcat send %s to %s' % (filesize, ip_to)

    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/out.file | nc %s 7777 -q 0' % ip_to)
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
    ssh_serv.connect(ip_serv, username='ubuntu', key_filename=ssh_key)
    stdin, stdout, stderr = ssh_serv.exec_command('sudo killall -9 iperf')
    stdout.channel.recv_exit_status()
    stdin, stdout, stderr = ssh_serv.exec_command('iperf -s -p 1234 &>/dev/null')

    print 'iperf server start'

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_cli, username='ubuntu', key_filename=ssh_key)
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



if __name__ == '__main__':

    ps = []

    for itype in ['m1.small', 'm1.xlarge', 'c1.medium']:

        ps.append(mp.Process(target=ec2_network_io_test,
                kwargs={'inst_type':itype, 'filesize':'5G'}))
        ps.append(mp.Process(target=ec2_network_io_test,
                        kwargs={'inst_type':itype, 'region1':'us-east-1', 'ami1':'ami-3fec7956',
                        'region2':'eu-west-1', 'ami2':'ami-f2191786', 'filesize':'5G'}))

    for p in ps:
        p.start()

    for p in ps:
        try:
            p.join()
        except KeyboardInterrupt:
            pass
