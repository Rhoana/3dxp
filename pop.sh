stldir=/home/john/2017/data/3dxp/stl
popdir=/home/john/2017/data/3dxp/stl/pop/$1
filename=$1"_smooth1"
stlname=$filename".stl"
x3dname=$filename".x3d"

cd $stldir

mkdir $popdir
mkdir $popdir/popGeo

aopt -i $stlname -x $popdir/$x3dname

cd $popdir
aopt -i $x3dname -K popGeo/:pb -N index.html
