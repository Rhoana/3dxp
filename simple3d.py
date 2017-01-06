from threed import ThreeD

DATA = '/home/harvard/2017/data/bf/jan_push/8x_downsampled_segmentation.h5'
ROOTDIR = '/home/harvard/2017/data/3dxp/jan_push/'
STLFOLDER = ROOTDIR + 'stl'
X3DFOLDER = ROOTDIR + 'x3d'


ThreeD.run(DATA, 0, 0, STLFOLDER, tilewidth=200)
ThreeD.run(DATA, 0, 1, STLFOLDER, tilewidth=200)
ThreeD.run(DATA, 1, 0, STLFOLDER, tilewidth=200)
ThreeD.create_website(STLFOLDER, X3DFOLDER, None)

