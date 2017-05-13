import sys, argparse
from toArgv import toArgv

def start(_argv):
    args = parseArgv(_argv)
    return args

def parseArgv(argv):
    sys.argv = argv

    help = {
        'help': 'Basic demo for toArgv script'
    }

    parser = argparse.ArgumentParser(description=help['help'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

