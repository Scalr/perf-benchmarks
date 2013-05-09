
import boto.ec2
import telnetlib
import time

number_of_inst = 1000
seconds_in_day = 60.0*60*24
time_remain = seconds_in_day

f = open('ec2', 'w+')
conn = boto.ec2.connect_to_region('us-east-1')

for i, _ in enumerate(range(number_of_inst)):
    reservation = conn.run_instances('ami-3fec7956', key_name='roma', instance_type='t1.micro', security_groups=['roma'])
    instances = reservation.instances
    start_time = time.time()
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

    stop_time = time.time()

    inst_time = stop_time - start_time

    time_remain = time_remain - inst_time

    f.write('%i\t%s\n' % (start_time, inst_time))
    f.flush()

    conn.terminate_instances(instance_ids=[instances[0].id])

    print '%s\t%s' % (i, inst_time)
    
    try:
        print time_remain
        print number_of_inst-i-1
        print 'sleep %s' % (time_remain/(number_of_inst-i-1))
        time.sleep(time_remain/(number_of_inst-i-1))
    except ZeroDivisionError:
        pass

f.close()
