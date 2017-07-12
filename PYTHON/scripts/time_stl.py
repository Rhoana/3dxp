import json
import re

if __name__ == "__main__":

    # Number of subvolumes
    BLOCKS = 8 ** 3

    # The format of all input files
    IN_FORMAT = "/n/coxfs01/thejohnhoffer/logging/all_stl/all_{}.err"

    # The destination of the output list
    OUT_FILE = "/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-0z-3xy_mesh-8xyz/time_stl.json"
    # The output list
    OUTPUT = {
        "N": 0,
        "TOTAL": 0,
        "LIST": [],
    }
    
    # For all possible subregions
    for block in range(BLOCKS):

        with open(IN_FORMAT.format(block),'r') as bf:
            # Search the input file for the time
            bf_text = bf.read()
            bf_time = re.search(r"real\s(.*)m(.*)s", bf_text)
            # If the time is found
            if bf_time:
                # Format the times
                time = float(bf_time.group(1)) * 60.0
                time += float(bf_time.group(2))
                time = int(time)
                # Add the time to the list and total
                OUTPUT["LIST"].append(time)
                OUTPUT["TOTAL"] += time
                OUTPUT["N"] += 1

    # Save to json
    with open(OUT_FILE, 'w') as jf:
        print ("Writing {}".format(OUT_FILE))
        json.dump(OUTPUT, jf) 
