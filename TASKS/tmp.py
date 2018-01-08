# -*- coding: utf-8 -*-
from fcntl import fcntl, F_GETFL, F_SETFL
from itertools import groupby
from threading import Thread
from threading import current_thread
from pydoc import pipepager
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
    return w_cmd, w_flags, _max

def start_proc(proc_args):
    w_cmd = proc_args['cmd']
    w_flags = proc_args['flags']
    # Debug
    #w_flags['stdout'] = -1
    return psutil.Popen(w_cmd, **w_flags)

def watch_user():
    with raw_in(sys.stdin):
        in_reader = lambda: sys.stdin.read(1)
        for key in iter(in_reader, 'q'):
            if key in '.>':
                return (+1, 0)
            if key in ',<':
                return (-1, 0)
            if key in '-_':
                return (0, -1)
            if key in '=+':
                return (0, +1)
        return False

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
    def add_viz(symbols, k_rel, _i, _j):
        sym = symbols[any(k_rel)]
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

def update_proc(state, *args):
    n_rel, o_ij, c_ij = args
    ndim = len(o_ij)
    n_c = 4
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
    # Make a new state
    cache = state.pop('cache')
    state['cache'] = {}
    # Which index changed?
    idx = n_abs.index(n_new[0])
    add_viz, see_viz = see_cache(n_c, args)
    # Filter cache keys
    in_bound = lambda k: abs(k[idx]) <= n_c
    for o_to_k, k_proc in cache.items():
        # Where is the process in ij indices?
        k_ij = index_cache(o_to_k, o_ij, c_ij, n=1)
        # How far is the process from to next ij?
        n_to_k = tuple(k-n for n,k in zip(n_ij, k_ij))
        # Delete if too far away
        if not in_bound(n_to_k):
            add_viz('xx', o_to_k, *k_ij)
            delete_proc(k_proc)
            continue
        # Delete if redundant
        if n_to_k in state['cache']:
            add_viz('@+', o_to_k, *k_ij)
            delete_proc(k_proc)
            continue
        # Shift process to new slot
        add_viz('@+', o_to_k, *k_ij)
        state['cache'][n_to_k] = k_proc
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
        n_ij = update_proc(state, delta, o_ij, c_ij)
        return read_in(_task, _ba, n_ij, state)
    # Exit
    sys_kill()

def tmp_task(id):
    return {
        'dir': 'tmp',
        'id': id,
        'n': 3,
    }

A,B,C = "ABC"

task = tmp_task(B)
after = [tmp_task(C)]
before = [tmp_task(A)]

read_in(task, [before, after])

