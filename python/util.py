
import os
import scp
import paramiko
import traceback

import subprocess as subps


'''
def magic(func, *args, **kwargs):
    for i in range(3):
        try:
            ret = func(*args, **kwargs)
            break
        except:
            print sys.exc_info()
            time.sleep(10)
            continue
    else:
        print 'magic failed'
        raise
    return ret
'''


def instances_prepare(instances, packages=[]):

    for inst in instances:

        for i in range(3):
            try:

                print '[PREPARE] %s | %s' % (inst.itype, inst.region)

                ssh_cli = paramiko.SSHClient()
                ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh_cli.connect(inst.remote_ip, username=inst.user, key_filename=inst.ssh_key)

                scp_cli = scp.SCPClient(ssh_cli.get_transport())
                scp_cli.put('%s/.ssh/id_rsa' % os.environ['HOME'], '/tmp/id_rsa')
                scp_cli.put('%s/.ssh/id_rsa.pub' % os.environ['HOME'], '/tmp/id_rsa.pub')

                stdin, stdout, stderr = ssh_cli.exec_command('cat /tmp/id_rsa.pub >>$HOME/.ssh/authorized_keys')
                #print stderr.read()

                stdin, stdout, stderr = ssh_cli.exec_command('mv /tmp/id_rsa $HOME/.ssh/')
                #print stderr.read()

                stdin, stdout, stderr = ssh_cli.exec_command('mv /tmp/id_rsa.pub $HOME/.ssh/')
                #print stderr.read()

                stdin, stdout, stderr = ssh_cli.exec_command('chmod 400 $HOME/.ssh/id_rsa*')
                #print stderr.read()

                stdin, stdout, stderr = ssh_cli.exec_command('ssh-keyscan github.com >>$HOME/.ssh/known_hosts')
                #print stderr.read()

                for another_inst in [i for i in instances if i != inst]:
                    stdin, stdout, stderr = ssh_cli.exec_command('ssh-keyscan %s >>$HOME/.ssh/known_hosts'\
                                                                 % another_inst.remote_ip)
                    #print stderr.read()

                    stdin, stdout, stderr = ssh_cli.exec_command('ssh-keyscan %s >>$HOME/.ssh/authorized_keys'\
                                                                 % another_inst.remote_ip)
                    #print stderr.read()

                for pkg in packages:
                    print '[INSTALL] %s' % pkg
                    if inst.distr == 'debian':
                        manager = 'apt-get'
                    if inst.distr == 'centos':
                        manager = 'yum'
                        opt = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
                        cmd = 'ssh -t -i %s -l %s %s %s' % (inst.ssh_key, inst.user, opt, inst.remote_ip)
                        remote_cmd = "sudo sed -i -e 's/^Defaults.*requiretty/# &/' /etc/sudoers"
                        subps.call(cmd.split() + [remote_cmd])

                    stdin, stdout, stderr = ssh_cli.exec_command('sudo %s install -y %s' % (manager, pkg))
                    print stderr.read()
                    print stdout.read()

                ssh_cli.close()

                print '[PREPARE] done'
                break

            except scp.SCPException:
                
                print traceback.print_exc()

            except paramiko.SSHException:
                
                print traceback.print_exc()

