
import os
import time
import traceback

import boto.ec2


ec2_instance_types = [
        't1.micro',
        'm1.small',
        'm1.medium',
        'm1.large',
        'm1.xlarge',
        'm3.xlarge',
        'm3.2xlarge',
        'm2.xlarge',
        'm2.2xlarge',
        'm2.4xlarge',
        'c1.medium',
        'c1.xlarge',
        'hi1.4xlarge',
        'hs1.8xlarge']


class EC2Inst(object):

    def __init__(self, itype, image, region, user, ssh_key, sec_group):

        self.itype = itype
        self.image = image
        self.region = region
        self.remote_ip = None
        self.user = user
        self.key_name = os.path.basename(ssh_key)[0:-4] if ssh_key.endswith('.pem') else os.path.basename(ssh_key)
        self.ssh_key = ssh_key
        self.sec_group = sec_group
        self.cloud = 'ec2'
        self._vol = None

        if image in ['ami-3fec7956', 'ami-f2191786', 'ami-883714cd', 'ami-4ac9437a']:
            self.distr = 'debian'
        if image in ['ami-05355a6c', 'ami-3ffed17a', 'ami-0358ce33', 'ami-c7c0d6b3']:
            self.distr = 'centos'

    def launch(self, disk_size=None):
        print '[LAUNCHING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)

        self._conn = boto.ec2.connect_to_region(self.region)

        reservation = self._conn.run_instances(
                self.image,
                key_name=self.key_name,
                instance_type=self.itype,
                security_groups=[self.sec_group])

        self._inst = reservation.instances[0]
        self.remote_ip = self._inst.ip_address

        if disk_size:
            try:
                print '[CREATING DISK]'
                self._vol = self._conn.create_volume(disk_size, self._inst.placement)
                print '[CREATE DISK] ok'
                print '[ATTACHING DISK]'
                for _ in range(24):
                    self.update()
                    if self._inst.state == 'running':
                        self._vol.attach(self._inst.id, '/dev/sdb')
                        print '[ATTACH DISK] ok'
                        break
                    else:
                        time.sleep(5)
                else:
                    print '[ATTACH DISK] timeout'
                    raise SystemExit
            except:
                self.terminate()
                raise

    def update(self):
        
        self._inst.update()
        self.remote_ip = self._inst.ip_address

    def terminate(self):

        if self._vol:
            try:
                print '[DETACHING DISK]'
                self._vol.update()
                if self._vol.detach(force=True):
                    print '[DETACH DISK] ok'
                else:
                    print '[DETACH DISK] failed'
            except:
                print '[DETACH DISK] failed'

            print '[TERMINATING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)
            self._conn.terminate_instances(instance_ids=[self._inst.id])
            print '[TERMINATED]'

            try:
                print '[DELETING DISK]'
                while self._vol.status != 'available':
                    self._vol.update()
                    time.sleep(5)
                if self._conn.delete_volume(self._vol.id):
                    print '[DELETE DISK] ok'
                else:
                    print '[DELETE DISK] failed'
            except:
                print '[DELETE DISK] failed'
                traceback.print_exc()
            self._vol = None

        else:
            print '[TERMINATING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)
            self._conn.terminate_instances(instance_ids=[self._inst.id])
            print '[TERMINATED]'
