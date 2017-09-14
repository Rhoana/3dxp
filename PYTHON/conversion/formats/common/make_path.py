import os
   
def make_path(out_path):
    if not os.path.exists(out_path):
        try:
            os.makedirs(out_path)
        except OSError: 
            pass      
