
import os

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

    def launch(self):
        print '[LAUNCHING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)

        self._conn = boto.ec2.connect_to_region(self.region)

        reservation = self._conn.run_instances(
                self.image,
                key_name=self.key_name,
                instance_type=self.itype,
                security_groups=[self.sec_group])

        self._inst = reservation.instances[0]
        self.remote_ip = self._inst.ip_address

    def update(self):
        
        self._inst.update()
        self.remote_ip = self._inst.ip_address

    def terminate(self):
        print '[TERMINATING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)

        self._conn.terminate_instances(instance_ids=[self._inst.id])

        print '[TERMINATED]'
