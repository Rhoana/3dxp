import subprocess
import argparse
import copy
import yaml
import sys
import six
import os

ID_START = int('A', 16)

class FormatError(KeyError):
    pass

class EvalError(Exception):
    pass

def log_quiet(msg, quiet=False):
    if not quiet:
        print(msg)

def log_yaml(i, y, quiet=False):
    pretty = {
        'default_flow_style': '\n' in y,
    }
    log_quiet(yaml.safe_dump({i:y}, **pretty), quiet)

def log_error(task_id, e):
    phrase, code, name, problem = e.args
    log_yaml('Evaluation Error', {
        'Check your {}'.format(problem): phrase,
        '{} has {}'.format(task_id, name): code,
    })

def log_warn(task, warn, quiet=False):
    task_id = uniq_id(task)
    warnings = {
        'Slyml:NO_USE': (
            'Unused id Warning',
            {
                'id {}'.format(task_id):
                'No Slurm or Needs',
            },
            quiet
        ),
        '': ('Warning', warn)
    }
    warned = warnings.get(warn)
    log_yaml(*warned)

def seems_like_path(s):
    return s[:1] in ['.', '/', '~']

def run_subprocess(command):
    return subprocess.check_output(command, stderr=subprocess.STDOUT)

def change_root(task, default):
    root = default.get('Workdir', '')
    workdir = task.get('Workdir', '')
    if workdir:
        # Allow workdir as path literal
        if os.path.isdir(workdir):
            return workdir
        # Try bash script
        try:
            return run_subprocess(workdir.split(' ')).rstrip()
        except subprocess.CalledProcessError as e:
            fmt_args = [workdir, 'Workdir', 'script syntax']
            raise EvalError(e.output.rstrip(), *fmt_args)
        except IOError as e:
            fmt_args = [workdir, 'Workdir', 'script paths']
            log_yaml('IOError', e.strerror)
        except Exception as e:
            fmt_args = [workdir, 'Workdir', 'script']
            raise EvalError(repr(e), *fmt_args)
    # Default to original
    return root

def format_path(path, root=''):
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

def join_format_overwrite(root, parent, child):
    # Copy all from parent
    result = copy.deepcopy(parent)
    # Format all strings in child
    for k,v in child.items():
        # Add value
        result[k] = v
        if isinstance(v, six.string_types):
            try:
                result[k] = v.format(**parent)
            except KeyError as e:
                fmt_args = [v, k, parent.keys()]
                raise FormatError(e.args[0], *fmt_args)
            # Unpack path if looks like a path
            if seems_like_path(result[k]):
                result[k] = format_path(result[k], root)
    #####
    # Constant values from parent
    # Values from child formatted by parent
    #####
    return result

def eval_kv(k,v):
    if isinstance(v, six.string_types):
        try:
            return eval(v)
        except SyntaxError as e:
            fmt_args = [v, k, 'syntax']
            raise EvalError(e.args[0], *fmt_args)
        except Exception as e:
            fmt_args = [v, k, 'expression']
            raise EvalError(repr(e), *fmt_args)
    return v

def eval_keys(task, evals=[]):
    for k in evals:
        v = task.get(k, 0)
        task[k] = eval_kv(k,v)
        
def is_true(key, task, default={}):
    prior = str(default.get(key, ''))
    quiet_bool = str(task.get(key, prior))
    return yaml.load(quiet_bool) in [True, 1, '1']

def is_debug(task, default={}):
    return is_true('Debug', task, default)

def is_quiet(task, default={}):
    return is_true('Quiet', task, default)

def uniq_id(task):
    task_ids = task.get('Slyml:ID', [])
    log_ids = map("{:X}".format, task_ids)
    return os.sep.join(log_ids)

def get_logs(task, ext='out'):
    # Get log or default to id string
    log_dir = task.get('Logs', 'LOGS')
    log_relative = os.path.join(log_dir, uniq_id(task))
    log_path = format_path(log_relative, task['Workdir'])
    # Make log directory
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    # Make out and err paths
    return os.path.join(log_path, 'array_%a'+'.'+ext)

def job_okay(job, debug=False):
    return debug or job.isdigit()

def get_dependency(needed, debug=False):
    deps = [x for x in needed if job_okay(x,debug)]
    if not deps:
        return ''
    # Return dependencies
    return "afterok:{}".format(':'.join(deps))

def all_flags(task):
    all_out = {}
    for k in task.get('Flags', []):
        all_out[k] = task.get(k, '')
    return all_out

def all_exports(task):
    all_out = {}
    for k in task.get('Exports', []):
        all_out[k] = task.get(k, '')
    return all_out

def get_exports(task):
    exports = all_exports(task)
    # Export all environment variables
    for k,v in exports.items():
        os.environ[k] = v
    return "ALL"

def get_array(task):
    output = {}
    default = 1
    for k in ['Runs', 'Sync']:
        v = task.get(k, default)
        try:
            val = int(v)
            output[k] = val
            default = val
        except ValueError as e:
            fmt_args = [v, k, 'integer']
            raise EvalError(e.args[0], *fmt_args)
    # Concurrent and Total Array Jobs
    sync = output['Sync']
    runs = max(0, output['Runs'] - 1)
    return "0-{}%{}".format(runs, sync)

def get_slurm(task, dependency):
    output = ['sbatch']
    try:
        arrays = get_array(task)
    except EvalError as e:
        raise
    default_list = [
        ['job-name', uniq_id(task)],
        ['output', get_logs(task, 'out')],
        ['error', get_logs(task, 'err')],
        ['dependency', dependency],
        ['workdir', task.get('Workdir','')],
        ['export', get_exports(task)],
        ['array', arrays],
    ]
    user_opt = all_flags(task)
    default_opt = dict(default_list)
    options = join_no_overwrite(user_opt, default_opt)

    def format_options(k):
        v = options.get(k,'')
        if not str(v):
            return ''
        if len(str(k)) > 1:
            return "--{}={}".format(k,v)
        return "-{} {}".format(k,v)

    flags = set(user_opt.keys())
    # Keep the main keys in order
    main_keys = zip(*default_list)[0]
    extra_keys = list(flags - set(main_keys))
    # Get user-provided options and standard options
    output += map(format_options, extra_keys)
    output += map(format_options, main_keys)
    # Return the full sbatch arguments
    output += [task.get("Slurm", '')]
    return filter(bool, output)

def job_meta(task, full_slurm=''):
    if not task.get("Slurm"):
        if task.get("Needs"):
            return map(job_meta, task["Needs"])
        # Warn user
        return {
            "Slyml:WARN": 'Slyml:NO_USE'
        }
    # Show the exports for the task
    exports = all_exports(task)
    # Return full command line arguments
    if full_slurm:
        return {
            "Slurm command": full_slurm,
            "All exports": exports,
        }
    return exports

def run_slurm(slurm_job):
    submitted = 'ERROR'
    # Submit and collect the job id
    try:
        submitted = run_subprocess(slurm_job)
    except subprocess.CalledProcessError as e:
        log_yaml('slurm error', e.output.rstrip())
    # Return the id number identifying the job
    str_out = submitted.rstrip().split(' ')
    str_digits = (s for s in str_out if s.isdigit())
    return next(str_digits, 'ERROR')

def default_joiner(_default, __default, quiet=False):
    def join_default(k, v):
        add_default = {}
        add_msg = 'Default {} added'.format(k)
        # Actually add all new defaults
        _default[k] = join_no_overwrite(v, __default[k])
        # Handle fancy update logging
        for ki,vi in v.items():
            if ki not in __default[k]:
                add_default[ki] = vi
                continue
            if _default[k] != __default[k]:
                msg = 'Default {}[{}]'.format(k, ki)
                details = {
                    'from': __default[k],
                    'to': _deafult[k],
                }
                log_yaml(msg, details, quiet)
                continue
        # Log added
        if len(add_default):
            log_yaml(add_msg, add_default, quiet)
    return join_default

def tree_box(task_id, sym='', quiet=False):
    tree_len = len(task_id.split('/'))
    tree_lines = sym[:2]*tree_len
    tree_label = task_id+sym[-1]
    tree_border = ''
    if not quiet:
        tree_label = task_id + ' {}{}'.format(tree_lines, sym[2])
        tree_border = sym[0]*(len(tree_label) - 1)
    return tree_label, tree_border

def start_tree(task_id, quiet=False):
    tree_label, tree_border = tree_box(task_id, '_ \\', quiet)
    for line in [tree_border, tree_label]:
        if line:
            print(line)

def end_tree(task_id, quiet=False):
    tree_label, tree_border = tree_box(task_id, "` /", quiet)
    for line in [tree_label, tree_border]:
        if line:
            print(line)

def run_task(__default, __task, __i=0):
    # Take defaults for task
    _default = copy.deepcopy(__default)
    _task = join_no_overwrite(__task, __default)
    # Get special values from task
    _needs = _task.get('Needs', [])
    _inputs = _task.get('Inputs', {})
    _constants = _task.get('Constants', {})
    # Define internal ID for this task
    _default['Slyml:ID'] +=  (ID_START + __i,)
    _task['Slyml:ID'] = _default['Slyml:ID']
    task_id = uniq_id(_task)
    # Try to get working directory
    try:
        _task['Workdir'] = change_root(_task, _default)
    except EvalError as e:
        log_error(task_id, e)
        end_tree(task_id)
        return ['ERROR']
    # Set Special keys from default
    _task['Debug'] = is_debug(_task, _default)
    _task['Quiet'] = is_quiet(_task, _default)
    # Unpack special variables
    root = _task['Workdir']
    debug = _task['Debug']
    quiet = _task['Quiet']
    evals = _task['Evals']
    # Cute nested task line
    start_tree(task_id, quiet)

    # Update defaults for needs
    join_default = default_joiner(_default, __default, quiet)
    join_default('Constants', _constants)
    join_default('Inputs', _inputs)

    ####
    # Constants join and format inputs,
    # Inputs join and format task
    ####
    joining = ['Constants', 'Inputs']
    try:
        inputs = join_format_overwrite(root, _constants, _inputs)
        joining = ['Inputs', task_id]
        task = join_format_overwrite(root, inputs, _task)
    except FormatError as e:
        source, target = joining
        key, fmt, name, source_keys = e.args
        log_yaml('Formatting Error', {
            '{} have'.format(source): source_keys,
            '{} needs'.format(target): key,
            name: fmt,
        })
        end_tree(task_id, quiet)
        return ['ERROR']

    try:
        # Allow math on parameters
        eval_keys(task, evals)
    except EvalError as e:
        log_error(task_id, e)
        end_tree(task_id, quiet)
        return ['ERROR']

    # Get a simple overview of the task
    overview = job_meta(task)
    if 'Slyml:WARN' in overview:
        log_warn(task, overview['Slyml:WARN'])
    # Get all needed jobs
    need_names = []
    need_jobs = []

    if _needs:
        # Recursively run all jobs needed
        for ni, n in enumerate(_needs):
            # Run task and keep job
            n_job = run_task(_default, n, ni)
            n_name = map("Job {}".format, n_job)
            need_names += n_name
            need_jobs += n_job

    # If the task has errors in needs
    if 'ERROR' in need_jobs:
        log_yaml('Not trying', overview)
        end_tree(task_id, quiet)
        return ['ERROR']
    # If task has slurm command
    if 'Slurm' in task:
        # Write the slurm command
        dependency = get_dependency(need_jobs, debug)
        try:
            slurm_job = get_slurm(task, dependency)
        except EvalError as e:
            log_error(task_id, e)
            end_tree(task_id, quiet)
            return ['ERROR']
        # Get the full overview of the job
        slurm_string = ' '.join(slurm_job)
        if debug:
            details = job_meta(task, slurm_string)
            log_yaml('Debug Details', details)
            end_tree(task_id, quiet)
            return [task_id]
        #####
        # Actually schedule the job
        ####
        job_num = run_slurm(slurm_job)
        job_name = "Job {} ({})".format(job_num, task_id)
        # Show dependencies
        if need_names:
            need_msg = '{} needs'.format(job_name)
            log_yaml(need_msg, need_names, quiet)
        # Check if job queued
        if not job_okay(job_num, debug):
            log_yaml('Error queuing', overview)
            end_tree(task_id, quiet)
            return ['ERROR']
        # Show job ID and all details
        log_yaml(job_name, overview, quiet)
        log_yaml('Queued', job_name, quiet)
        end_tree(task_id, quiet)
        return [job_num]

    end_tree(task_id, quiet)
    # Pass dependencies forward
    return need_jobs

if __name__ == "__main__":

    help = {
        'slyml': """Schedule slurm jobs from yaml.
    Dependencies: Python 2 (>=2.6) and slurm (>=14.11)
        """,
        'quiet': 'Show output only if error',
        'debug': 'Do not actually schedule jobs',
        'entry': 'Parse entry in yaml (default Main)',
        'yaml': """A path to YAML file with optional keys...
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
            - Needs:
              Constants: {...}
                  - Needs: [ ... ]
                    Constants: {...}
                    ...
              ...
            - Needs
              Constants: {...}
              ...
            - ...
        Flags: [mem, ... ]
        Exports: [x, y, ... ]
        x: "{A}/overwrites_default.py"
        y: "--new option"
        mem: 9000
        ...
     Default:
        Evals: [Runs, Sync ]
        Exports: []
        Flags: []
        Constants: {}
        Inputs: {}
        Workdir: "/root/path/to/this/YAML.yaml"
        Logs: "./LOGS"
        Slurm: ""
        Quiet: false
        Debug: false
        Runs: "{N}"
        Sync: "{N}"
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
    parsed = parser.parse_args()
    # Expand the input yaml path
    yaml_path = format_path(parsed.yaml)

    main_key = parsed.entry
    main_entry = {}
    yml_keys = []
    try:
        with open(yaml_path, 'r') as yf:
            yml = yaml.load(yf)
            yml_keys = yml.keys()
            main_entry = yml[main_key]
    except yaml.parser.ParserError as e:
        sys.exit(' STOP: Invalid YAML')
    except (AttributeError, KeyError)as e:
        log_yaml('Missing "{}" key'.format(main_key), {
            'yaml': yaml_path,
            'keys': yml_keys,
        })
    except IOError as e:
        log_yaml('IOError', e.strerror)

    # Require the Main entry
    if not main_entry:
        sys.exit(' STOP: no "{}" entry'.format(main_key))
    # Get any default values
    empty_entry = yml.get('Default', {})
    empty_entry['Slyml:ID'] = tuple()
    empty_entry['Needs'] = []

    _empty = {
        'Workdir': os.path.dirname(yaml_path),
        'Evals': ['Runs','Sync'],
        'Quiet': parsed.quiet,
        'Debug': parsed.debug,
        'Logs': './LOGS',
        'Constants': {},
        'Inputs': {},
        'Exports': [],
        'Flags': [],
        'Sync': 1,
        'Runs': 1,
    }
    default = join_no_overwrite(empty_entry, _empty)
    default_quiet = is_quiet(default)
    log_yaml('Default', default, default_quiet)

    # Begin the scheduling
    need_jobs = run_task(default, main_entry)
    # Sumarize results
    happenings = [
        ['SUCCESS', 'Scheduled'],
        ['NO BUGS', 'Parsed'],
    ]
    what_happened = happenings[is_debug(default)]
    msg = """
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
 {0}: {1} all jobs.
______________________________
        """.format(*what_happened)

    if 'ERROR' in need_jobs:
        msg = """
|||||||||||||||||||||||||||||||
 ERROR: some jobs had issues.
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
        """
    if default_quiet:
        msg = msg.split('\n')[2]
    print(msg)
