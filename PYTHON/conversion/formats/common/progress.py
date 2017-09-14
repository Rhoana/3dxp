def progress(part, whole, N=100, step='Loaded'):
    """ Shows progress in loop
    Arguments
    ----------
    part: int
        Iterations done
    whole: int
        All iterations
    N: int
        Print N iterations
    step: str
        The end goal of progress
    """
    interval = max(1, whole / N)
    if part % interval == 0:
        msg = '{}: {:.2f}%'
        percent = 100.0 * part / whole
        print(msg.format(step, percent))
