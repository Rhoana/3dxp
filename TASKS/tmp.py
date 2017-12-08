# -*- coding: utf-8 -*-
from fcntl import fcntl, F_GETFL, F_SETFL
from itertools import groupby
from threading import Thread
from threading import current_thread
from pydoc import pipepager
import subprocess
import argparse
import tempfile
import termios
import getpass
import string
import signal
import psutil
import time
import copy
import yaml
import sys
import six
import tty
import os

# http://ballingt.com/nonblocking-stdin-in-python-3/
class raw_in(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

def get_watch_log(task, _i=0):
    w_list = []
    w_cmd = ['cat']
    n_max = task['n']
    arr_i = _i % n_max
    # Get log files for array index
    fmt_name = '{}_{}.tmp'.format
    log_name = fmt_name(task['id'], arr_i)
    log_file = os.path.join(task['dir'], log_name)
    # Get command for specific file
    w_cmd.append(log_file)
    # Get the full number of logs
    return '', w_cmd, n_max

def index_proc(_task, _i):
    _dir, _cmd, _max = get_watch_log(_task, _i)
    # Set up watch subproccess
    w_flags = {}
    if _dir:
        w_flags['cwd'] = _dir
    w_cmd = ['python', 'watchall.py'] + _cmd
#    w_cmd = ['watch'] + _cmd
    return w_cmd, w_flags, _max

def start_proc(proc_args):
    w_cmd = proc_args['cmd']
    w_flags = proc_args['flags']
    return psutil.Popen(w_cmd, **w_flags)

def watch_user():
    with raw_in(sys.stdin):
        ESC = chr(27)
        in_reader = lambda: sys.stdin.read(1)
        for key in iter(in_reader, ESC):
            if key == 'q':
                return False
            if key in '.>':
                return (+1, 0)
            if key in ',<':
                return (-1, 0)
        key_1 = in_reader()
        if '[' not in key_1:
            return (0,0)
        key_2 = in_reader()
        # Arrow keys
        return {
            'C': (0, +1),
            'D': (0, -1),
        }.get(key_2, (0,0))

def cycle_rel(v, min, max):
    return (v - min) % (max - min) + min

def index_task(_task, _ba, _i):
    before, after = _ba
    i_min = -len(before)
    i_max = 1 + len(after)
    i = cycle_rel(_i, i_min, i_max)
    # Get task from bounded j index
    tasks = before + [_task] + after
    return tasks[i - i_min], i_min, i_max

def get_edge(_idx, _k, _p, _n):
    ndim = len(_k)
    get_kp = lambda i: [_k, _p][i is _idx][i]
    get_kn = lambda i: [_k, _n][i is _idx][i]
    get_ko = lambda i: 0 if i is _idx else _k[i]
    kp = tuple(map(get_kp, range(ndim)))
    kn = tuple(map(get_kn, range(ndim)))
    ko = tuple(map(get_ko, range(ndim)))
    return ko,kn,kp

def index_cache(k_rel, o_ij, c_ij, n=1):
    k_i_c = list(zip(k_rel, o_ij, c_ij))
    return tuple(cycle_rel(i+n*k, *c) for k,i,c in k_i_c)

def add_delta(*args):
    return tuple(map(sum, zip(*args)))

def see_cache(dn, args):
    rn = 2*dn + 1
    vi = args[-1][0]
    vj = args[-1][1]
    di = vi[1]-vi[0]
    dj = vj[1]-vj[0]
    ij_viz = ((' '+'.'*dj)*di)[1:]
    rel_viz = ((' '+'.'*rn)*rn)[1:]
    viz = {
        'ij': list(map(list, ij_viz.split(' '))),
        'rel': list(map(list, rel_viz.split(' '))),
    }
    def add_viz(sym, k_rel, _i, _j):
        viz['ij'][_i-vi[0]][_j-vj[0]] = sym
        viz['rel'][k_rel[0]+dn][k_rel[1]+dn] = sym
    def show_viz(k):
        k_viz = viz.get(k, 'ij')[::-1]
        k_str = '\n'.join(map(''.join, k_viz))
        sys.stdout.write('\n' + k_str + '\r\n')
        sys.stdout.flush()
    # Convenient logging functions
    return add_viz, show_viz

def delete_proc(p_proc):
    p_proc.kill()
    psutil.wait_procs([p_proc])

def delete_cache(cache, k):
    if k not in cache:
        return False
    p_proc = cache.pop(k)
    delete_proc(p_proc)
    return True

def update_proc(cache, *args):
    n_c = 4
    shift_sym = '.'
    n_rel, o_ij, c_ij = args
    ndim = len(o_ij)
    # Clamp new indices
    p_ij = index_cache(*args, n=-1) 
    n_ij = index_cache(*args, n=1)
    no_ij = zip(n_ij, o_ij)
    # Absolute change
    n_abs = tuple(n-o for n,o in no_ij)
    n_new = list(filter(None, n_abs))
    # Ensure exactly one index changed
    if len(n_new) is not 1:
        return o_ij
    # Which index changed?
    idx = n_abs.index(n_new[0])
    n_sign = 1 if n_rel[idx] > 0 else -1
    add_viz, see_viz = see_cache(n_c, args)
    # Filter cache keys
    p_rel = tuple(-n for n in n_rel)
    in_bound = lambda k: abs(k[idx]) <= n_c
    get_idx = lambda k: k[idx]*n_sign
    # Get orignal values
    input_k = sorted(cache.keys(), key=get_idx)
    for ko_rel in input_k:
        kn_rel = add_delta(ko_rel, n_rel)
        kp_rel = add_delta(ko_rel, p_rel)
        ko_ij = index_cache(ko_rel, o_ij, c_ij)
        kn_ij = index_cache(kn_rel, o_ij, c_ij)
        kp_ij = index_cache(kp_rel, o_ij, c_ij)
        sym = shift_sym if any(ko_rel) else '@'
        ko_proc = cache.pop(ko_rel)
        shift_rel = kp_rel
        # Loop to next
        if kp_ij == kn_ij:
            shift_rel = kn_rel
        # Uncache if too far
        if not in_bound(shift_rel):
            add_viz('x', ko_rel, *ko_ij)
            delete_proc(ko_proc)
            continue
        # Shift proc to new slot
        add_viz(sym, ko_rel, *ko_ij)
        delete_cache(cache, shift_rel)
        cache[shift_rel] = ko_proc
    # Visualize options
    see_viz('ij')
    # Return next values
    return n_ij

def prep_proc(_task, _ba, o_ij):
    # Interpret all indices
    t_i, i_min, i_max = index_task(_task, _ba, o_ij[0])
    _cmd, _flags, j_max = index_proc(t_i, o_ij[1])
    proc_args = {
        'cmd': _cmd,
        'flags': _flags,
    }
    clamp = [
        [i_min, i_max],
        [0, j_max],
    ]
    return proc_args, clamp

def get_proc(proc_args, state, loc=(0,0)):
    cache = state['cache']
    # Get existing process
    if loc in cache:
        return cache.get(loc)
    # Make a new process
    o_proc = start_proc(proc_args)
    cache[loc] = o_proc
    # Pause new task
    o_proc.suspend()
    return o_proc

def read_in(_task, _ba, o_ij=(0,0), state={}):
    state = state or {
        'scroll': {},
        'cache': {},
    }
    # Get command parameters and bounds
    proc_args, c_ij = prep_proc(_task, _ba, o_ij)
    o_proc = get_proc(proc_args, state)
    o_proc.resume()
    def sys_kill(*_):
        for k in state['cache'].keys():
            delete_cache(state['cache'], k)
        os.system('reset')
        raise KeyboardInterrupt()
    signal.signal(signal.SIGINT, sys_kill)
    # Respond to standard input
    for delta in iter(watch_user, False):
        if not delta:
            break
        o_proc.suspend()
        # Change watched command
        n_ij = update_proc(state['cache'], delta, o_ij, c_ij)
        return read_in(_task, _ba, n_ij, state)
    # Exit
    sys_kill()

def tmp_task(id):
    return {
        'dir': 'tmp',
        'id': id,
        'n': 3,
    }

task = tmp_task('B')
after = [tmp_task('C')]
before = [tmp_task('A')]

read_in(task, [before, after])

