import numpy as np

def trial2span(trial, runs, z_start, z_stop):
    """
    Arguments
    ----------
    trial: 
        The trial in [0..runs)
    runs: int
        The number of parallel jobs
    z_start: int
        The first slice
    z_stop: int
        One above the last slice

    Returns
    --------
    np.ndarray
        [The first z slice, the upper limit]
    """
    # Make a linear space for all the runs
    all_runs = np.linspace(z_start, z_stop, runs + 1)
    # Return the current run
    this_run = all_runs[trial:][:2]
    return np.uint64(this_run)
