## Setting the parameters

In `tiff_lists.sbatch`
	- `TIFF_JSON` should point to a json file listing all tiffs
	- `OUTPUT_PNG` should point to the directory to save all pngs
	- `N_RES` should give the number of times to downsample by 2
	- `TOTAL_RUNS` should give the number of parallel jobs

## Running the batch job

The array should be the same length as `$TOTAL_RUNS`

```
sbatch --array=0-19 tiff_lists.sbatch
```
