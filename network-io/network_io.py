
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


def network_io_test(
        inst_type='m1.small',
        ami1='ami-883714cd', ami2='ami-4ac9437a',
        region1='us-west-1', region2='us-west-2',
        filesize='5G'):

    f = open('%s.csv' % inst_type, 'w+')
    f.write('date;time;netcat;scp;iperf;iperfd;iperf4;iper8;iperf16\n')
    f.flush()
    f.close()

    conn1 = boto.ec2.connect_to_region(region1)
    conn2 = boto.ec2.connect_to_region(region2)

    print 'run first instance'
    reservation1 = conn1.run_instances(
            ami1,
            key_name='perf-bench-us-west-1',
            instance_type=inst_type,
            security_groups=['perf-bench-us-west-1'])

    inst1=reservation1.instances[0]

    print inst1

    print 'run second instance'
    reservation2 = conn2.run_instances(
            ami2,
            key_name='perf-bench-us-west-2',
            instance_type=inst_type,
            security_groups=['perf-bench-us-west-2'])

    inst2=reservation2.instances[0]

    print inst2

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

        print inst1.ip_address
        print inst2.ip_address

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
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('mv /tmp/id_rsa $HOME/.ssh/')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('mv /tmp/id_rsa.pub $HOME/.ssh/')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('chmod 400 $HOME/.ssh/id_rsa*')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('cat /tmp/id_rsa.pub >> $HOME/.ssh/authorized_keys')
        print stderr.read()
        
        stdin, stdout, stderr = ssh_cli2.exec_command('mv /tmp/id_rsa $HOME/.ssh/')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('mv /tmp/id_rsa.pub $HOME/.ssh/')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('chmod 400 $HOME/.ssh/id_rsa*')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan github.com >> $HOME/.ssh/known_hosts')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % inst2.ip_address)
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % inst2.ip_address)
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan github.com >> $HOME/.ssh/known_hosts')
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/known_hosts' % inst1.ip_address)
        print stderr.read()

        stdin, stdout, stderr = ssh_cli2.exec_command('ssh-keyscan %s >> $HOME/.ssh/authorized_keys' % inst1.ip_address)
        print stderr.read()

        stdin, stdout, stderr = ssh_cli1.exec_command('export DEBIAN_FRONTEND=noninteractive;sudo apt-get install -y iperf fio')
        stdout.channel.recv_exit_status()
        #stdin, stdout, stderr = ssh_cli1.exec_command('git clone git@github.com:Scalr/perf-benchmarks.git $HOME/perf-benchmarks')

        stdin, stdout, stderr = ssh_cli2.exec_command('export DEBIAN_FRONTEND=noninteractive;sudo apt-get install -y iperf fio')
        stdout.channel.recv_exit_status()
        #stdin, stdout, stderr = ssh_cli2.exec_command('git clone git@github.com:Scalr/perf-benchmarks.git $HOME/perf-benchmarks')

        ssh_cli1.close()
        ssh_cli2.close()

        today = datetime.datetime.today()
        f = open('%s.csv' % inst_type, 'a+')

        netcat_start_time = time.time()
        netcat_time = netcat_test(inst1.ip_address, inst2.ip_address, '10M')
        print 'netcat;%i:%s;' % (netcat_start_time, netcat_time)

        scp_start_time = time.time()
        scp_time = scp_test(inst1.ip_address, inst2.ip_address, '10M')
        print 'scp;%i:%s;' % (scp_start_time, scp_time)

        speed = iperf_test(inst1.ip_address, inst2.ip_address)

        f.write('%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (today.date(), today.strftime('%H:%m:%S'), netcat_time, scp_time, speed, 4, 5, 6 , 7))
        f.flush()
        f.close()

        print 'ok'
        time.sleep(1*60)

    except:

        print sys.exc_info()

    finally:

        print 'terminating instances ...'
        conn1.terminate_instances(instance_ids=[inst1.id])
        conn2.terminate_instances(instance_ids=[inst2.id])


def scp_test(ip_from, ip_to, filesize):

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username='ubuntu', key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /tmp/out.file' % filesize)
    print stdout.read()
    print stderr.read()

    print 'scp test ...'

    print 'send %s to %s' % (filesize, ip_to)
    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('scp /tmp/out.file ubuntu@%s:/tmp/scp.file' % ip_to)
    stdout.channel.recv_exit_status()
    end_time = time.time()
    print stderr.read()
    ssh_cli.close()

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_to, username='ubuntu', key_filename=ssh_key)
    stdin, stdout, stderr = ssh_cli.exec_command('ls -lah /tmp')
    print stdout.read()
    print stderr.read()
    ssh_cli.close()

    return end_time - start_time


def netcat_test(ip_from, ip_to, filesize):

    p = subps.Popen([
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-l", "ubuntu",
            ip_to,
            'nc -l 7777 > /tmp/netcat.file'],
            stdout=subps.PIPE, stderr=subps.PIPE, close_fds=True)
    print 'run netcat listener on %s' % ip_to

    time.sleep(1)

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_from, username='ubuntu', key_filename=ssh_key)

    stdin, stdout, stderr = ssh_cli.exec_command('truncate -s %s /tmp/out.file' % filesize)
    print stdout.read()
    print stderr.read()

    print 'netcat test ...'

    start_time = time.time()
    stdin, stdout, stderr = ssh_cli.exec_command('sudo killall -9 nc')
    stdout.channel.recv_exit_status()

    print 'send %s to %s' % (filesize, ip_to)
    stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/out.file | nc %s 7777 -q 0' % ip_to)
    stdout.channel.recv_exit_status()
    end_time = time.time()
    print stderr.read()
    ssh_cli.close()

    ssh_cli = paramiko.SSHClient()
    ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_cli.connect(ip_to, username='ubuntu', key_filename=ssh_key)
    stdin, stdout, stderr = ssh_cli.exec_command('ls -lah /tmp')
    print stdout.read()
    print stderr.read()
    ssh_cli.close()

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
    stdin, stdout, stderr = ssh_cli.exec_command("iperf -c %s -p 1234 -t 5 | grep '/sec' >> /tmp/iperf.log" % ip_serv)
    stdout.channel.recv_exit_status()
    print stderr.read()
    stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/iperf.log')
    stdout.channel.recv_exit_status()
    print stderr.read()
    out = stdout.read()

    speed = 'unknown'
    for line in out.split('\n'):
        if line.endswith('/sec'):
            speed = line.split()[-2]

    stdin, stdout, stderr = ssh_serv.exec_command('sudo killall -9 iperf')
    stdout.channel.recv_exit_status()

    ssh_cli.close()
    ssh_serv.close()

    return speed



if __name__ == '__main__':

    network_io_test()

