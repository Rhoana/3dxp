from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import numpy as np

# Set up a colormap
def color_ids(vol):
    colors = np.zeros((3,)+ vol.shape).astype(np.uint8)
    colors[0] = np.mod(107 * vol, 700).astype(np.uint8)
    colors[1] = np.mod(509 * vol, 900).astype(np.uint8)
    colors[2] = np.mod(200 * vol, 777).astype(np.uint8)
    return np.moveaxis(colors,0,-1)

def color_id(i):
    return color_ids(np.uint64([i]))[0]

def get_side(vol, key, i):
    any_side = {
        'z': lambda vol, i: vol[i,:,:],
        'y': lambda vol, i: vol[:,i,:],
        'x': lambda vol, i: vol[:,:,i]
    }
    return any_side[key](vol, i)

def make_img(args, img_out, img_vol, ids_vol=''):
    for key in args['a']:
        # Position along axis
        pos = args[key]
        # Make the new file name based on position
        file_name = '{}_in_{}.png'.format(pos, key)
        sidefile = os.path.join(img_out, file_name)
        # Yield nothing if path exists
        if os.path.exists(sidefile):
            return -1
        # Get the slice from the image volume
        image = get_side(img_vol, key, pos).astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # If the ids exist
        if len(ids_vol):
            # Get the slice from the id volume
            ids = get_side(ids_vol, key, pos)
            # Chosen id
            if args['i'] > 0:
                chosen_id = args['i']
                # Get location of chosen id
                chosen_xy = np.uint8(ids == chosen_id)
                # Dilate coordinates
                if args['g'] >0:
                    kernel = np.ones((args['g'],)*2, np.uint8)
                    chosen_xy = cv2.dilate(chosen_xy, kernel)
                # Replace image with chosen id
                image[chosen_xy > 0] = color_id(chosen_id) 
            # Get ids of black background
            black_xy = ids == 0
            # Convert the ids to color
            ids = color_ids(ids)
            # Replace black ids with raw image
            ids[black_xy] = image[black_xy]
            # Combine the image with the ids
            alpha, beta = args['o'], 1.0-args['o']
            image = image*beta + ids*alpha
        # Write the image to a file
        cv2.imwrite(sidefile, image)
        print 'wrote', sidefile

def load_files(args, img_out, img_in, ids_in):
    # Do nothing if no images
    if not os.path.exists(img_in):
        return -1
    # Load the image volume
    with h5py.File(img_in, 'r') as img_f:
        img_vol = img_f[img_f.keys()[0]]
        # Only images if no segmentation
        if not os.path.exists(ids_in):
            return make_img(args, img_out, img_vol)
        # Load the segmentation volume
        with h5py.File(ids_in, 'r') as ids_f:
            ids_vol = ids_f[ids_f.keys()[0]]
            return make_img(args, img_out, img_vol, ids_vol)

def start(_argv):
    args = parseArgv(_argv)

    IMG_IN = args['raw']
    IDS_IN = args['ids']
    IMG_OUT = args['out']

    if not os.path.exists(IMG_OUT):
        os.makedirs(IMG_OUT)

    # Generate side images
    load_files(args, IMG_OUT, IMG_IN, IDS_IN) 

def parseArgv(argv):
    sys.argv = argv

    help = {
       'help': 'Find the sides of an image volume',
       'out': 'output image directory (default .)',
       'raw': 'input raw h5 volume (default raw.h5)',
       'ids': 'input h5 segmentation volume (default id.h5)',
       'x': 'The position of the x slice (default 0)',
       'y': 'The position of the y slice (default 0)',
       'z': 'The position of the z slice (default 0)',
       'o': 'The opacity of the segmentation (default 0.5)',
       'i': 'The ID to highlight (default None)',
       'a': 'All slices to generate (default xyz)',
       'g': 'Amount to grow highlight (default 0',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='.', help=help['out'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('ids', default='ids.h5', help=help['ids'])
    parser.add_argument('-y', type=int, default=0, help=help['y'])
    parser.add_argument('-x', type=int, default=0, help=help['x'])
    parser.add_argument('-z', type=int, default=0, help=help['z'])
    parser.add_argument('-o', type=float, default=0.5, help=help['o'])
    parser.add_argument('-i', type=int, default=0, help=help['i'])
    parser.add_argument('-g', type=int, default=0, help=help['g'])
    parser.add_argument('-a', default='xyz', help=help['a'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

