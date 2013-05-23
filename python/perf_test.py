
import time
import argparse

import network_io


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--type', default=None, help='test type <network-io|disk-io>')
    parser.add_argument('-i', '--instance', default=None, help='instance type')
    parser.add_argument('-c', '--cloud', default='ec2', help='cloud platform for test <ec2|gce>')
    parser.add_argument('-m', '--mode', default=None, help='region mode <us-us|eu-us> for network-io test')
    parser.add_argument('-n', '--number', default=1, type=int, help='number of test iterations')
    parser.add_argument('-s', '--size', default='1024M', help='file size')
    parser.add_argument('-T', '--timeout', default=360, type=int, help='timeout for netcat and scp test, seconds')

    args = parser.parse_args()

    start_time = time.time()

    if args.type == 'network-io':
    
        regions = {
                    'ec2':{
                        'us-us':{
                            'region1':'us-west-1',
                            'region2':'us-west-2'},
                        'eu-us':{
                            'region1':'us-east-1',
                            'region2':'eu-west-1'}},
                    'gce':{
                        'us-us':{
                            'region1':'us-central1-a',
                            'region2':'us-central2-a'},
                        'eu-us':{
                            'region1':'us-central1-a',
                            'region2':'europe-west1-a'}}}
        
        if args.cloud == 'ec2':
        
            ec2_images = {'us-east-1':'ami-3fec7956', 'eu-west-1':'ami-f2191786',
                    'us-west-1':'ami-883714cd', 'us-west-2':'ami-4ac9437a'}
        
            region1 = regions[args.cloud][args.mode]['region1']
            region2 = regions[args.cloud][args.mode]['region2']
        
            network_io.netrwork_io_test(args.instance, ec2_images[region1], region1, args.instance,
                    ec2_images[region2], region2, filesize=args.size, iteration=int(args.number), timeout=args.timeout) 
        
        if args.cloud == 'gce':
        
            google_image='https://www.googleapis.com/compute/v1beta14/projects/google/global/images/gcel-12-04-v20130325'
        
            zone1 = regions[args.cloud][args.mode]['region1']
            zone2 = regions[args.cloud][args.mode]['region2']
        
            network_io.netrwork_io_test(args.instance, google_image, zone1, args.instance,
                    google_image, zone2, filesize=args.timeout, iteration=int(args.number), timeout=args.timeout) 

    print 'Tests finish in %s seconds' % (time.time() - start_time)

