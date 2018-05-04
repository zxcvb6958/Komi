conda remove protobuf libprotobuf libtiff

cd caffe
rm -r build
mkdir build
cd build

cmake .. -DBLAS=open -DCUDNN_INCLUDE=/home/wangcheng/cuda/include -DCUDNN_LIBRARY=/home/wangcheng/cuda/lib64/libcudnn.so

make -j8
cd ../..
conda install protobuf=2 libprotobuf=2 scikit-image
