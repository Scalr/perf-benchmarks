
import boto.ec2
import telnetlib

from time import sleep, time

number_of_instances = 1000
seconds_in_day = 60.0 * 60.0 * 24
time_remaining = seconds_in_day

f = open('ec2.csv', 'w+')
conn = boto.ec2.connect_to_region('us-east-1')

for i in range(number_of_instances):
    reservation = conn.run_instances('ami-3fec7956', key_name='roma', instance_type='t1.small', security_groups=['roma'])
    instances = reservation.instances
    start_time = time()
    inst = instances[0]

    while inst.ip_address is None:
        inst.update()
        sleep(0.2)

    while True:
        try:
            telnetlib.Telnet(inst.ip_address, 22, 1)
            break
        except:
            pass

    stop_time = time()

    instance_time = stop_time - start_time

    time_remaining = time_remaining - instance_time

    f.write('%i\t%s\n' % (start_time, instance_time))
    f.flush()

    conn.terminate_instances(instance_ids=[instances[0].id])

    print '%s;%s' % (i, instance_time)
    
    try:
        print 'sleep %s' % (time_remaining / (number_of_instances - i - 1))
        sleep(time_remaining / (number_of_instances - i - 1))
    except ZeroDivisionError:
        pass

f.close()
