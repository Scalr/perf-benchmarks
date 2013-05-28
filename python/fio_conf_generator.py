
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--name', default='Name', help='name')
    parser.add_argument('-f', '--file', default='/tmp/fio.file', help='file or device name')
    parser.add_argument('-s', '--size', default='1G', help='file size')
    parser.add_argument('-m', '--mode', default='randrw', help='rw mode')
    parser.add_argument('-b', '--bs', default='1k', help='block size')
    parser.add_argument('-d', '--depth', default='1', help='io depth')
    parser.add_argument('-t', '--runtime', type=int, default=120,  help='runtime')
    parser.add_argument('-o', '--out', default='/tmp/fio_conf.fio', help='fio config output')

    args = parser.parse_args()

    with open(args.out, 'w') as f:
        f.write('[global]\n')
        f.write('clocksource=cpu\n')
        f.write('ioscheduler=deadline\n')
        f.write('ramp_time=30\n')
        f.write('randrepeat=0\n')
        f.write('ioengine=libaio\n')
        f.write('direct=1\n')

        f.write('[%s]\n' % args.name)
        f.write('filename=%s\n' % args.file)
        f.write('rw=%s\n' % args.mode)
        f.write('size=%s\n' % args.size)
        f.write('bs=%s\n' % args.bs)
        f.write('iodepth=%s\n' % args.depth)
        f.write('runtime=%s\n' % args.runtime)
        f.write('stonewall\n')

