import subprocess
import argparse
import yaml
import six
import os

def log_yaml(i, y):
    print("{}:\n{}".format(i, yaml.dump(y)))

def update_dict(parent, child):
    # create new dictionary
    result = parent.copy()
    # Format all strings in child
    for k,v in child.items():
        # Add value
        result[k] = v
        if isinstance(v, six.string_types):
            result[k] = v.format(**parent)
    # Return new dictionary
    return result

def format_input(constants, inputs, tasks):
    # Update all items in input dictionary
    inputs = update_dict(constants, inputs)
    # Log the formatted input
    log_yaml('All inputs', inputs)
    # Return all needed to start
    return inputs, tasks

def get_logs(task):
    log_file = task.get('logs', './logs')
    # Make log directory if does not exist
    log_parent = os.path.dirname(log_file) or '.'
    if not os.path.exists(log_parent):
        os.makedirs(log_parent)
    return [
        "sbatch",
        "--output={}_%a.out".format(log_file),
        "--error={}_%a.err".format(log_file),
    ]

def get_depends(needed):
    if not len(needed):
        return []
    # Return dependencies
    return [
        "--dependency=afterok:{}".format(':'.join(needed)),
    ]

def get_exports(task):
    # Export all environment variables
    for k in task.get('exports', []):
        os.environ[k] = task.get(k, '')
    return [
        "--export=ALL",
    ]

def get_array(task):
    # Get slurm array parameters
    n_runs = max(0, task.get('runs', 1) - 1)
    n_sync = task.get('sync', n_runs+1)
    return [
        "--array=0-{}%{}".format(n_runs, n_sync),
        task.get("slurm", '')
    ]

def run_task(inputs, task):
    # Update all items in input dictionary
    task = update_dict(inputs, task)
    # Try to run needed jobs
    needs_tasks = task.get("needs", [])
    recursion = lambda n: run_task(inputs, n)
    needs_ids = sum(map(recursion, needs_tasks), [])
    # If task has slurm command
    if 'slurm' in task:
        # Write the slurm command
        slurm_job = get_logs(task) + get_depends(needs_ids)
        slurm_job += get_exports(task) + get_array(task)
        # Submit and collect the job id
        submitted = subprocess.check_output(slurm_job).rstrip()
        job_id = next(s for s in submitted.split(' ') if s.isdigit())
        # Slurm job dependencies
        print(' '.join(slurm_job))
        log_yaml(job_id, needs_ids)
        # Return job id
        return [job_id]
    # Log group of dependencies
    log_yaml('group', needs_ids)
    # Pass dependencies forward
    return needs_ids

if __name__ == "__main__":

    help = {
        'run_yaml': 'Run the main action from yaml',
        'yaml': """path to YAML file of the form
        main: 
            constants:
                A: "./EXAMPLE"
                ...
            inputs:
                B: "{A}/ANY.FILE"
                C: "/ANY_DIR"
                ...
            tasks: 
                - needs: [ ... ]
                  exports: [python]
                  python: "{A}/called.py"
                  slurm: "{C}/caller.sbatch"
                  logs: "{C}/called_log"
                  runs: 1
                - ...
        """,
    }
    # Most important
    main_entry = {}

    parser = argparse.ArgumentParser(description=help['run_yaml'])
    parser.add_argument('yaml', help=help['yaml'])
    parsed = parser.parse_args()
    # Expand the input yaml path
    yaml_path = os.path.realpath(os.path.expanduser(parsed.yaml))

    with open(yaml_path, 'r') as yf:
        # Get the main entrypoint from yaml
        main_entry = yaml.load(yf)['main']
    
    # Format the input
    inputs, tasks = format_input(**main_entry)
    # Send inputs and tasks to be run
    for task in tasks:
        run_task(inputs, task)
