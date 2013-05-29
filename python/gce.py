
import random

import subprocess as subps


gce_instance_types =  ['n1-standard-1',
                       'n1-standard-1-d',
                       'n1-standard-2',
                       'n1-standard-2-d',
                       'n1-standard-4',
                       'n1-standard-4-d',
                       'n1-standard-8',
                       'n1-standard-8-d',
                       'n1-highcpu-2',
                       'n1-highcpu-2-d',
                       'n1-highcpu-4',
                       'n1-highcpu-4-d',
                       'n1-highcpu-8',
                       'n1-highcpu-8-d',
                       'n1-highmem-2',
                       'n1-highmem-2-d',
                       'n1-highmem-4',
                       'n1-highmem-4-d',
                       'n1-highmem-8',
                       'n1-highmem-8-d']


class GCEInst(object):

    def __init__(self, itype, image, region, user, ssh_key):
        
        self.itype = itype
        self.image = image
        self.region = region
        self.remote_ip = None
        self.user = user
        self.ssh_key = ssh_key  #'%s/.ssh/google_compute_engine' % os.environ['HOME']
        self.cloud = 'gce'
        self.disk_name = None

        self.distr = 'debian'

    def launch(self, disk_size=None):
        print '[LAUNCHING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)

        self.name = '%s-%s%s' % (self.itype, random.randint(100, 999), random.randint(100, 999))

        p = subps.Popen(['/usr/local/bin/gcutil',
                     '--project=scalr.com:scalr-labs',
                     'addinstance',
                     self.name,
                     '--machine_type=%s' % self.itype,
                     '--zone=%s' % self.region,
                     '--image=%s' % self.image], stdout=subps.PIPE, stderr=subps.PIPE)
        print p.stderr.read() 
        print p.stdout.read()

        if disk_size:
            self.disk_name = '%s-fiodisk' % self.name

            p = subps.Popen(['/usr/local/bin/gcutil',
                         '--project=scalr.com:scalr-labs',
                         'adddisk',
                         '--size_gb=%s' % disk_size,
                         self.disk_name,
                         '--zone=%s' % self.region], stdout=subps.PIPE, stderr=subps.PIPE)
            print p.stderr.read() 
            print p.stdout.read()


            p = subps.Popen(['/usr/local/bin/gcutil',
                         '--project=scalr.com:scalr-labs',
                         'getdisk',
                         self.disk_name], stdout=subps.PIPE, stderr=subps.PIPE)
            print p.stderr.read() 
            print p.stdout.read()

            p = subps.Popen(['/usr/local/bin/gcutil',
                         '--project=scalr.com:scalr-labs',
                         'attachdisk',
                         '--disk',
                         self.disk_name,
                         self.name], stdout=subps.PIPE, stderr=subps.PIPE)
            print p.stderr.read() 
            print p.stdout.read()

    def update(self):

        p = subps.Popen(['/usr/local/bin/gcutil',
                     '--project=scalr.com:scalr-labs',
                     'getinstance',
                     self.name], stdout=subps.PIPE, stderr=subps.PIPE)
        out = p.stdout.read()

        for line in out.split('\n'):
            if 'external-ip' in line:
                self.remote_ip = line.split('|')[2].strip()

    def terminate(self):
        if self.disk_name:
            print '[DETACHING] %s' % self.disk_name
            p = subps.Popen(['/usr/local/bin/gcutil',
                         '--project=scalr.com:scalr-labs',
                         'detachdisk',
                         '--device_name',
                         self.disk_name,
                         self.name], stdout=subps.PIPE, stderr=subps.PIPE)
            print p.stderr.read() 
            print p.stdout.read()

            print '[TERMINATING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)
            p = subps.Popen(['/usr/local/bin/gcutil',
                    '--project=scalr.com:scalr-labs',
                    'deleteinstance',
                    self.name],
                    stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)
            p.communicate(input='yes')
            print '[TERMINATED]'

            print '[DELETING] %s' % self.disk_name
            p = subps.Popen(['/usr/local/bin/gcutil',
                         '--project=scalr.com:scalr-labs',
                         'deletedisk',
                         self.disk_name], stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)
            p.communicate(input='y')
            self.disk_name = None
            print '[DELETED]'

        else:
            print '[TERMINATING] %s | %s | %s | %s' % (self.itype, self.image, self.region, self.user)
            p = subps.Popen(['/usr/local/bin/gcutil',
                    '--project=scalr.com:scalr-labs',
                    'deleteinstance',
                    self.name],
                    stdin=subps.PIPE, stdout=subps.PIPE, stderr=subps.PIPE)
            p.communicate(input='yes')
            print '[TERMINATED]'
