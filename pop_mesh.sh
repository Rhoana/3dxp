stlroot=/tmp/john/ #/home/john/2017/data/3dxp/stl
poproot=/tmp/john/pop/ #/home/john/2017/data/3dxp/stl/pop
geodir=$1"_geo"
filename=$1"_mesh"
stlname=$filename".stl"
x3dname=$filename".x3d"
htmlname=$filename".html"

mkdir $stlroot
mkdir $poproot
mkdir $poproot/$geodir
cd $stlroot

aopt -i $stlname -x $poproot/$x3dname
cd $poproot
aopt -i $x3dname -K $geodir/:pb -N $htmlname
