## SlyML
__Version 2.2.2__

Here is a python script to run and monitor [Slurm](https://slurm.schedmd.com/) jobs from yaml config files.

### 0.0) Get ready:

```
git clone https://github.com/Rhoana/3dxp.git
cd 3dxp/TASKS
```

0.5) Only if using 3DXP:

_(On the Harvard Odyssey Cluster)[†](#custom-setup)_

```
. harvard/environment.sh
```

_(Elsewhere...)_

```
pip install -r ../PYTHON/requirements.txt
```

### 1.0) Get started:

```
python slyml.py my_config.yaml
```

#### Wait, but first, write a config

Run marching cubes over [many jobs](demos/many.yaml) on a hdf5 volume handled in parallel in blocks.
```
cp demos/many.yaml my_config.yaml
```

In `Default.Constants`,

- Set `OUTPUT` to wherever you want your meshes.
- Set `HD_IDS` to the path to your input HDF5 file.
- Set `TODAY` to the current date (for logging).
- `BLOCK_COUNT: 4` breaks meshes into 64 blocks.
	- Each block is ¼×¼×¼ of the volume.

In `Main.Inputs`,

- Set `LIST_IDS` to select segments for stl generation.

### Example my_config.yaml

```yaml
Main:
    python: ./PYTHON/all_stl.py
    args: "-b {BLOCK_COUNT} -l {LIST_IDS} {HD_IDS} {MESH_IDS}"
    Inputs:
        MESH_IDS: "{OUTPUT}/{TODAY}/many"
        LIST_IDS: "1:200:300"
Default:
    Constants:
        TODAY: "2017-11-11"
        HD_IDS: ~/data/ids.h5
        OUTPUT: ~/data
        BLOCK_COUNT: 4
    Workdir: "git rev-parse --show-toplevel"
    Slurm: ./SLURM/many.sbatch
    Exports: [python, args]
    Logs: "./LOGS/{TODAY}"
    Runs: "{BLOCK_COUNT}**3"
```

Running `python slyml.py my_config.yaml` acts like this:

```bash
TODAY="2017-11-11"
HD_IDS=~/data/ids.h5
OUTPUT=~/data
BLOCK_COUNT=4

Workdir=`git rev-parse --show-toplevel`
Slurm=$Workdir/SLURM/many.sbatch
Logs=$Workdir/LOGS/$TODAY
Runs=$((BLOCK_COUNT**3))

MESH_IDS=$OUTPUT/$TODAY/many
LIST_IDS="1:200:300"

export python="$Workdir/PYTHON/all_stl.py"
export args="-b $BLOCK_COUNT -l $LIST_IDS $HD_IDS $MESH_IDS"
sbatch --job-name=A --output=$Logs/A/array_%a.out --error=~$Logs/A/array_%a.err --workdir=$Workdir --export=ALL --array=0-$((Runs-1)) $Slurm
```

### But this is so much more

This particular demo runs [a python script](/PYTHON/all_stl.py) from [a very general sbatch file](/SLURM/many.sbatch). The YAML file sent to `slyml.py` can parallelize any command by exporting environment variables to any `sbatch` file. The general format of `my_config.yaml` is given by `python slyml.py -h`!

#### Extensibility

- If your data does not need to be parallelized, you can omit `Runs` to schedule [one job](demos/one.yaml)
	- Set `BLOCK_COUNT` to 1 to handle the whole volume.
- We can write the examples for [one job](demos/one.yaml) and [many jobs](demos/many.yaml) with fewer lines in a [combined file](demos/list.yaml).
	- The `slyml.py` script will use any entry (like `Main`) if passed as the second argument.
 		- So `python slymyl.py /demos/list.yaml` schedules [many jobs](demos/list.yaml#L8) (from the `Main` entry).
 		- And `python slymyl.py /demos/list.yaml one` schedules [one job](demos/list.yaml) (with different `Inputs`).
	- With the power to anchor `&`, refer `*`, and extend `<<:` objects and lists, YAML allows the quick [recombination](http://blog.daemonl.com/2016/02/yaml.html) of tasks and parameters.
- `Main` can have `Needs` that must be completed before `Main` can start.
	- The `Needs` can have `Needs`, recursively indefinitely.
	- The `Needs` inherit `Constants` and `Inputs` as `Default` values.
	- Other keywords like `Slum`, `Workdir`, or user-defined keys are not inherited.
- The `slyml.py` script takes optional keywords that can be set and unset directly in the yaml file.
	- `python slyml.py -q` or `Default.Quiet` (only log errors or warnings).
	- `python slyml.py -d` or `Default.Debug` (only log, without scheduling jobs).
- Any key understands absolute paths (`/`), or paths relative to the `Workdir` (`.`) or home directory (`~`).
	- The `Workdir` can be an existing directory or a valid shell command. No other keyword works like this.
- The `Exports` key lists all keys to export to the `Slurm` file.
- The `Flags` key lists all keys to use as flags to `sbatch`.
- The `Evals` key lists all keys to evaluate as `python`.
	- By default, this is `[Runs, Sync]`.

#### Limitations

- The `Constants` and `Inputs` can format any value except `Workdir`, `Exports`, `Evals`, or `Flags`.
	- But only the `Constants` can format the values for the `Inputs`.
	- The `Constants` cannot be formatted and must be literal.
- To run jobs, set `Slurm` to the path of a valid `sbatch` file.
	- Based on `Runs`, the `sbatch` file can use `$SLURM_ARRAY_TASK_ID` and `SLURM_ARRAY_TASK_COUNT`
- Internally, `slymyl.py` sets `sbatch` arguments `job-name`, `workdir`, `array`, `dependency`, `output`, `error`, and `export`.
	- The `Flags` key selects any other `sbatch` flags from the keys of each task.
- Only Unix-like relative paths are expanded to absolute paths


#### Custom setup
Running `slyml.py` requires only [a simple setup](harvard/minimal.sh) on the harvard cluster, but in this example we also [set up a virtual environment](harvard/environment.sh) with the libraries needed to run the python used in 3DXP.
