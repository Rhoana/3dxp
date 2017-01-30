import sys, argparse

def toArgv(*args, **flags):
    keyvals = flags.items()
    all_tokens = range(2*len(keyvals))
    endash = lambda fkey: '-'+fkey if len(fkey) == 1 else '--'+fkey
    enflag = lambda kv,fl: str(kv[fl]) if fl else endash(str(kv[fl]))
    kargv = [enflag(keyvals[i//2],i%2) for i in all_tokens]
    return ['main'] + list(map(str,args)) + kargv
