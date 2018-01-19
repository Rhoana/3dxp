from toArgv import toArgv
import sys, argparse
import os

def get_labels(label_str, max_count=1):
    count = 0
    for one_str in label_str.split(' '):
        one_list = one_str.split(',')
        one_iter = map("'{}'".format, one_list)
        bar_str = '_'.join(one_iter)
        count += 1
        yield bar_str
        # Handle extra data
        if count > max_count:
            sys.stderr.write('Extra #%d\r\n' % count)
            return

    # Handle missing data
    for _ in range(max_count - count):
        sys.stderr.write('Missing #%d\r\n' % count)
        yield ''

def start(_argv):

    args = parseArgv(_argv)
    INDEX = args['index']
    IN_DIR = args['input']
    url_file = os.path.join(IN_DIR, 'url.txt')
    ids_file = os.path.join(IN_DIR, 'ids.txt')

    # Find the url
    url_str = '%s'
    with open(url_file, 'r') as f:
        for line in f:
            if len(line) and line[0] != '#':
                url_str = line.rstrip('\n')
                continue

    # Find the labels
    label_str = ''
    with open(ids_file, 'r') as f:
        for i,line in enumerate(f):
            if i == INDEX:
                label_str = line.rstrip('\n')
                continue

    # Format the url with the labels
    num_lists = url_str.count('%')
    list_iter = get_labels(label_str)
    print url_str % tuple(list_iter)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'help': 'Make NG URL for a mapping of IDs',
        'input': 'Directory with /url.txt and ids.txt',
        'index': 'URL index for ID mapping',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('input', type=str, help=help['input'])
    parser.add_argument('index', type=int, help=help['index'])

    # Get all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)
