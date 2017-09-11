def progress(part, whole, N=100):
    """ Shows progress in loop
    Arguments
    ----------
    part: int
        Iterations done
    whole: int
        All iterations
    N: int
        Print N iterations
    """
    if part % (whole / N) == 1:
        msg = 'Loaded: {:.2f}%'
        percent = 100.0 * part / whole
        print(msg.format(percent))
