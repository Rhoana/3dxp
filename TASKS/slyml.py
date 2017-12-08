# -*- coding: utf-8 -*-
from itertools import groupby
from threading import Thread
import subprocess
import argparse
import termios
import getpass
import string
import signal
import psutil
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

class FormatError(KeyError):
    pass

class EvalError(Exception):
    pass

class QueueError(Exception):
    pass

class ScriptError(Exception):
    pass

def log_quiet(msg, quiet=False):
    if not quiet:
        print(msg)

def safe_yaml(y):
    if isinstance(y, dict):
        return {str(k):safe_yaml(y[k]) for k in y}
    if isinstance(y, (list, tuple, set)):
        return [safe_yaml(v) for v in y]
    if isinstance(y, type):
        return repr(y)
    return y

def log_yaml(i, y, quiet=False):
    pretty = {
        'default_flow_style': False,
    }
    out = {str(i):safe_yaml(y)}
    y_str = yaml.safe_dump(out, **pretty)
    log_quiet(y_str.rstrip('\n'), quiet)

def logEvalError(task_id, e, quiet=False):
    code, name, err = e.args
    log_yaml('Evaluation Error', {
        type(err).__name__: str(err),
        '{} in {}'.format(name, task_id): code,
    }, quiet)

def logFormatError(joining, e, quiet=False):
    source, target = joining
    key, fmt, name, source_keys = e.args
    log_yaml('Formatting Error', {
        '{} have'.format(source): source_keys,
        '{} needs'.format(target): key,
        name: fmt,
    }, quiet)

def seems_like_path(s):
    return s[:1] in ['.', '/', '~']

def run_subprocess(command):
    return subprocess.check_output(command, stderr=subprocess.STDOUT)

def change_root(root):
    # Allow root as path literal
    if not root or os.path.isdir(root):
        return root
    # Try bash script
    try:
        return run_subprocess(root.split(' ')).rstrip()
    except subprocess.CalledProcessError as e:
        raise EvalError(root, 'Workdir', e)
    except IOError as e:
        raise EvalError(root, 'Workdir', e)
    except Exception as e:
        raise EvalError(root, 'Workdir', e)

def fmt_path(path, root=''):
    user_path = os.path.expanduser(path)
    root_path = os.path.join(root, user_path)
    return os.path.abspath(root_path)

def join_no_overwrite(parent, child):
    # Copy all from parent
    result = copy.deepcopy(parent)
    for k,v in child.items():
        result[k] = result.get(k,v)
    # Values from child if not in parent
    return result

def join_fmt_overwrite(root, parent, child):
    # Copy all from parent
    result = copy.deepcopy(parent)
    # Format all strings in child
    for k,v in child.items():
        # Add value
        result[k] = v
        if not isinstance(v, six.string_types):
            continue
        # Format strings from parent
        try:
            result[k] = v.format(**parent)
        except KeyError as e:
            fmt_args = [v, k, list(parent.keys())]
            raise FormatError(e.args[0], *fmt_args)
        # Unpack path if looks like a path
        if seems_like_path(result[k]):
            result[k] = fmt_path(result[k], root)
    # Values from child formatted by parent
    return result

def get_typer(task, k=None, d=None):
    typer = type(d)
    if d is None:
        types = task['Slyml']['TYPE']
        typer = types.get(k, str)
    return typer

def eval_key(task, k, d=None):
    typer = get_typer(task, k, d)
    if d is None:
        d = typer()
    try:
        v = task.get(k, d)
        if isinstance(v, six.string_types):
            if k == 'Workdir':
                v = change_root(v)
                return v
            v = eval(v)
        return typer(v)
    except ValueError as e:
        raise EvalError(v, k, e)
    except SyntaxError as e:
        raise EvalError(v, k, e)
    except Exception as e:
        raise EvalError(v, k, e)

def check_evals(task):
    evals = task.get('Evals') or []
    for k in evals:
        eval_key(task, k)

def is_debug(task):
    # Watching always debugging
    if task['Slyml']['WATCH-KEY']:
        return True
    return get_safe(task, 'Debug')

def is_quiet(task):
    # Watching always quiet
    if task['Slyml']['WATCH-KEY']:
        return True
    return get_safe(task, 'Quiet')

def is_bash(task):
    return get_safe(task, 'Bash')

def get_safe(task, k, d=None):
    # Handle python evaluation
    evals = task.get('Evals') or []
    typer = get_typer(task, k, d)
    quiet = d is not None
    if not quiet:
        d = typer()
    if k not in evals:
        v = task.get(k,d)
        return typer(v)
    # Evaluate as a given type
    try:
        return eval_key(task, k, d)
    except EvalError as e:
        logEvalError(get_unique(task), e, quiet)
    return d 

def get_watch_log(task, _i=0):
    w_list = []
    w_cmd = ['tail']
    log_list = ['out', 'err']
    log_max = len(log_list)
    # Get logfile indices
    arr_i, log_i = divmod(_i, log_max)
    run_max = get_safe(task, 'Runs')
    arr_i = arr_i % run_max
    # Get log files for array index
    log_v = get_log_var(task, arr_i)
    log_ext = log_list[log_i]
    # Get command for specific file
    w_cmd.append(log_v[log_ext])
    w_dir = log_v['dir']
    # Get the full number of logs
    full_max = log_max * run_max
    return w_dir, w_cmd, full_max

def get_watch_job(task, _i=0):
    squeue = './squeue'
    w_dir = '/usr/bin'
    if not os.path.exists(w_dir):
        squeue = 'squeue'
        w_dir = ''
    job_n = '--name='+get_uniq(task)
    job_u = '--user='+getpass.getuser()
    # Get constant part of command
    w_cmd = [squeue, job_n, job_u]
    # Get differently formatted outputs
    job_list =  [
        [
            '-o', '"%8j %6K %M %t %r"',
        ],
        [
            '-o', '"%8j %16S %N %k"',
            '-t', 'all', '--sort=-S,p',
        ],
    ]
    job_max = len(job_list)
    # Get a command of a given format
    w_cmd += job_list[_i % job_max]
    return w_dir, w_cmd, job_max

def get_watch(_task, _i=0):
    w_k = _task['Slyml']['WATCH-KEY']
    if w_k == 'LOG':
        return get_watch_log(_task, _i)
    if w_k == 'JOB':
        return get_watch_job(_task, _i)
    return '', []

def get_watch_flags(_dir, _task, _i=0):
    in_tmp = get_logs(_task, 'in.tmp', _i) 
    out_tmp = get_logs(_task, 'out.tmp', _i) 
    # Handle input files
    watch_flags = {
        'stdout': open(out_tmp, 'a+', 0),
        'stdin': open(in_tmp, 'w+', 0),
        'cwd': _dir,
    }
    if not _dir:
        del watch_flags['cwd']
    return watch_flags

def index_proc(*_args):
    _dir, _cmd, _max = get_watch(*_args)
    w_cmd = ['watch', '-n', '1'] + _cmd
    w_flags = get_watch_flags(_dir, *_args)
    return w_cmd, w_flags, _max

def start_proc(w_cmd, w_flags):
    w_proc = psutil.Popen(w_cmd, **w_flags)
    w_in = w_flags['stdin']
    w_out = w_flags['stdout']
    return w_proc, w_in, w_out

def watch_proc(_p, _in, _out):
    ti = 0.1
    pause_set = {'stopped'}
    short_name = os.path.basename(_out.name)
    killer = lambda x: psutil.wait_procs([x], ti)[0]
    pauser = lambda x: x.status() in pause_set
    for _ in iter(_p.is_running, False):
        was_paused = pauser(_p)
        # Killed or paused
        if killer(_p):
            break
        if not psutil.pid_exists(_p.pid):
            break
        if not os.path.exists(_out.name):
            break
        if pauser(_p):
            continue
        if was_paused:
            _out.write('\r')
        # Read the watched file
        with open(_out.name, 'r') as read_out:
            for c in read_out.read():
                sys.stdout.write(c)
                sys.stdout.flush()
    # Delete temp files
    for _f in [_in, _out]:
        _f.close()
        try:
            os.remove(_f.name)
        except OSError:
            pass
    sys.stdout.flush()

def watch_user():
    with raw_in(sys.stdin):
        reader = lambda: sys.stdin.read(1)
        for key in iter(reader, chr(27)):
            if 'q' in key:
                return []
        if '[' not in reader():
            return []
        # Arrow keys
        return {
            'A': (1, 0),
            'B': (-1, 0),
            'C': (0, 1),
            'D': (0, -1),
        }.get(reader(), (0,0))

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

def get_proc(_task, _ba, o_ij, cache={}, loc=(0,0)):
    # Interpret all indices
    t_i, i_min, i_max = index_task(_task, _ba, o_ij[0])
    _cmd, _flags, j_max = index_proc(t_i, o_ij[1])
    o_clamp = [
        [i_min, i_max],
        [0, j_max],
    ]
    # Get existing process
    if loc in cache:
        o_proc = cache.get(loc)
        return o_proc, o_clamp
    # Make a new process
    o_proc, o_in, o_out = start_proc(_cmd, _flags)
    cache[loc] = o_proc
    # Stream output of task
    Thread(**{
        'target': watch_proc,
        'args': (o_proc, o_in, o_out),
    }).start()
    o_proc.suspend()
    return o_proc, o_clamp

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

def read_in(_task, _ba, o_ij=(0,0), cache={}):
    o_proc, c_ij = get_proc(_task, _ba, o_ij, cache)
    os.system('stty sane')
    o_proc.resume()
    def sys_kill(*_):
        for k in cache:
            p = cache.get(k)
            p.kill()
        raise KeyboardInterrupt()
    signal.signal(signal.SIGINT, sys_kill)
    # Respond to standard input
    delta = watch_user()
    if delta:
        o_proc.suspend()
        # Update if any change
        n_ij = update_proc(cache, delta, o_ij, c_ij)
        # Change watched command
        read_in(_task, _ba, n_ij, cache=cache)
    # Done
    sys_kill()

def run_watch(_task, *args):
    watch_t = _task['Slyml']['WATCH']
    if watch_t == get_out(_task, 'NAME'):
        # Read user input
        try:
            read_in(_task, args)
        except KeyboardInterrupt:
            os.system('stty sane')

def get_entry_path(task):
     keys = [
         task['Slyml']['FILE'][:3],
         task['Slyml']['ENTRY'][:4],
     ]
     return [k for k in keys if k != 'Main']

def get_unique(task, full=True):
    task_ids = task['Slyml']['ID']
    entry_path = get_entry_path(task) 
    human_ids = [] 
    def to_word(n):
        abc = string.ascii_uppercase
        (d, m) = divmod(n, len(abc))
        return (to_word(d).lower() if d else '') + abc[m]
    # Count any repetitions
    if full: 
        for v,g in groupby(task_ids):
            count = sum(1 for _ in (g)) - 1
            pre = 1 + count if count else ''
            human_ids.append(str(pre) + to_word(v))
    # Return full path or only entry
    return os.sep.join(human_ids + entry_path)

def join_uniq(root, *args):
    name = ''.join(args)
    return os.sep.join([root, name])

def shorten_uniq(task_id, keys):
    s = -len(keys)
    a = task_id.split(os.sep)
    return join_uniq(''.join(a[:s]), *a[s:])

def get_uniq(task):
    unique = get_unique(task)
    t_path = get_entry_path(task)
    return shorten_uniq(unique, t_path)

def get_log_name(_id, _ext, _arr):
    log_name = '{}.{}'.format(_arr, _ext)
    return os.path.join(_id, log_name)

def get_log_var(task, arr):
    log_id = get_unique(task)
    entry_id = get_unique(task, 0)
    root = get_safe(task, 'Workdir')
    log_dir = fmt_path(get_safe(task, 'Logs'), root)
    return {
        'dir': log_dir,
        'out': get_log_name(log_id, 'out', arr),
        'err': get_log_name(log_id, 'err', arr), 
        'in.tmp': get_log_name(log_id, 'in.tmp', arr), 
        'out.tmp': get_log_name(log_id, 'out.tmp', arr), 
        'yml': get_log_name(entry_id, 'yml', arr), 
    }

def get_logs(task, ext='out', arr='%a'):
    # Return one full log path
    log_v = get_log_var(task, arr)
    log_file = os.path.join(log_v['dir'], log_v[ext])
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_file

def get_deps(task, before, debug=False):
    name = ['NAME','OUT'][not debug]
    deps = [get_out(b, name) for b in before]
    out_fmt = 'afterok:{}'
    out = [d for d in deps if d.isdigit()]
    if debug:
        s_file = get_safe(task, 'Slurm')
        s_base = os.path.basename(s_file)
        s_name = s_base.split('.')[0]
        out_fmt = s_name + ': {}'
        out = [d.split('/')[0] for d in deps]
    if not out:
        return ''
    # Return dependencies
    return out_fmt.format(':'.join(out))

def get_flags(task):
    all_out = {}
    for k in get_safe(task,'Flags'):
        v = get_safe(task,k,'')
        if v:
            all_out[k] = v
    return all_out

def get_exports(task):
    all_out = {}
    for k in get_safe(task,'Exports'):
        v = get_safe(task,k,'')
        if v:
            all_out[k] = v
    return all_out

def set_exports(task):
    exports = get_exports(task)
    # Export all environment variables
    for k,v in exports.items():
        os.environ[k] = v
    return "ALL"

def get_array(task):
    output = {}
    default = 1
    for k in ['Runs', 'Sync']:
        val = get_safe(task,k,default)
        output[k] = val
        default = val
    # Concurrent and Total Array Jobs
    sync = output['Sync']
    runs = max(0, output['Runs'] - 1)
    return "0-{}%{}".format(runs, sync)

def get_bash(task):
    output = ['bash']
    set_exports(task)
    output.append(get_safe(task,"Slurm"))
    return output

def parse_opt(k, v):
    if not str(v):
        return []
    if k in {'comment'}:
        v = '"{}"'.format(v)
    if len(str(k)) > 1:
        return ['--{}={}'.format(k,v)]
    return ['-'+k, v]

def get_slurm(task, before):
    out = ['sbatch']
    debug = is_debug(task)
    arrays = get_array(task)
    # Get debug dependencies for comments
    message = get_deps(task, before, True)
    real_deps = get_deps(task, before, debug)
    default_list = [
        ['job-name', get_uniq(task)],
        ['output', get_logs(task, 'out')],
        ['error', get_logs(task, 'err')],
        ['dependency', real_deps],
        ['comment', message],
        ['workdir', get_safe(task,'Workdir')],
        ['export', set_exports(task)],
        ['array', arrays],
    ]
    user_opt = get_flags(task)
    main_opt = dict(default_list)
    main_keys = [o[0] for o in default_list]
    opt = join_no_overwrite(user_opt, main_opt)

    key_set = set(user_opt.keys())
    user_keys = list(key_set - set(main_keys))
    # Get user-provided opts and standard opts
    for k in main_keys + user_keys:
        out += parse_opt(k, opt[k])
    # Return the full sbatch arguments
    out.append(get_safe(task,"Slurm"))
    return list(filter(bool, out))

def run_bash(bash_job, task):
    try:
        submitted = run_subprocess(bash_job)
        log_yaml('Ran', job_meta(task), is_quiet(task))
    except subprocess.CalledProcessError as e:
        raise ScriptError(e.output.rstrip())
    bash_log = get_logs(task, 'out', 0)
    with open(bash_log, 'w') as f:
        f.write(submitted)
    return 'BASH'

def run_slurm(slurm_job, task):
    submitted = 'ERROR'
    # Submit and collect the job id
    try:
        submitted = run_subprocess(slurm_job)
        log_yaml('Queued', job_meta(task), is_quiet(task))
    except subprocess.CalledProcessError as e:
        raise ScriptError(e.output.rstrip())
    # Return the id number identifying the job
    str_out = submitted.rstrip().split(' ')
    str_digits = (s for s in str_out if s.isdigit())
    try:
        return next(str_digits)
    except StopIteration:
        raise QueueError()

def run_script(job, task):
    runners = {
        'sbatch': run_slurm,
        'bash': run_bash,
    }
    runner = runners.get(job[0], run_bash)
    return runner(job, task)

def job_meta(task, full_command='', quiet=False):
    slurm_name = get_safe(task,'Slurm')
    needs_list = get_safe(task,"Needs")
    for_list = get_safe(task,"For")
    if not slurm_name:
        if any([needs_list, for_list]):
            return {}
        # Warn user
        w_fmt = "Empty {} Needs none, For none"
        warning =  w_fmt.format(get_unique(task)),
        log_yaml('Warning', warning, quiet)
    output = {
        "Slurm": os.path.basename(slurm_name)
    }
    if quiet:
        return output["Slurm"]
    # Show the exports for the task
    output['Exports'] = get_exports(task)
    # Return full command line arguments
    if full_command:
        output['Command'] = full_command
    return output

def log_default(parent, child):
    if is_quiet(child) or not is_debug(child):
        return
    for n in ['Constants', 'Inputs']:
        child_n = get_safe(child, n)
        parent_n = get_safe(parent, n)
        log_diff(parent_n, child_n, n)

def log_diff(old_m, new_m, name):
    new_k = set(new_m.keys())
    old_k = set(old_m.keys())
    # Record all adedd keys
    add_m = {k:new_m[k] for k in new_k - old_k}
    # Record all changed keys
    is_same = lambda k: old_m[k] != new_m[k]
    same_k = iter(filter(is_same, new_k & old_k))
    change_m = {k: [old_m[k], new_m[k]] for k in same_k}
    if add_m:
        log_yaml('Added '+name, add_m)
    if change_m:
        log_yaml('Updated '+name, change_m)

def start_tree(_id):
    return '{}\\'.format(_id)

def end_tree(_id):
    id_dots = '.'*len(_id)
    return """{}/
{}""".format(_id, id_dots) 

def flatten(*args):
    def flat_1(a):
        if isinstance(a, (tuple, list)):
            return flatten(*a)
        return (a,)
    return (val for a in args for val in flat_1(a))

def match_any(_tasks, _bad={'ERROR'}):
    in_bad = lambda t: get_out(t, 'OUT') in _bad
    return any(filter(in_bad, _tasks))

def match_all(_tasks, _bad={'ERROR'}):
    in_bad = lambda t: get_out(t, 'OUT') in _bad
    return all(filter(in_bad, _tasks))

# Run all jobs we need
def do_before(_default, _needs):
    before = []
    # Run all jobs we need
    for nid, n in enumerate(_needs):
        before += run_task(_default, n, nid)
    return before

def do_after(_tasks, _default, _before, _for):
    after = []
    # Run all jobs needing us
    for fi, f in enumerate(_for):
        fid = len(_before) + fi
        after += run_task(_default, f, fid, _tasks)
    return after

def get_out(_task, _k=None):
    results = {
        'ID': get_unique(_task),
        'NAME': get_uniq(_task),
        'OUT': _task['Slyml']['OUT'],
        'RUNS': get_safe(_task, 'Runs', 1),
    }
    if not _k:
        return results
    return results.get(_k, None)

def set_out(_task, _out='ERROR'):
    _task['Slyml']['OUT'] = _out

def end_task(_task, _before=[], _after=[]):
    # Stop to watch if asked
    _quiet = is_quiet(_task)
    t_out = get_out(_task)
    # Log all dependencies
    name_fmt = '{RUNS}x {NAME}'.format
    if _before:
        t_msg = t_out['NAME']+' Needs'
        b_o = iter(map(get_out, _before))
        b_n = [name_fmt(**o) for o in b_o]
        log_yaml(t_msg, b_n, _quiet)
    if _after:
        t_msg = t_out['NAME']+' For'
        a_o = iter(map(get_out, _after))
        a_n = [name_fmt(**o) for o in a_o]
        log_yaml(t_msg, a_n, _quiet)
    # End current node
    if not _quiet:
        print(end_tree(t_out['ID']))
    # Stop to watch if needed
    run_watch(_task, _before, _after)
    return [_task]

def start_task(__default, __task, __i):
    # Take defaults for task
    _default = copy.deepcopy(__default)
    _task = join_no_overwrite(__task, __default)
    # Define internal ID for this task
    _default['Slyml']['ID'] +=  (__i,)
    _task['Slyml'] = _default['Slyml']
    # Set Special keys from default
    d_keys = ['Debug', 'Quiet', 'Bash']
    for dk in d_keys:
        _task[dk] = get_safe(_task, dk, _default[dk])

    # Log start of task
    if not is_quiet(_task):
        print(start_tree(get_unique(_task)))
    return _default, _task

def run_task(__default, __task, __i=0, __before=[]):
    # Copy task and default
    _default, _task = start_task(__default, __task, __i)
    # Static special values
    debug = is_debug(_task)
    quiet = is_quiet(_task)
    task_id = get_unique(_task)
    # Modifiable special values
    _for = get_safe(_task,'For')
    _needs = get_safe(_task,'Needs')
    _inputs = get_safe(_task,'Inputs')
    _constants = get_safe(_task,'Constants')
    # Try to get working directory
    root = get_safe(_task, 'Workdir')
    dI = get_safe(_default, 'Inputs')
    dC = get_safe(_default, 'Constants')
    # Take unset constants and inputs from default
    _constants = join_no_overwrite(_constants, dC)
    _inputs = join_no_overwrite(_inputs, dI)
    # Update default for dependencies
    default = copy.deepcopy(_default)
    default['Constants'] = _constants
    default['Inputs'] = _inputs
    # Log changes to defaults
    log_default(_default, default)

    ####
    # Constants join and format inputs,
    # Inputs join and format task
    ####
    try:
        joining = ['Constants', 'Inputs']
        inputs = join_fmt_overwrite(root, _constants, _inputs)
        joining = ['Inputs', task_id]
        task = join_fmt_overwrite(root, inputs, _task)
    except FormatError as e:
        logFormatError(joining, e)
        return end_task(_task)

    # Allow math on parameters
    try:
        check_evals(task)
    except EvalError as e:
        logEvalError(task_id, e)
        return end_task(task)

    # Error details for task
    task_err_msg = job_meta(task)

    # All unscheduled dependencies
    all_needs = list(flatten(_needs))
    all_for = list(flatten(_for))

    # All scheduled needed jobs
    before = __before + do_before(default, all_needs)
    for_args = [default, before, all_for]

    if match_any(before):
        log_yaml('Error- unmet needs', task_err_msg)
        return end_task(task)

    if not get_safe(task,'Slurm'):
        # All tasks after need all tasks before
        after = do_after(before, *for_args)
        end_task(task, before, after)
        return before

    if is_bash(task):
        # No slurm dependency
        if not match_all(before, {'BASH', 'DEBUG'}):
            err_msg = 'Error- bash after slurm'
            log_yaml(err_msg, task_err_msg)
            return end_task(task)
        job_process = get_bash(task)
    else:
        # Create the slurm command
        job_process = get_slurm(task, before)

    if debug:
        task_debug = job_meta(task, job_process, quiet)
        log_yaml(task_id, task_debug)
        set_out(task, 'DEBUG')
        after = do_after([task], *for_args)
        return end_task(task, before, after)

    #####
    # Run or schedule the job
    ####
    try:
        job_id = run_script(job_process, task)
    except QueueError:
        log_yaml('Error queuing', task_err_msg)
        return end_task(task)
    except ScriptError as e:
        log_yaml('Error', e.args[0])
        return end_task(task)

    # Run the dependent jobs and return
    set_out(task, job_id)
    after = do_after([task], *for_args)
    return end_task(task, before, after)

if __name__ == "__main__":

    help = {
        'slyml': """Schedule slurm jobs from yaml.
    Dependencies: Python 2 (>=2.6) and slurm (>=14.11)
        """,
        'quiet': 'Show output only if error',
        'debug': 'Do not actually schedule jobs',
        'entry': 'Parse entry in yaml (default Main)',
        'bash': 'Use bash, no arrays or dependencies',
        'log': 'After queueing, watch *.out for given job',
        'job': 'After queueing, watch squeue for given job',
        'yaml': """A/path/to/file.yaml with optional keys...
    Main:
        Constants:
            A: ./EXAMPLE/0
            N: 42
            ...
        Inputs:
            B: "{A}/FORMAT/STRING"
            C: "NUMBER LIKE {N}"
            ...
        Needs:
            - Constants: {...}
              Needs: [ ... ]
              For: [ ... ]
              ...
            - Constants: {...}
              ...
            - ...
        For:
            - Constants: {...}
              Needs: [ ... ]
              For: [ ... ]
              ...
            - ...
        Flags: [mem, ... ]
        Exports: [x, y, ... ]
        x: "{A}/overwrites_default.py"
        y: "--new option"
        mem: 9000
        Runs: "{N}"
        ...
     Default:
        Evals: [Runs, Sync]
        Exports: []
        Flags: []
        Constants: {}
        Inputs: {}
        Workdir: "A/path/to/file.yaml"
        Logs: "./LOGS"
        Slurm: ""
        Quiet: false
        Debug: false
        Runs: "1"
        Sync: "1"
        """,
    }
    # Most important
    main_entry = {}

    parser = argparse.ArgumentParser(**{
        'description': help['slyml'],
        'formatter_class': argparse.RawTextHelpFormatter,
    })
    parser.add_argument('yaml', help=help['yaml'])
    parser.add_argument('entry', **{
        "help": help['entry'],
        "default": "Main",
        "nargs": "?",
    })
    parser.add_argument('-d', '--debug', **{
        "help": help['debug'],
        "action": 'store_true',
        "default": False,
    })
    parser.add_argument('-q', '--quiet', **{
        "help": help['quiet'],
        "action": 'store_true',
        "default": False,
    })
    parser.add_argument('-b', '--bash', **{
        "help": help['bash'],
        "action": 'store_true',
        "default": False,
    })
    parser.add_argument('-l', '--log', **{
        "help": help['log'],
        "const": 'A',
        "nargs": '?',
    })
    parser.add_argument('-j', '--job', **{
        "help": help['job'],
        "const": 'A',
        "nargs": '?',
    })
    cmd = parser.parse_args()
    cmd = parser.parse_args()
    # Expand the input yaml path
    yml_path = fmt_path(cmd.yaml)

    main_key = cmd.entry
    main_entry = {}
    yml_keys = []
    try:
        with open(yml_path, 'r') as yf:
            yml = yaml.load(yf)
            yml_keys = list(yml.keys())
            main_entry = yml[main_key]
    except yaml.parser.ParserError as e:
        log_yaml(type(e).__name__, yml_path)
        sys.exit(' STOP: Invalid YAML')
    except (AttributeError, KeyError, TypeError)as e:
        log_yaml('Missing "{}" key'.format(main_key), {
            'keys': yml_keys,
            'yaml': yml_path,
        })
    except IOError as e:
        log_yaml('IOError', e.strerror)

    # Require the Main entry
    if not main_entry:
        sys.exit(' STOP: no "{}" entry'.format(main_key))

    # Get any default values
    _default = yml.get('Default', {})
    # Favor watching logs over watching jobs
    watch_cmd = iter(filter(all, [
        ['JOB', cmd.job],
        ['LOG', cmd.log],
    ]))
    w_k, w_v = next(watch_cmd, ('',''))
    yml_base = os.path.basename(yml_path)
    _default['Slyml'] = {
        'FILE': yml_base.split('.')[0],
        'ENTRY': main_key,
        'WATCH-KEY': w_k,
        'ID': tuple(),
        'OUT': 'ERROR',
    }
    d_path = get_entry_path(_default)
    w_v = w_v.replace(os.sep, '')
    w_v = join_uniq(w_v, *d_path)
    _default['Slyml']['WATCH'] = w_v
    _default['Slyml']['TYPE'] = {
        'Constants': dict,
        'Inputs': dict,
        'Exports': list,
        'Flags': list,
        'Needs': list,
        'For': list,
        'Runs': int,
        'Sync': int,
        'Quiet': bool,
        'Debug': bool,
        'Bash': bool,
    }
    # Users overwrite per task
    _default['Needs'] = []
    _default['For'] = []
    # Overwrite by default or per task
    _empty = {
        'Workdir': os.path.dirname(yml_path),
        'Evals': ['Workdir','Runs','Sync'],
        'Slyml': _default['Slyml'],
        'Quiet': cmd.quiet,
        'Debug': cmd.debug,
        'Bash': cmd.bash,
        'Logs': 'LOGS',
        'Runs': 1,
    }
    default = join_no_overwrite(_default, _empty)
    log_default(_empty, default)
    quiet_d = is_quiet(default)
    debug_d = is_debug(default)

    # Begin the scheduling
    before = run_task(default, main_entry)
    # Sumarize results
    happenings = [
        ['SUCCESS', 'Scheduled'],
        ['NO BUGS', 'Parsed'],
    ]
    what_happened = happenings[debug_d]
    # If any job went to bash
    if match_any(before, {'BASH'}):
        what_happened[1] = 'Ran (or Scheduled)'    
    # Typical success message
    msg = """\
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
 {0}: {1} all jobs.
______________________________
        """.format(*what_happened)
    # If any job could not happen
    if match_any(before):
        msg = """\
|||||||||||||||||||||||||||||||
 ERROR: some jobs had issues.
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
        """
    if quiet_d:
        msg = msg.split('\n')[1]
    print(msg)
