conda remove protobuf libprotobuf libtiff

cd caffe
rm -r build
mkdir build
cd build

cmake .. -DBLAS=open -DCPU_ONLY=ON

make -j8
cd ../..
conda install protobuf=2 libprotobuf=2 scikit-image
