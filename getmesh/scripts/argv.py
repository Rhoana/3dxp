import sys, argparse

def toArgv(args, **flags):
    keyvals = flags.items()
    all_tokens = range(2*len(keyvals))
    endash = lambda fkey: '-'+fkey if len(fkey) == 1 else '--'+fkey
    enflag = lambda kv,fl: str(kv[fl]) if fl else endash(str(kv[fl]))
    kargv = [enflag(keyvals[i//2],i%2) for i in all_tokens]
    return ['main'] + list(map(str,args)) + kargv

## Demo usage

def parseArgv(argv):
    sys.argv = argv
    parser = argparse.ArgumentParser()
    parser.add_argument('a',default='a',nargs='?')
    parser.add_argument('-b',default='b')
    return vars(parser.parse_args())

def start(args, **flags):
    return main(toArgv(args,**flags))

def main(argv):
    return parseArgv(argv)

if __name__ == "__main__":
    print main(sys.argv)
