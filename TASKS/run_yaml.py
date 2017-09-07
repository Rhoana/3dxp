import argparse
import yaml
import os

if __name__ == "__main__":

    help = {
        'run_yaml': 'Run the main action from yaml',
        'yaml': """path to YAML file of the form
        main: 
            log_path: "/log/parent/"
            constant:
                A: "./EXAMPLE"
                ...
            input:
                B: "{A}/ANY.FILE"
                ...
            needs: 
                - needs: [ ... ]
                  python: "{A}/called.py"
                  slurm: "{A}/caller.sbatch"
                  args: "{A} -b {B}"
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

    print yaml.dump(main_entry)
