stldir=/home/john/2017/data/3dxp/stl
popdir=/home/john/2017/data/3dxp/stl/pop/$1
geodir=popdir/popGeo
filename=$1"_mesh"
stlname=$filename".stl"
x3dname=$filename".x3d"
htmlname=$filename".html"

cd $stldir
mkdir $popdir
mkdir $geodir

aopt -i $stlname -x $x3dname
aopt -i $x3dname -K $geodir/:pb -N index.html
