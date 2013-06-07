
import json
import argparse

def parse(data):

    speed = float(data['size']) / float(data['time'])
    out = '%s %s' % (data['datetime'], speed)
    return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('-f', '--file', help="file")

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        raw = f.read()
        for el in raw.replace('}', '}#').split('#'):
            try:
                data = json.loads(el)
                print parse(data)
            except:
                pass
