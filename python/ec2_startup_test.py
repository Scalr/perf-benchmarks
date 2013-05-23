
import time
import argparse
import boto.ec2
import datetime
import telnetlib


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--number', type=int, default=1, help='number of instances for start')
    parser.add_argument('-i', '--interval', default=60, type=int, help='interval between starts')

    args = parser.parse_args()

    conn = boto.ec2.connect_to_region('us-east-1')

    for i in range(args.number):
        if i is not 0:
            time.sleep(args.interval)

        start_time = time()
        utcnow = datetime.datetime.utcnow()
        time_str = utcnow.strftime('%d:%m:%Y;%H:%M:S') 

        reservation = conn.run_instances('ami-3fec7956', key_name='roma', instance_type='t1.micro', security_groups=['roma'])
        instances = reservation.instances
        inst = instances[0]

        while inst.ip_address is None:
            inst.update()
            time.sleep(0.2)

        while True:
            try:
                telnetlib.Telnet(inst.ip_address, 22, 1)
                break
            except:
                pass

        stop_time = time()

        conn.terminate_instances(instance_ids=[instances[0].id])

        instance_time = stop_time - start_time

        with open('ec2.csv', 'w+') as f:
            f.write('%s;%s\n' % (time_str, instance_time))

        print '%s;%s' % (time_str, instance_time)

